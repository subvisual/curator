# Curator

Status: current

Curator is a reusable starter for evidence-backed project knowledge. Each project gets an independent repository, separate from production code, with readable explanations, traceable sources, and one maintained home per topic.

**Initial starter publication:** [subvisual/curator](https://github.com/subvisual/curator), authorized on 16 October 2026. The owner explicitly waived independent human seed review once for this initial snapshot, following independent AI review and local verification. This exception does not apply to future changes. Primary approver `ABZerra` is the current code owner; the backup remains intentionally pending, so primary-authored changes must wait for an eligible independent owner. Native settings must be verified separately; live review/merge behavior and Cowork PR submission remain unverified. License selection is deferred; public visibility alone does not grant a general reuse license.

## Start here

- **Owner:** follow [setup](SETUP.md) to establish an independent repository. Projects are private by default; personal accounts and organizations are supported, with organizations recommended for teams.
- **Reader:** start at the [topic index](docs/index.md), then ask naturally in Cowork or Claude Code after one-time access setup. The index is a template until real project sources are incorporated.
- **Contributor:** an explicit request to incorporate information starts the [contribution workflow](CONTRIBUTING.md). Proposals become accepted knowledge only after independent human approval and passing checks.
- **AI assistant:** use the shared [instructions](AGENTS.md). `CLAUDE.md` imports them where supported; Cowork instruction loading requires account-specific verification.

Maintained documentation is English; conversations use the reader's preferred language and originals retain theirs. Supported summaries and comparisons need no extra permission. State gaps, scope, dates, and encountered contradictions. Approval authorizes publication; it does not prove a claim true.

The repository covers purpose, users, capabilities, decisions, priorities, milestones, and limitations. Detailed delivery tracking and generated reports or presentations belong outside it. Add topic pages and evidence only when actual content warrants them. There is no scheduled intake, automatic starter sync, review deadline, mandatory skill, AI-review service, or separate backend.

## Validation and origin

[Check documentation](checks/README.md) defines the local commands and exact evidence/status format. Exactly three documentation statuses block publication: `curator/internal-references`, `curator/evidence-provenance`, and `curator/document-status`. Semantic findings and unreachable external sources are advisory; an approver may still request changes.

[Starter origin](.curator/origin.json) records provenance and selective upgrades. No release has been tagged. The origin record identifies the starter repository; its own bootstrap commit is null because a commit cannot contain its own hash. Adopters must record the actual immutable starter commit they copy. Independent projects adopt upgrades only through an explicitly requested maintenance PR; copying files does not copy or verify GitHub settings.
