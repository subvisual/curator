"""Small, deterministic evidence-sidecar contract."""
from __future__ import annotations

import json
import posixpath
import re
from datetime import date
from urllib.parse import urlsplit

from documents import diagnostic, local_target

TYPES = {'document', 'meeting-notes', 'transcript', 'firsthand-account', 'verification', 'extraction'}
ROLES = {'original', 'notes', 'transcript', 'extract', 'translation', 'rendering'}


def inspect_provenance(files):
    errors, references, originals, covered = [], [], set(), set()
    paths = sorted(p for p in files if p.startswith('evidence/') and p.endswith('/provenance.json'))
    for path in paths:
        def fail(message):
            errors.append(diagnostic('evidence-provenance', path, message))
        try:
            data = json.loads(files[path].decode('utf-8'))
            if not isinstance(data, dict):
                raise ValueError('Expected a JSON object')
        except (ValueError, UnicodeError) as error:
            fail('Invalid provenance JSON: ' + str(error))
            continue
        for field in ('origin', 'date', 'attribution', 'source_type', 'original', 'locator'):
            if not isinstance(data.get(field), str) or not data[field].strip():
                fail('Provide nonempty ' + field + '.')
        if data.get('status') != 'evidence':
            fail('Set provenance status to evidence.')
        if not isinstance(data.get('source_type'), str) or data['source_type'] not in TYPES:
            fail('Use a recognized source_type: ' + ', '.join(sorted(TYPES)))
        value = data.get('date')
        if isinstance(value, str) and value != 'unknown':
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError()
                date.fromisoformat(value)
            except ValueError:
                fail('Use a valid YYYY-MM-DD date or unknown.')
        directory = posixpath.dirname(path)
        original = data.get('original')
        if isinstance(original, str) and original.strip():
            parsed = urlsplit(original)
            if ((parsed.scheme or parsed.netloc) and
                    (parsed.scheme not in {'http', 'https'} or not parsed.netloc)):
                fail('original must be a local file or an HTTP(S) source URL.')
            references.append((path, original, None, directory))
        items = data.get('files')
        if not isinstance(items, list) or not items:
            fail('Provide a nonempty files list.')
            continue
        seen = set()
        for item in items:
            if not isinstance(item, dict):
                fail('Each files entry must contain path and role.')
                continue
            name, role = item.get('path'), item.get('role')
            if not isinstance(role, str) or role not in ROLES:
                fail('Use a recognized retained-file role.')
            if not isinstance(name, str) or not name.strip():
                fail('Each files entry needs a nonempty path.')
                continue
            if urlsplit(name).scheme or name.startswith(('/', '//')):
                fail('files paths must be local paths relative to this submission.')
                continue
            references.append((path, name, None, directory))
            try:
                target = local_target(path, name, within=directory)
                if target is None:
                    continue
                resolved, fragment = target
                if fragment or urlsplit(name).query or resolved == path:
                    fail('files paths must identify a retained file, not a fragment, query or sidecar.')
                    continue
                if resolved in seen:
                    fail('Do not list the same retained file twice.')
                seen.add(resolved)
                covered.add(resolved)
                if role == 'original':
                    originals.add(resolved)
            except ValueError:
                pass  # Missing/escaping references belong to the internal-reference category.
        if isinstance(original, str) and original.strip():
            try:
                original_target = local_target(path, original, within=directory)
                if original_target and original_target[0] not in seen:
                    fail('Local original must identify a retained source in files, not a sidecar or directory.')
            except ValueError:
                pass  # The internal-reference check reports escaping original paths.
    for path in sorted(files):
        if path.startswith('evidence/') and path not in paths and path not in covered:
            errors.append(diagnostic('evidence-provenance', path,
                'Retain a provenance.json record covering this evidence file.'))
    return errors, references, originals
