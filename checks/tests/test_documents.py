import json
import tempfile
import unittest
from pathlib import Path

from validate import validate


class Documents(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def errors(self, category):
        return validate(self.root, category)

    def test_status_required_and_valid_values(self):
        for status in ("current", "superseded", "template"):
            self.put("README.md", f"# Page\nStatus: {status}\n\n## Detail\nText\n")
            self.assertEqual(self.errors("document-status"), [])
        for text in ("# Page\n", "Status: draft\n", "Status: current\nStatus: current\n",
                     "# Page\n## Detail\nStatus: current\n", "```\nStatus: current\n```\n"):
            self.put("README.md", text)
            self.assertEqual(len(self.errors("document-status")), 1, text)

    def test_instructions_exemptions_and_arbitrary_md(self):
        self.put("CLAUDE.md", "@AGENTS.md\n")
        self.put(".github/pull_request_template.md", "## Change\n")
        self.put("checks/tests/example.md", "fixture")
        self.put("other.md", "# Not exempt")
        self.assertEqual([e["path"] for e in self.errors("document-status")], ["other.md"])

    def test_original_md_unchanged_and_extract_requires_evidence(self):
        self.put("evidence/s/raw.md", "Original without status")
        self.put("evidence/s/extract.md", "# Extract\nStatus: evidence\n")
        self.put("evidence/s/provenance.json", json.dumps({"files": [
            {"path": "raw.md", "role": "original"}, {"path": "extract.md", "role": "extract"}]}))
        self.assertEqual(self.errors("document-status"), [])
        self.put("evidence/s/extract.md", "Status: current\n")
        self.assertEqual(len(self.errors("document-status")), 1)

    def test_links_fragments_images_reference_and_code(self):
        self.put("README.md", """# Page
Status: current
[good](docs/Topic%20One.md?x=1#café--usage)
[root](/docs/Topic%20One.md#repeat-1)
![image][asset]
[asset]: docs/image.png
[same](#page)
`[ignored](missing.md)`
```
[ignored](missing.md)
```
[outside](https://invalid.invalid/missing)
[email](mailto:reader@example.com)
""")
        self.put("docs/Topic One.md", "# Café & Usage!\n## Repeat\n## Repeat\n")
        self.put("docs/image.png", "fake binary")
        self.assertEqual(self.errors("internal-references"), [])

    def test_missing_case_escape_and_missing_anchor(self):
        self.put("README.md", "[a](missing.md) [b](topic.md) [c](../out.md) [d](Topic.md#absent)")
        self.put("Topic.md", "# Exists\n")
        self.assertEqual(len(self.errors("internal-references")), 4)

    def test_html_anchors_and_binary_fragment(self):
        self.put("README.md", '[x](#explicit)\n<a id="explicit"></a>\n[x](source.pdf#page=2)')
        self.put("source.pdf", "binary")
        self.assertEqual(self.errors("internal-references"), [])

    def test_symlink_not_followed(self):
        (self.root / "escape.md").symlink_to(Path(__file__))
        self.put("README.md", "[unsafe](escape.md)")
        self.assertTrue(self.errors("internal-references"))

    def test_bad_root_is_execution_error(self):
        with self.assertRaises(OSError):
            validate(self.root / "absent", "document-status")

    def test_multiline_inline_code_does_not_supply_status(self):
        self.put('README.md', '# Example\n\n`example\nStatus: current\nexample`\n')
        self.assertTrue(self.errors('document-status'))

    def test_links_to_ancestor_directories(self):
        self.put('README.md', '[docs](docs/)')
        self.put('docs/topics/topic.md', '# Topic')
        self.assertEqual(self.errors('internal-references'), [])

    def test_cache_named_directories_cannot_hide_proposed_documents(self):
        self.put('evidence/__pycache__/account.md', '[broken](missing.md)')
        for category in ('internal-references', 'evidence-provenance', 'document-status'):
            self.assertTrue(self.errors(category), category)


if __name__ == "__main__":
    unittest.main()
