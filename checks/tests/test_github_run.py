import base64
import copy
import tempfile
import unittest
from pathlib import Path

from github_run import run, materialize, resolve_pr_number

BASE = 'a' * 40
HEAD = 'b' * 40
OTHER = 'c' * 40


class FakeAPI:
    def __init__(self):
        self.pr = {'state': 'open', 'base': {'ref': 'main', 'sha': BASE},
                   'head': {'sha': HEAD, 'repo': {'full_name': 'owner/repo'}}}
        self.statuses = []
        self.contents = {'README.md': b'# Hello\nStatus: current\n'}
        self.change = None
        self.metadata_reads = 0
        self.deny_blob = False
        self.truncated = False

    def get(self, route):
        if route.endswith('/pulls/1'):
            self.metadata_reads += 1
            if self.metadata_reads > 1 and self.change:
                self.pr[self.change]['sha'] = OTHER
            return copy.deepcopy(self.pr)
        if route.endswith('/git/ref/heads/main'):
            return {'object': {'sha': self.pr['base']['sha']}}
        if '/git/commits/' in route:
            return {'tree': {'sha': HEAD}}
        if '/git/trees/' in route:
            return {'truncated': self.truncated, 'tree': [
                {'path': p, 'type': 'blob', 'mode': '100644', 'sha': str(i)}
                for i, p in enumerate(self.contents)]}
        if '/git/blobs/' in route:
            if self.deny_blob:
                raise OSError('Denied')
            data = list(self.contents.values())[int(route.rsplit('/', 1)[1])]
            return {'encoding': 'base64', 'content': base64.b64encode(data).decode()}
        raise AssertionError(route)

    def post(self, route, payload):
        self.statuses.append((route, payload))
        return {}


class GitHubRun(unittest.TestCase):
    def run_it(self, api):
        return run(api, 'owner/repo', 1, BASE, 'https://github.com/owner/repo/actions/runs/1')

    def test_valid_head_three_successes(self):
        api = FakeAPI()
        self.assertEqual(self.run_it(api), 0)
        self.assertEqual([s['state'] for _, s in api.statuses], ['pending'] * 3 + ['success'] * 3)
        self.assertTrue(all(route.endswith(HEAD) for route, _ in api.statuses))

    def test_candidate_validator_is_never_executed(self):
        api = FakeAPI()
        api.contents['README.md'] += b'[broken](absent.md)\n'
        api.contents['checks/validate.py'] = b'raise RuntimeError("UNTRUSTED CODE EXECUTED")'
        api.contents['sitecustomize.py'] = b'raise RuntimeError("UNTRUSTED IMPORT")'
        self.assertEqual(self.run_it(api), 1)
        final = {s['context']: s['state'] for _, s in api.statuses[-3:]}
        self.assertEqual(final['curator/internal-references'], 'failure')
        self.assertEqual(final['curator/document-status'], 'success')

    def test_missing_status_is_failure(self):
        api = FakeAPI()
        api.contents['README.md'] = b'# Hello'
        self.assertEqual(self.run_it(api), 1)
        self.assertEqual(api.statuses[-1][1]['state'], 'failure')

    def test_changed_head_or_base_never_reports_success(self):
        for field in ('head', 'base'):
            api = FakeAPI()
            api.change = field
            self.assertEqual(self.run_it(api), 2)
            self.assertNotIn('success', [s['state'] for _, s in api.statuses])

    def test_denied_blob_is_error_not_green(self):
        api = FakeAPI()
        api.deny_blob = True
        self.assertEqual(self.run_it(api), 2)
        self.assertEqual([s['state'] for _, s in api.statuses[-3:]], ['error'] * 3)

    def test_truncated_shallow_tree_fails_closed(self):
        api = FakeAPI()
        api.truncated = True
        self.assertEqual(self.run_it(api), 2)
        self.assertNotIn('success', [s['state'] for _, s in api.statuses])

    def test_untrusted_base_does_not_publish(self):
        api = FakeAPI()
        api.pr['base']['sha'] = OTHER
        self.assertEqual(self.run_it(api), 2)
        self.assertEqual(api.statuses, [])

    def test_non_main_or_closed_does_not_publish(self):
        for key in ('closed', 'branch'):
            api = FakeAPI()
            if key == 'closed':
                api.pr['state'] = 'closed'
            else:
                api.pr['base']['ref'] = 'other'
            self.assertEqual(self.run_it(api), 2)
            self.assertEqual(api.statuses, [])

    def test_unsafe_tree_paths_never_materialized(self):
        for path in ('../outside', '/absolute', '.git/config', 'a/../../escape'):
            api = FakeAPI()
            api.contents = {path: b'unsafe'}
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    materialize(api, 'owner/repo', HEAD, Path(tmp))

    def test_event_number_is_validated(self):
        self.assertEqual(resolve_pr_number({'number': 42}), 42)
        self.assertEqual(resolve_pr_number({'inputs': {'pr_number': '7'}}), 7)
        for event in ({}, {'number': True}, {'number': -1}, {'inputs': {'pr_number': '1;exit'}}):
            with self.assertRaises(ValueError):
                resolve_pr_number(event)


if __name__ == '__main__':
    unittest.main()
