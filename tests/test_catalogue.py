import csv
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalogue
import catalogue_data
import lookup


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        shutil.copytree(ROOT / 'taxonomy', root / 'taxonomy')
        yield root


def change_csv(root, path, change):
    with (root / path).open(encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle)
        headers, rows = reader.fieldnames, list(reader)
    change(rows)
    with (root / path).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


class CatalogueTests(unittest.TestCase):
    def test_generated_json_matches_csv_sources(self):
        self.assertEqual((ROOT / 'taxonomy/categories.json').read_text(encoding='utf-8'),
                         catalogue.serialise(catalogue_data.build()))

    def test_catalogue_identity_counts_and_statuses(self):
        data = catalogue_data.build()
        categories = [c for g in data['groups'] for c in g['categories']]
        self.assertEqual(data['catalogueId'], 'urn:uuid:1747a70b-79ad-4fb1-92e0-ed19b20ce53d')
        self.assertEqual(data['status'], 'draft')
        self.assertEqual(data['license'], 'Apache-2.0')
        self.assertEqual(len(data['groups']), 20)
        self.assertEqual(sum(c['kind'] == 'activity' for c in categories), 196)
        self.assertEqual(sum(c['kind'] == 'characteristic' for c in categories), 9)
        self.assertEqual(sum(c['status'] == 'active' for c in categories), 131)
        self.assertEqual(sum(c['status'] == 'proposed' for c in categories), 74)
        self.assertEqual(len(categories), len({c['id'] for c in categories}))
        self.assertLess(len(categories), 250)

    def test_nine_optional_characteristics(self):
        group = next(g for g in catalogue_data.build()['groups'] if g['id'] == 'g023')
        self.assertEqual({c['name'] for c in group['categories']}, {
            'Franchise', 'Home Based', 'Online Operation', 'Mobile Operation', 'Relocatable',
            'Business with Property', 'Owner Operated', 'Under Management', 'Premises Based'})
        self.assertTrue(all(c['kind'] == 'characteristic' for c in group['categories']))

    def test_retired_ids_cannot_be_reused(self):
        data = catalogue_data.build()
        active = {c['id'] for g in data['groups'] for c in g['categories']}
        retired = catalogue_data.retired_ids(ROOT, active)
        self.assertEqual(len(retired), 63)
        self.assertEqual(active | retired, {f'c{i:04}' for i in range(1, 269)})
        self.assertFalse(active & retired)
        with fixture() as root:
            change_csv(root, 'taxonomy/categories.csv', lambda r: r[0].update(category_id='c0101'))
            with self.assertRaises(ValueError):
                catalogue_data.build(root)

    def test_invalid_category_data_is_rejected(self):
        invalid = [
            lambda r: r[1].update(category_id=r[0]['category_id']),
            lambda r: r[1].update(category_name=r[0]['category_name'].upper()),
            lambda r: r[-1].update(category_name=r[0]['category_name']),
            lambda r: r[1].update(group_name='Conflicting name'),
            lambda r: r[0].update(description=''),
            lambda r: r[0].update(status='approved'),
            lambda r: r[0].update(kind='industry'),
            lambda r: r[0].update(kind='characteristic'),
            lambda r: r[-1].update(kind='activity'),
            lambda r: r[-1].update(group_name='Franchise'),
            lambda r: r[0].update(description='Unknown category c9999.'),
        ]
        for change in invalid:
            with self.subTest(change=change), fixture() as root:
                change_csv(root, 'taxonomy/categories.csv', change)
                with self.assertRaises(ValueError):
                    catalogue_data.build(root)

    def test_invalid_retirement_ledger_is_rejected(self):
        for change in [lambda r:r.append(dict(r[0])),
                       lambda r:r[0].update(category_id='c0053'),
                       lambda r:r[0].update(replaced_by='c9999')]:
            with self.subTest(change=change), fixture() as root:
                change_csv(root, 'taxonomy/retired.csv', change)
                with self.assertRaises(ValueError):
                    catalogue_data.build(root)

    def test_invalid_alias_source_is_rejected(self):
        for change in [lambda r:r[0].update(category_id='c9999'),
                       lambda r:r[0].update(category_id='c0101'),
                       lambda r:r[0].update(alias='***'),
                       lambda r:r[0].update(note=''),
                       lambda r:r.append({**r[0], 'alias':r[0]['alias'].upper()})]:
            with self.subTest(change=change), fixture() as root:
                change_csv(root, 'taxonomy/aliases.csv', change)
                with self.assertRaises(ValueError):
                    catalogue_data.build(root)

    def test_every_alias_term_note_and_parent_is_preserved(self):
        data = catalogue_data.build()
        categories = {c['id']:c for g in data['groups'] for c in g['categories']}
        expected = {cid:[] for cid in categories}
        for row in catalogue_data.read_csv(ROOT / 'taxonomy/aliases.csv', catalogue_data.ALIAS_HEADERS):
            expected[row['category_id']].append({'alias':row['alias'], 'note':row['note']})
        self.assertEqual(sum(len(v) for v in expected.values()), 162)
        self.assertTrue(all(c['aliases'] == expected[cid] for cid,c in categories.items()))
        self.assertTrue(any(c['aliases'] == [] for c in categories.values()))
        self.assertEqual(len(categories['c0064']['aliases']), 7)

    def test_bad_csv_shape_headers_and_whitespace_are_rejected(self):
        for text in ['wrong,header\na,b\n', ','.join(catalogue_data.ALIAS_HEADERS)+'\na,b\n',
                     ','.join(catalogue_data.ALIAS_HEADERS)+'\n term,c0053,note\n']:
            with self.subTest(text=text), fixture() as root:
                (root / 'taxonomy/aliases.csv').write_text(text,encoding='utf-8')
                with self.assertRaises(ValueError):
                    catalogue_data.build(root)

    def test_generator_cli_can_check_and_report_stale_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / 'tools', root / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(ROOT / 'taxonomy', root / 'taxonomy')
            command = [sys.executable, str(root / 'tools/catalogue.py')]
            self.assertEqual(subprocess.run(command+['--check'],capture_output=True).returncode, 0)
            (root / 'taxonomy/categories.json').write_text('{}',encoding='utf-8')
            self.assertEqual(subprocess.run(command+['--check'],capture_output=True).returncode, 1)
            self.assertEqual(subprocess.run(command,capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(command+['--check'],capture_output=True).returncode, 0)


class SelectionTests(unittest.TestCase):
    def test_valid_independent_limits(self):
        cases = [
            (['c0053'], []),
            (['c0053','c0051','c0247'], []),
            (['c0053'], ['c0260','c0266','c0267']),
            (['c0053','c0051','c0247'], ['c0260','c0266','c0267']),
            (['c0053','c0051'], ['c0260','c0267']),
        ]
        for activities,characteristics in cases:
            with self.subTest(activities=activities,characteristics=characteristics):
                result = lookup.validate_selection(activities,characteristics)
                self.assertTrue(result['valid'],result['issues'])
                self.assertEqual(result['activities'],activities)
                self.assertEqual(result['characteristics'],characteristics)
                self.assertEqual(result['issues'],[])

    def test_invalid_independent_limits(self):
        for activities,characteristics in [
            ([],[]), ([],['c0260']),
            (['c0053','c0051','c0247','c0061'],[]),
            (['c0053'],['c0260','c0261','c0262','c0263']),
        ]:
            with self.subTest(activities=activities,characteristics=characteristics):
                result = lookup.validate_selection(activities,characteristics)
                self.assertFalse(result['valid'])
                self.assertTrue(result['issues'])
                self.assertEqual(result['activities'],activities)
                self.assertEqual(result['characteristics'],characteristics)

    def test_duplicates_unknown_and_retired_ids_are_invalid(self):
        for activities,characteristics in [
            (['c0053','c0053'],[]),
            (['c0053'],['c0260','c0260']),
            (['c0053'],['c0053']),
            (['c9999'],[]),
            (['c0101'],[]),
            (['c0053'],['c9999']),
            (['c0053'],['c0112']),
        ]:
            with self.subTest(activities=activities,characteristics=characteristics):
                self.assertFalse(lookup.validate_selection(activities,characteristics)['valid'])

    def test_wrong_kinds_are_invalid_in_both_directions(self):
        for activities,characteristics in [(['c0260'],[]), (['c0053'],['c0051'])]:
            with self.subTest(activities=activities,characteristics=characteristics):
                result = lookup.validate_selection(activities,characteristics)
                self.assertFalse(result['valid'])
                self.assertTrue(any('expected' in issue for issue in result['issues']))

    def test_characteristics_never_supply_an_inferred_activity(self):
        result = lookup.validate_selection([],['c0260','c0262','c0268'])
        self.assertFalse(result['valid'])
        self.assertEqual(result['activities'],[])

    def test_omitted_characteristics_are_valid(self):
        result = lookup.validate_selection(['c0053'])
        self.assertTrue(result['valid'])
        self.assertEqual(result['characteristics'],[])

    def test_validation_is_not_receiver_compatibility(self):
        result = lookup.validate_selection(['c0202'],['c0267'])
        self.assertTrue(result['valid'])
        self.assertEqual(set(result), {'catalogueId','version','valid','activities','characteristics','issues'})

    def test_non_list_input_and_non_string_ids(self):
        with self.assertRaises(ValueError):
            lookup.validate_selection('c0053')
        self.assertFalse(lookup.validate_selection([123])['valid'])

    def test_cli_valid_invalid_and_usage_statuses(self):
        command = [sys.executable,str(ROOT / 'tools/lookup.py')]
        valid = subprocess.run(command+['--activities','c0053','c0051','--characteristics','c0260','c0267'],
                               capture_output=True,text=True)
        self.assertEqual(valid.returncode,0)
        self.assertTrue(json.loads(valid.stdout)['valid'])
        for args in [['--characteristics','c0260'], ['--activities','c9999'],
                     ['--activities','c0260'], ['--activities','c0053','--characteristics','c0051']]:
            with self.subTest(args=args):
                invalid = subprocess.run(command+args,capture_output=True,text=True)
                self.assertEqual(invalid.returncode,1)
                self.assertFalse(json.loads(invalid.stdout)['valid'])
        for args in [[], ['--search','pizza','--activities','c0053']]:
            with self.subTest(args=args):
                self.assertEqual(subprocess.run(command+args,capture_output=True).returncode,2)


class SearchTests(unittest.TestCase):
    def ids(self,term):
        return {c['id'] for c in lookup.search(term)}

    def test_exact_online_alias_does_not_suggest_premises(self):
        self.assertEqual(self.ids('online business'), {'c0262'})
        self.assertEqual([a['alias'] for a in lookup.search('online business')[0]['matchedAliases']], ['online business'])
        self.assertEqual(self.ids('online business with premises'), {'c0262','c0268'})
        self.assertEqual(self.ids('Online Operation'), {'c0262'})
        self.assertEqual(self.ids('online shop'), {'c0218'})

    def test_legitimate_ambiguous_aliases_keep_all_exact_options(self):
        cases = [('pizza shop', {'c0061','c0064'}), ('pizzeria',{'c0061','c0064'}),
                 ('tyre sales and fitting', {'c0014','c0024'}),
                 ('beauty product supply', {'c0129','c0256'}),
                 ('luggage sales and repairs', {'c0125','c0178'})]
        for term,expected in cases:
            with self.subTest(term=term):
                matches = lookup.search(term)
                self.assertEqual({c['id'] for c in matches}, expected)
                self.assertTrue(all(c['matchedAliases'] and c['matchedAliases'][0]['note'] for c in matches))

    def test_partial_aliases_cannot_override_an_exact_name(self):
        with fixture() as root:
            path = root / 'taxonomy/categories.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            next(c for g in data['groups'] for c in g['categories'] if c['id']=='c0051')['aliases'].append(
                {'alias':'Takeaway Food equipment', 'note':'Partial phrase only.'})
            path.write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual({c['id'] for c in lookup.search('Takeaway Food',root)}, {'c0064'})

    def test_exact_id_only_returns_that_record(self):
        self.assertEqual(self.ids('c0064'), {'c0064'})

    def test_normalisation_and_short_tokens(self):
        for term in ['fish & chips','FISH-AND-CHIPS',' fish &amp; chips ']:
            self.assertEqual(self.ids(term), {'c0064'})
        self.assertEqual(self.ids('ＴＡＴＴＳ'), {'c0131'})
        self.assertEqual(self.ids('Coin-Laundry'), {'c0245'})
        self.assertEqual(self.ids('AI'), {'c0197'})
        self.assertNotIn('c0014',self.ids('arts'))
        self.assertNotIn('c0028',self.ids('arts'))

    def test_all_source_aliases_find_their_parent_and_note(self):
        for row in catalogue_data.read_csv(ROOT/'taxonomy/aliases.csv',catalogue_data.ALIAS_HEADERS):
            with self.subTest(alias=row['alias'],category=row['category_id']):
                result = next(c for c in lookup.search(row['alias']) if c['id']==row['category_id'])
                self.assertIn({'alias':row['alias'],'note':row['note']},result['matchedAliases'])

    def test_description_fallback_and_no_match(self):
        self.assertIn('c0025',self.ids('refinishing'))
        self.assertIn('c0207',self.ids('solar'))
        self.assertEqual(lookup.search('no matching category 12345'),[])
        with self.assertRaises(ValueError):
            lookup.search('***')

    def test_single_json_is_sufficient_for_search_and_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'taxonomy').mkdir()
            shutil.copy2(ROOT/'taxonomy/categories.json',root/'taxonomy/categories.json')
            self.assertEqual({c['id'] for c in lookup.search('pizza shop',root)}, {'c0061','c0064'})
            self.assertTrue(lookup.validate_selection(['c0053'],['c0260'],root)['valid'])

    def test_malformed_embedded_aliases_and_kinds_are_rejected(self):
        for aliases in [None,'term',[None],[{'alias':'term'}],[{'alias':12,'note':'Context'}],
                        [{'alias':'***','note':'Context'}],[{'alias':'term','note':''}],
                        [{'alias':'term','note':'Context'},{'alias':'TERM','note':'Duplicate'}]]:
            with self.subTest(aliases=aliases),fixture() as root:
                path = root/'taxonomy/categories.json'
                data = json.loads(path.read_text(encoding='utf-8'))
                data['groups'][0]['categories'][0]['aliases'] = aliases
                path.write_text(json.dumps(data),encoding='utf-8')
                with self.assertRaises(ValueError):
                    lookup.search('term',root)
        with fixture() as root:
            path = root/'taxonomy/categories.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            data['groups'][0]['categories'][0]['kind'] = 'industry'
            path.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaises(ValueError):
                lookup.search('term',root)

    def test_search_cli_offers_choices_without_selection(self):
        result = subprocess.run([sys.executable,str(ROOT/'tools/lookup.py'),'--search','pizza shop'],
                                capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertEqual({c['id'] for c in json.loads(result.stdout)}, {'c0061','c0064'})


if __name__ == '__main__':
    unittest.main()
