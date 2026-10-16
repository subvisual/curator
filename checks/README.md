# Documentation checks
Status: current

Curator blocks exactly three objective documentation categories. A successful check does not establish factual truth. Writing quality, duplication, whether evidence supports a claim, and unreachable external URLs remain advisory; a human reviewer can still withhold approval.

## Run locally

Use Python 3.12 or newer. Keep the environment outside the repository. From its root:

```sh
python3 -m venv ../curator-venv
../curator-venv/bin/python -m pip install --require-hashes --only-binary=:all: -r checks/requirements.lock
PYTHONPATH=checks ../curator-venv/bin/python -m unittest discover -s checks/tests -v
../curator-venv/bin/python -I checks/validate.py --root . --category internal-references
../curator-venv/bin/python -I checks/validate.py --root . --category evidence-provenance
../curator-venv/bin/python -I checks/validate.py --root . --category document-status
```

Use `--format json` for diagnostics with category, repository path, line when available and repair message. Exit 0 means valid, 1 means objective violations, 2 means validation could not complete. Do not interpret an infrastructure error or missing check as a pass. Tests exercise the validators, not an AI answering benchmark.

## Internal references

Markdown inline/reference links, images, HTML links, repository files, sections and provenance file references must resolve. Code blocks and inline code are ignored. Local paths are case-sensitive; URL-encoded names and query strings are handled. Repository-root paths begin with `/`. Relative paths resolve from the linking file. References cannot escape the repository; provenance file references must stay within their submission directory.

Headings use GitHub-style anchors, including duplicate suffixes and Unicode. Explicit `<a id="stable-name"></a>` anchors are preferable for durable section references. Exotic rendering differences still need confirmation against GitHub before release; no live rendering compatibility test has been performed in local setup. PDF and other binary fragments are advisory locators, not parsed sections. External URLs are never fetched by these checks.

Unmodified original Markdown is evidence from another context: its embedded relative links are not reinterpreted as repository links. The sidecar's retained-file and original references are checked. Link to it through the submission sidecar, which supplies its provenance and role. Missing local evidence targets fail this category, not provenance twice. Symlinks and submodules cannot act as evidence pointing outside the inspected tree.

## Evidence provenance

Every retained file under `evidence/` must be covered by a submission's `provenance.json`. Create a submission only for actual intake; no empty evidence tree is needed. Paths in `files` and local `original` resolve relative to the sidecar directory. Use an existing HTTP(S) shared-storage URL for an external original, with local notes/transcript or a labeled extract. All readers must have access; access suitability is human-reviewed, never a blocking network probe.

A sidecar is a JSON object with these required fields:

| Field | Value |
| --- | --- |
| `status` | `evidence` |
| `origin` | Nonempty description of where the original came from |
| `date` | Valid `YYYY-MM-DD` or `unknown`; never a fabricated date |
| `attribution` | Person/organization, or explicit unknown/anonymous attribution scoped by the reviewer |
| `source_type` | `document`, `meeting-notes`, `transcript`, `firsthand-account`, `verification`, or `extraction` |
| `original` | Local retained original path or original HTTP(S) source URL |
| `files` | Nonempty list of objects with `path` and `role` |
| `locator` | Nonempty section/page/release/time range or complete-account locator |

File roles: `original`, `notes`, `transcript`, `extract`, `translation`, `rendering`. Optional `language` and `limitations` preserve useful context. A reviewer judges whether attribution, role and locator meaningfully describe the source. JSON presence alone does not establish support or accuracy. Firsthand accounts distinguish reported experience from independently verified system behavior. Transcripts are not recording-verified unless that check happened. Preserve originals byte for byte and do not duplicate an original already in shared storage.

Malformed records, missing fields, unknown types/roles, and uncovered evidence files fail provenance. No provenance record or verification date is generated from filesystem modification times.

## Document status

All maintained Markdown files require exactly one early visible standalone `Status: current`, `Status: superseded`, or `Status: template` line before the first substantive section. `current` identifies the maintained page at the inspected revision, not factual currentness. Branch files remain proposals until merged. The starter routing page is a template; replace it with supported project navigation during setup.

Retained Markdown notes/transcripts/extracts require `Status: evidence`. Label the source type visibly too. Unmodified original Markdown is exempt from in-file status edits when its sidecar lists its role as `original`. Other original formats use sidecar labeling. `CLAUDE.md`, the PR body template and synthetic `checks/tests/` fixtures are exempt. JSON, binaries and executable code do not require document status. There is no user-supplied ignore list. Changing labels to evade intended review remains a human-review issue.

## Trusted execution and deployment

The [documentation workflow](../.github/workflows/documentation.yml) loads code and its hash-locked dependencies from the accepted default-branch commit, never from the PR. The [runner](github_run.py) retrieves proposed tree blobs into a temporary data directory; it never checks out or executes them. It reports `curator/internal-references`, `curator/evidence-provenance` and `curator/document-status` on the captured PR head SHA, then checks head and accepted-base freshness before final results. A base change requires a fresh run from current `main`; use the workflow's manual PR-number input if necessary. A missing report blocks merge when protection is configured.

No parsing operation fetches external sources. The runner's GitHub API transport is fixed to GitHub.com and does not forward credentials through redirects. It descends shallow Git trees to avoid accepting a truncated recursive listing. Truncated shallow trees, unsupported symlinks/submodules, nesting beyond 80 levels, over 20,000 tree entries, API responses over 24 MiB or total content over 100 MiB cause incomplete validation rather than success. These are resource limits, not new policy checks; keep large originals in shared storage and investigate an incomplete run without weakening review rules.

Bind required status contexts to the observed Actions app during [owner setup](../SETUP.md). That binding is not authentication of a unique workflow: trusted writers and administrators remain a governance boundary. Every workflow, check, instruction and ownership edit requires existing eligible human review and an explicitly requested maintenance PR. Proposed rules cannot authorize their own adoption. Test proposed validator code locally without privileged credentials; merge under the old validators. Use additive schema migrations when needed.

The [auto-merge workflow](../.github/workflows/enable-auto-merge.yml) only enables GitHub's native auto-merge; it neither approves nor directly merges. After verifying protections, enable repository variable `CURATOR_AUTOMERGE_ENABLED=true`. Until then the workflow is dormant. A denied mutation leaves an unsuccessful workflow run and a pending enablement action; an assistant must report that limitation, never promise automatic publication. It is not a fourth required documentation check. Repository settings and collaborator permissions are not configured by these files.

Action pins were resolved from public upstream tags: checkout v4.2.2 and setup-python v5.6.0. Parser dependencies are markdown-it-py 4.0.0 and mdurl 0.1.2, locked to downloaded wheel hashes. Dependency upgrades follow the same owner-requested maintenance workflow.
