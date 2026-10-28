"""Build the category catalogue and embedded aliases from CSV sources."""

import csv
import html
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ['category_id', 'group_id', 'group_name', 'category_name', 'kind', 'status', 'description']
RETIRED_HEADERS = ['category_id', 'replaced_by']
ALIAS_HEADERS = ['alias', 'category_id', 'note']


def normalise(value):
    text = unicodedata.normalize('NFKC', html.unescape(value)).casefold().replace('&', ' and ')
    return ' '.join(re.sub(r'[_\W]+', ' ', text).split())


def read_csv(path, headers):
    with path.open(encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != headers:
            raise ValueError(f'Unexpected CSV headers: {path.name}')
        rows = list(reader)
    if not rows:
        raise ValueError(f'Empty CSV: {path.name}')
    for number, row in enumerate(rows, 2):
        if None in row or any(value is None or value != value.strip() for value in row.values()):
            raise ValueError(f'Invalid CSV row {number}: {path.name}')
    return rows


def category_rows(root=ROOT):
    rows = read_csv(root / 'taxonomy/categories.csv', HEADERS)
    ids, names, groups, group_ids = set(), set(), {}, {}
    for row in rows:
        cid, gid = row['category_id'], row['group_id']
        if not re.fullmatch(r'c[0-9]{4}', cid) or not re.fullmatch(r'g[0-9]{3}', gid) or cid in ids:
            raise ValueError(f'Invalid or duplicate ID: {cid}')
        if not all(row[key] for key in ['category_name', 'group_name', 'description']):
            raise ValueError(f'Missing category label or definition: {cid}')
        if row['status'] not in {'active', 'proposed'}:
            raise ValueError(f'Invalid status: {cid}')
        if row['kind'] not in {'activity', 'characteristic'}:
            raise ValueError(f'Invalid category kind: {cid}')
        if (row['kind'] == 'characteristic') != (gid == 'g023'):
            raise ValueError(f'Characteristics must use the Business Characteristics group: {cid}')
        if gid == 'g023' and row['group_name'] != 'Business Characteristics':
            raise ValueError('Invalid Business Characteristics group label')
        name = normalise(row['category_name'])
        if name in names:
            raise ValueError(f'Duplicate selectable category label: {row["category_name"]}')
        if groups.setdefault(gid, row['group_name']) != row['group_name']:
            raise ValueError(f'Conflicting group names: {gid}')
        if group_ids.setdefault(normalise(row['group_name']), gid) != gid:
            raise ValueError('Duplicate group name with different IDs')
        ids.add(cid)
        names.add(name)
    return rows


def retired_ids(root, selectable_ids):
    rows = read_csv(root / 'taxonomy/retired.csv', RETIRED_HEADERS)
    ids = set()
    for row in rows:
        cid, replacement = row['category_id'], row['replaced_by']
        if not re.fullmatch(r'c[0-9]{4}', cid) or cid in ids or cid in selectable_ids:
            raise ValueError(f'Retired ID is invalid, duplicated or reused: {cid}')
        if replacement and replacement not in selectable_ids:
            raise ValueError(f'Retired replacement must identify a selectable category: {cid}')
        ids.add(cid)
    return ids


def read_aliases(root, ids):
    aliases, seen = {cid: [] for cid in ids}, set()
    for row in read_csv(root / 'taxonomy/aliases.csv', ALIAS_HEADERS):
        term, cid = normalise(row['alias']), row['category_id']
        if not term or cid not in ids or not row['note']:
            raise ValueError(f'Invalid alias or category reference: {row["alias"]}')
        key = term, cid
        if key in seen:
            raise ValueError(f'Duplicate normalised alias/category pair: {row["alias"]}')
        seen.add(key)
        aliases[cid].append({'alias': row['alias'], 'note': row['note']})
    return aliases


def build(root=ROOT):
    metadata = json.loads((root / 'taxonomy/version.json').read_text(encoding='utf-8'))
    groups = {}
    for row in category_rows(root):
        group = groups.setdefault(row['group_id'], {'id': row['group_id'], 'name': row['group_name'], 'categories': []})
        group['categories'].append({
            'id': row['category_id'], 'name': row['category_name'],
            'kind': row['kind'], 'status': row['status'], 'description': row['description'],
        })
    categories = {c['id']: c for g in groups.values() for c in g['categories']}
    known_ids = set(categories) | retired_ids(root, categories)
    aliases = read_aliases(root, categories)
    for cid, category in categories.items():
        category['aliases'] = aliases[cid]
        if any(ref not in known_ids for ref in re.findall(r'\bc\d{4}\b', category['description'])):
            raise ValueError(f'Unknown definition reference: {cid}')
    return {
        'catalogueId': metadata['catalogue_id'], 'version': metadata['catalogue_version'],
        'status': metadata['status'], 'license': 'Apache-2.0', 'groups': list(groups.values()),
    }
