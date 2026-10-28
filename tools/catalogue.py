"""Generate or check the category JSON, including embedded search aliases."""

import argparse
import json
from catalogue_data import ROOT, build


def serialise(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check generated JSON without writing files')
    args = parser.parse_args()
    try:
        text = serialise(build())
        path = ROOT / 'taxonomy/categories.json'
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != text:
                parser.exit(1, 'Category JSON is stale. Run python tools/catalogue.py\n')
            print('Category JSON matches the CSV sources.')
        else:
            path.write_text(text, encoding='utf-8', newline='\n')
            print('Wrote category JSON with embedded aliases.')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
