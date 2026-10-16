import json
import tempfile
import unittest
from pathlib import Path
from validate import validate


class Provenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sub = self.root / "evidence" / "submission"
        self.sub.mkdir(parents=True)
        (self.sub / "original.txt").write_text("Unmodified original", encoding="utf-8")
        self.record = dict(status="evidence", origin="Supplied account", date="unknown",
                           attribution="Named source", source_type="firsthand-account",
                           original="original.txt", files=[dict(path="original.txt", role="original")],
                           locator="Complete account")

    def save(self):
        (self.sub / "provenance.json").write_text(json.dumps(self.record), encoding="utf-8")

    def errors(self, category="evidence-provenance"):
        return validate(self.root, category)

    def test_complete_account_and_explicit_unknown_date(self):
        self.save()
        self.assertEqual(self.errors(), [])

    def test_each_required_field(self):
        for field in list(self.record):
            with self.subTest(field=field):
                value = self.record.pop(field)
                self.save()
                self.assertTrue(self.errors(), field)
                self.record[field] = value

    def test_dates_types_roles(self):
        for key, value in [("date", "2026-02-30"), ("source_type", "invented"),
                           ("files", [{"path": "original.txt", "role": "invented"}])]:
            old = self.record[key]
            self.record[key] = value
            self.save()
            self.assertTrue(self.errors())
            self.record[key] = old

    def test_missing_sidecar_and_orphan(self):
        self.assertTrue(self.errors())
        self.save()
        (self.sub / "orphan.pdf").write_bytes(b"preserved")
        self.assertTrue(self.errors())

    def test_malformed_and_nonobject_json(self):
        for value in ("{", "[]", "null"):
            (self.sub / "provenance.json").write_text(value, encoding="utf-8")
            self.assertTrue(self.errors())

    def test_missing_local_target_owned_by_link_category(self):
        (self.sub / "original.txt").unlink()
        self.save()
        self.assertEqual(self.errors(), [])
        self.assertTrue(self.errors("internal-references"))

    def test_external_original_no_network_and_local_transcript(self):
        self.record.update(original="https://invalid.invalid/private-recording", source_type="transcript")
        self.record["files"][0]["role"] = "transcript"
        self.save()
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.errors("internal-references"), [])

    def test_nested_relative_path_and_escape(self):
        self.record["files"].append({"path": "../escape.txt", "role": "extract"})
        self.save()
        self.assertTrue(self.errors("internal-references"))

    def test_malformed_field_types_are_provenance_diagnostics(self):
        for value in ([], {}):
            self.record['source_type'] = value
            self.record['files'][0]['role'] = value
            self.save()
            self.assertTrue(self.errors())
            self.assertEqual(self.errors('internal-references'), [])

    def test_original_must_identify_retained_source_not_sidecar(self):
        for value in ('provenance.json', '.', '//invalid.invalid/original'):
            self.record['original'] = value
            self.save()
            self.assertTrue(self.errors() + self.errors('internal-references'), value)

    def test_local_evidence_references_must_be_files(self):
        self.record['files'].append({'path': 'folder', 'role': 'original'})
        (self.sub / 'folder').mkdir()
        (self.sub / 'folder' / 'doc.txt').write_text('Text')
        self.save()
        self.assertTrue(self.errors('internal-references'))


if __name__ == "__main__":
    unittest.main()
