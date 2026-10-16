# Contributing project knowledge

Status: current

## Capture an explicit request

“Incorporate these notes” or “store this project information” authorizes preparing and opening a focused documentation PR. Useful-looking conversation content alone does not: offer first. Anyone may propose factual updates. All incoming material remains proposed until approved and merged.

During report, presentation, or other artifact work, keep the deliverable outside the knowledge repository and cite its supporting pages/revision. Hand an explicitly requested capture to a separate documentation workflow with relevant information, attribution, and necessary context. The artifact workflow can continue independently. Use a supported separate worker/context where available; automatic creation of a sidebar chat is not assumed.

Before writing, inspect relevant accepted topics, retained evidence, and related open proposals. Classify the result as an existing-topic update, justified new topic, evidence only, or no change. Reuse retained originals and avoid empty PRs and automatic meeting-summary pages. Reuse the same workflow's related open PR for subsequent related information; make unrelated updates independently reviewable and create a new PR after an earlier one has merged.

## Preserve evidence and write the explanation

Keep small originals under `evidence/<submission>/` and preserve their bytes and original language. Large originals, including recordings, stay in existing shared storage accessible to every repository reader. Retain relevant notes, transcripts, or labeled extracts locally alongside provenance and the external original link; do not present an extract as the complete original. Do not create evidence directories until there is evidence to retain.

Meeting notes or transcripts are the baseline; recordings are optional supporting evidence. If only a recording is supplied, obtain notes or a transcript from the contributor's existing tools. This starter does not provide a transcription service. Notes are not verbatim transcripts, and a transcript is not verified against audio unless someone actually performed that verification. Attribute firsthand accounts and distinguish reported experience from independently verified behavior or policy.

Every submission needs `provenance.json` with these fields:

| Field | Value |
| --- | --- |
| `status` | `evidence` |
| `origin` | Identifiable source origin |
| `date` | Relevant ISO date, or `unknown` |
| `attribution` | Author, speaker, organization, or verifier; explicitly record unknown or anonymous attribution when applicable rather than inventing it |
| `source_type` | `document`, `meeting-notes`, `transcript`, `firsthand-account`, `verification`, or `extraction` |
| `original` | Local relative original path or HTTPS URL |
| `files` | List of objects with `path` and `role`; cover every retained evidence file except the sidecar itself |
| `locator` | Useful source section, page, timestamp, release, or other precise locator |

File roles are `original`, `notes`, `transcript`, `extract`, `translation`, and `rendering`. Optional `language` and `limitations` clarify interpretation. See [the exact format and path rules](checks/README.md) before preparing the sidecar. Local missing file/section targets are internal-reference failures; malformed or missing metadata belongs to evidence provenance. External reachability is advisory and no validator fetches external links.

Original Markdown remains byte-preserved and is identified as original evidence by its sidecar rather than an inserted status line. Other evidence Markdown needs an early standalone `Status: evidence` line; a visible `Source type:` note is recommended. Maintained Markdown uses `Status: current`, `Status: superseded`, or `Status: template` after its title. All Markdown outside evidence and validator test fixtures is covered, except the thin `CLAUDE.md` adapter and PR template. Mark superseded pages visibly and point readers to the successor; history retains earlier positions.

Write maintained explanations in English with sources near substantive claims or coherent claim groups. Keep one home per topic; link from navigation instead of restating facts. Distinguish accepted decisions, observations, plans, research, interpretations, and unknowns. Preserve qualifications and meaningful verification scope/date/version. Ask only when ambiguity or conflict prevents a responsible proposal; useful incomplete explanations may retain explicit gaps. Approval establishes the accepted position, not factual truth.

## Submit and publish

Describe what changes, why, supporting evidence, related proposals, and unresolved concerns using [the PR template](.github/pull_request_template.md). Run the three checks as documented in [checks/README.md](checks/README.md):

```sh
python3 checks/validate.py --root . --category internal-references --format text
python3 checks/validate.py --root . --category evidence-provenance --format text
python3 checks/validate.py --root . --category document-status --format text
```

Exactly `curator/internal-references`, `curator/evidence-provenance`, and `curator/document-status` are required documentation checks. Evidence relevance, wording, duplication, and unreachable external links are advisory findings, but a human reviewer can request changes. Passing metadata checks does not prove a claim true. AI assistance is optional; no AI sign-off or fourth gate is required.

Request review from any invited team member with accepted repository access and effective write permission or higher. One eligible independent human approval suffices; no designated primary approver or backup is required. Nobody self-approves and an AI using the author's account is not independent human review. Public readers and pending invitations do not qualify. Without an eligible reviewer, the PR waits. Enable native auto-merge for this PR once authorized submission is available; repository-level enablement alone is insufficient. File changes invalidate approval and rerun checks; comments alone do not. Valid approval and passing checks authorize publication without a second manual confirmation.

If native access cannot submit a PR, provide a handoff containing the current statement and source, proposed change, supporting evidence, unresolved questions, and related open PR if known. Say that submission is pending. The [verified Cowork route](docs/cowork-setup.md) uses an attached local folder, Desktop Commander and existing host GitHub credentials. Other environments still need verification; a handoff does not demonstrate direct submission and must not silently become a Claude Code-only requirement.

For an unanswered question, offer a documentation-gap issue with established facts, unknowns, why it matters, and the relevant topic. Inspect duplicates and create it only after the reader accepts. Do not turn this into assignment or deadline tracking.

## Owner-requested maintenance

Changing instructions, validators, workflows, or approvers, and adopting starter upgrades, requires an explicit owner request and a separate focused maintenance PR. Ordinary intake cannot loosen these rules. Record the requester, authorized scope, relevant request context, behavioral changes, and any required GitHub settings changes. The existing eligible reviewer verifies the owner request and scope; there is no additional authorization check or initiator-identity service.

Compare requested changes against [.curator/origin.json](.curator/origin.json) and local adaptations. Preserve project knowledge and evidence; identify conflicts and omitted changes. Validate the proposal with currently trusted checks. Proposed check/workflow code must never execute with privileged PR credentials; the existing reviewer evaluates code changes under existing rules, not rules proposed by the PR itself. Expected GitHub App binding is useful but cannot distinguish trusted and untrusted workflows produced by the same App; writer/admin trust and review controls still matter.

Record the actual starter source and specific adopted changes in `adoptions`, identifying partial adoption as partial rather than claiming a whole release. Preserve known origin and use null for unknown source values. After merge, apply only authorized setting changes and verify their effective state; report remaining work. Other project repositories stay independent. No schedule, automatic upgrades, expiry, or recurring review obligation is introduced.
