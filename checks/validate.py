"""CLI for Curator's three objective documentation categories."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# With -I, add only this trusted source directory, never the content root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from documents import check_links, check_status, snapshot
from provenance import inspect_provenance

CATEGORIES = ('internal-references', 'evidence-provenance', 'document-status')


def validate(root: Path, category: str) -> list[dict]:
    if category not in CATEGORIES:
        raise ValueError('Unknown category: ' + category)
    files, unsafe = snapshot(Path(root))
    provenance, references, originals = inspect_provenance(files)
    if category == 'evidence-provenance':
        return provenance
    if category == 'internal-references':
        return check_links(files, unsafe, references, originals)
    return check_status(files, originals)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--category', choices=CATEGORIES, required=True)
    parser.add_argument('--format', choices=('text', 'json'), default='text')
    args = parser.parse_args(argv)
    try:
        errors = validate(args.root, args.category)
    except (OSError, UnicodeError, ValueError) as error:
        if args.format == 'json':
            print(json.dumps({'category': args.category, 'error': str(error), 'diagnostics': []}))
        else:
            print(f'{args.category}: unable to complete: {error}', file=sys.stderr)
        return 2
    if args.format == 'json':
        print(json.dumps({'category': args.category, 'diagnostics': errors}, ensure_ascii=False))
    else:
        for error in errors:
            print(f"{error['path']}:{error['line'] or '-'}: {error['message']}")
        print(f'{args.category}: {len(errors)} violation(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
