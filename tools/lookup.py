"""Search categories or validate separate activity and characteristic selections."""

import argparse
import json
from pathlib import Path
from catalogue_data import normalise

ROOT = Path(__file__).resolve().parents[1]


def load_catalogue(root=ROOT):
    data = json.loads((root / 'taxonomy/categories.json').read_text(encoding='utf-8'))
    index = {c['id']: {**c, 'group': g['name']} for g in data['groups'] for c in g['categories']}
    for category in index.values():
        if category.get('kind') not in {'activity', 'characteristic'}:
            raise ValueError('Each category requires an activity or characteristic kind')
        if not isinstance(category.get('aliases'), list):
            raise ValueError('Category aliases must be an array; regenerate the catalogue JSON')
        seen = set()
        for alias in category['aliases']:
            if (not isinstance(alias, dict) or not isinstance(alias.get('alias'), str)
                    or not isinstance(alias.get('note'), str) or not alias['note'].strip()):
                raise ValueError('Each embedded alias requires an alias string and contextual note')
            term = normalise(alias['alias'])
            if not term or term in seen:
                raise ValueError('Empty or duplicate normalised alias within a category')
            seen.add(term)
    return data, index


def validate_selection(activities, characteristics=(), root=ROOT):
    """Validate classification only; receiver-specific compatibility is separate."""
    if (isinstance(activities, str) or isinstance(characteristics, str)
            or not isinstance(activities, (list, tuple)) or not isinstance(characteristics, (list, tuple))):
        raise ValueError('Supply activity and characteristic IDs as separate lists')
    data, index = load_catalogue(root)
    issues, seen = [], set()
    if not 1 <= len(activities) <= 3:
        issues.append('Select 1 to 3 business activities.')
    if len(characteristics) > 3:
        issues.append('Select 0 to 3 optional Business Characteristics.')
    for kind, ids in [('activity', activities), ('characteristic', characteristics)]:
        for cid in ids:
            if not isinstance(cid, str):
                issues.append('Category IDs must be strings.')
                continue
            if cid in seen:
                issues.append(f'Duplicate ID: {cid}')
            seen.add(cid)
            if cid not in index:
                issues.append(f'Unknown or retired ID: {cid}')
            elif index[cid]['kind'] != kind:
                issues.append(f'{cid} has kind {index[cid]["kind"]}; expected {kind}.')
    return {
        'catalogueId': data['catalogueId'], 'version': data['version'],
        'valid': not issues, 'activities': list(activities),
        'characteristics': list(characteristics), 'issues': issues,
    }


def words_match(needle, text):
    words = normalise(text).split()
    return all(any(word == part if len(part) <= 2 else word.startswith(part) for word in words) for part in needle.split())


def search(text, root=ROOT):
    if not isinstance(text, str) or not normalise(text):
        raise ValueError('Supply a non-empty search term')
    _, index = load_catalogue(root)
    needle = normalise(text)
    results = []
    for cid, category in index.items():
        name = normalise(category['name'])
        matched = [a for a in category['aliases'] if words_match(needle, a['alias'])]
        if needle == normalise(cid):
            rank = 0
        elif needle == name:
            rank = 1
        elif any(needle == normalise(a['alias']) for a in matched):
            rank = 2
        elif words_match(needle, category['name']):
            rank = 3
        elif matched:
            rank = 4
        elif words_match(needle, category['description']):
            rank = 5
        elif words_match(needle, category['group']):
            rank = 6
        else:
            continue
        results.append((rank, name, cid, {**category, 'matchedAliases': matched}))
    if results:
        best = min(row[0] for row in results)
        cutoff = 0 if best == 0 else 2 if best <= 2 else 4 if best <= 4 else 6
        results = [row for row in results if row[0] <= cutoff]
        if cutoff <= 2:
            for row in results:
                row[3]['matchedAliases'] = [a for a in row[3]['matchedAliases'] if normalise(a['alias']) == needle]
    return [row[3] for row in sorted(results, key=lambda row: row[:3])]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search', metavar='TEXT', help='Find category candidates by name, ID or alias')
    parser.add_argument('--activities', nargs='+', metavar='ID', default=[], help='Select 1 to 3 activity IDs')
    parser.add_argument('--characteristics', nargs='+', metavar='ID', default=[], help='Optionally select up to 3 characteristic IDs')
    args = parser.parse_args()
    if args.search is not None and (args.activities or args.characteristics):
        parser.error('Use either --search or selection IDs')
    if args.search is None and not (args.activities or args.characteristics):
        parser.error('Use --search or --activities')
    try:
        result = search(args.search) if args.search is not None else validate_selection(args.activities, args.characteristics)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.search is None and not result['valid']:
        parser.exit(1)


if __name__ == '__main__':
    main()
