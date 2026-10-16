"""Trusted-branch runner: fetch PR blobs as data and report immutable-head statuses."""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, build_opener, HTTPRedirectHandler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import CATEGORIES, validate

MAX_RESPONSE = 24 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024
MAX_FILES = 20000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Do not forward credentials to a redirect destination.


class API:
    def __init__(self, token):
        if not token:
            raise ValueError('GITHUB_TOKEN is required')
        self.token = token
        self.opener = build_opener(NoRedirect())

    def request(self, method, route, payload=None):
        if not route.startswith('/repos/'):
            raise ValueError('Unsupported API route')
        body = json.dumps(payload).encode() if payload is not None else None
        request = Request('https://api.github.com' + route, data=body, method=method, headers={
            'Authorization': 'Bearer ' + self.token,
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/json',
            'User-Agent': 'curator-documentation-checks',
        })
        try:
            with self.opener.open(request, timeout=30) as response:
                data = response.read(MAX_RESPONSE + 1)
                if len(data) > MAX_RESPONSE:
                    raise OSError('GitHub response exceeds safe parsing capacity')
                return json.loads(data)
        except HTTPError as error:
            raise OSError(f'GitHub API HTTP {error.code}; check access and retry the trusted run') from None

    def get(self, route):
        return self.request('GET', route)

    def post(self, route, payload):
        return self.request('POST', route, payload)


def repo_name(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value):
        raise ValueError('Invalid GitHub repository identity')
    return value


def commit_sha(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-fA-F0-9]{40}', value):
        raise ValueError('Expected an immutable Git commit SHA')
    return value


def resolve_pr_number(event):
    value = event.get('number', event.get('inputs', {}).get('pr_number'))
    if isinstance(value, bool) or not re.fullmatch(r'[1-9][0-9]*', str(value)):
        raise ValueError('A positive numeric PR number is required')
    return int(value)


def materialize(api, repo, sha, destination):
    """Fetch shallow trees recursively to avoid silently truncated recursive trees."""
    repo_name(repo)
    commit_sha(sha)
    tree_sha = api.get(f'/repos/{repo}/git/commits/{sha}')['tree']['sha']
    pending = [('', tree_sha)]
    seen_paths, total = set(), 0
    while pending:
        prefix, tree = pending.pop()
        listing = api.get(f'/repos/{repo}/git/trees/{quote(tree, safe="")}')
        if listing.get('truncated'):
            raise OSError('Shallow Git tree is truncated; cannot validate all input')
        for entry in listing['tree']:
            path = prefix + entry['path']
            parts = PurePosixPath(path).parts
            if (not parts or path.startswith('/') or '\\' in path or '\x00' in path
                    or any(part in {'.', '..', '.git'} for part in parts)
                    or PurePosixPath(path).as_posix() != path):
                raise ValueError('Unsafe Git tree path')
            if len(parts) > 80:
                raise OSError('Tree nesting exceeds safe parsing capacity')
            if path in seen_paths:
                raise ValueError('Duplicate Git tree path')
            seen_paths.add(path)
            if len(seen_paths) > MAX_FILES:
                raise OSError('Tree exceeds safe parsing capacity; validation incomplete')
            if entry['type'] == 'tree' and entry['mode'] == '040000':
                pending.append((path + '/', entry['sha']))
                continue
            if entry['type'] != 'blob' or entry['mode'] not in {'100644', '100755'}:
                raise ValueError('Symlinks/submodules are not supported input: ' + path)
            blob = api.get(f'/repos/{repo}/git/blobs/{quote(entry["sha"], safe="")}')
            if blob.get('encoding') != 'base64':
                raise OSError('Unsupported Git blob encoding')
            data = base64.b64decode(''.join(blob['content'].split()), validate=True)
            total += len(data)
            if total > MAX_TOTAL:
                raise OSError('Content exceeds safe parsing capacity; validation incomplete')
            target = destination.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation also prevents aliases overwriting files on case-folded filesystems.
            with target.open('xb') as output:
                output.write(data)


def run(api, repo, number, trusted_sha, run_url):
    repo_name(repo)
    commit_sha(trusted_sha)
    resolve_pr_number({'number': number})
    head = None

    def publish(category, state, description):
        api.post(f'/repos/{repo}/statuses/{head}', {
            'state': state, 'context': 'curator/' + category,
            'description': description[:140], 'target_url': run_url,
        })

    try:
        pr = api.get(f'/repos/{repo}/pulls/{number}')
        base = commit_sha(pr['base']['sha'])
        if pr['state'] != 'open' or pr['base']['ref'] != 'main' or base != trusted_sha:
            raise ValueError('PR must be open on main and trusted code must match the current base; rerun from main')
        accepted = api.get(f'/repos/{repo}/git/ref/heads/main')['object']['sha']
        if accepted != trusted_sha:
            raise ValueError('Accepted branch advanced; rerun with current trusted code')
        head = commit_sha(pr['head']['sha'])
        source_repo = repo_name(pr['head']['repo']['full_name'])
        for category in CATEGORIES:
            publish(category, 'pending', 'Validating with accepted Curator rules')
        with tempfile.TemporaryDirectory(prefix='curator-data-') as tmp:
            materialize(api, source_repo, head, Path(tmp))
            results = {category: validate(Path(tmp), category) for category in CATEGORIES}
        current = api.get(f'/repos/{repo}/pulls/{number}')
        accepted = api.get(f'/repos/{repo}/git/ref/heads/main')['object']['sha']
        if (current['state'] != 'open' or current['base']['ref'] != 'main'
                or current['head']['sha'] != head or current['base']['sha'] != base
                or accepted != base):
            # No final write from stale work. A new run owns the current state.
            print('PR or accepted branch changed; rerun trusted validation.', file=sys.stderr)
            return 2
        for category, errors in results.items():
            # JSON escapes newlines, so input text cannot inject Actions workflow commands.
            print(json.dumps({'category': category, 'diagnostics': errors}, ensure_ascii=True))
            publish(category, 'failure' if errors else 'success', f'{len(errors)} objective violation(s)')
        return int(any(results.values()))
    except Exception as error:
        # No token or server response bodies in diagnostics. Preserve pending if reporting fails.
        print(f'Validation incomplete ({type(error).__name__}). Inspect input/access and rerun trusted checks.', file=sys.stderr)
        if head:
            for category in CATEGORIES:
                try:
                    publish(category, 'error', 'Validation did not complete; rerun trusted checks')
                except Exception:
                    pass
        return 2


def main():
    try:
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
        repo = repo_name(os.environ['GITHUB_REPOSITORY'])
        number = resolve_pr_number(event)
        trusted = commit_sha(os.environ['CURATOR_TRUSTED_SHA'])
        run_id = os.environ['GITHUB_RUN_ID']
        if not run_id.isdigit():
            raise ValueError('Invalid run ID')
        api = API(os.environ.get('GITHUB_TOKEN', ''))
        return run(api, repo, number, trusted, f'https://github.com/{repo}/actions/runs/{run_id}')
    except Exception as error:
        print(f'Cannot start trusted validation ({type(error).__name__}).', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
