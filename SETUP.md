# Owner setup

Status: current

This procedure prepares an independent project knowledge repository. Local starter files are not a configured GitHub repository. External creation, authentication, publication, PRs, and settings changes require a concrete authorized destination and scope. Curator's initial seed is authorized under the one-time exception recorded below. Repository settings and live behavior must be verified separately.

## A. Establish the repository from sources

1. Record the destination (personal account or organization), project purpose, intended readers, primary human approver, backup, and contributor access. Prefer an organization for teams. Ask only for missing information. Projects are private by default; public visibility needs the project's explicit decision. All repository readers must also be able to access retained external originals.
2. Verify the destination's plan supports required PRs, eligible code-owner review, required checks, stale-approval dismissal, strict branch freshness, and auto-merge for the chosen visibility. If an upgrade is needed, explain it and leave setup incomplete; do not weaken controls or make a project public as a workaround. Check current [GitHub ruleset availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) against the actual account.
3. After external setup is authorized, create an independent repository from the reviewed starter, using `main` as the accepted branch. Inspect the initial seed before it is trusted: an independent eligible human must review the seed, including workflows and validators, before privileged execution or publication of accepted project knowledge. A first commit is not proof of reviewed provenance. If the account cannot support an independently reviewed bootstrap, stop external setup with a concrete limitation rather than self-approving or bypassing review.
4. Record the verified starter source repository, commit, and release in `.curator/origin.json`, with project kind and an accurate adoption record. Do not invent a published release for this unreleased local starter. Preserve local adaptations and the original source identity for later selective upgrades.
5. Apply and verify the native controls below. Copying a template, CODEOWNERS, workflow, or policy file does not apply GitHub settings. Leave setup incomplete until the effective controls are confirmed.
6. Inspect supplied documents, notes, links, and accessible originals first. Preserve evidence using [CONTRIBUTING.md](CONTRIBUTING.md). Identify coherent topics and ask only about meaningful gaps or conflicts; use an interview when sources are sparse. Replace the template index with useful supported explanations and explicit unknowns, rather than empty folders or invented facts.
7. Open the initial documentation PR. If the primary authored it, the backup reviews. Enable auto-merge for the PR; passing required checks and valid independent human approval publish the knowledge. No eligible reviewer means waiting, not a timeout bypass.

For **Curator itself**, the public destination is [subvisual/curator](https://github.com/subvisual/curator), with description “Curator — a reusable starter for evidence-backed project knowledge.” Primary approver `ABZerra` is an active organization member with repository administrator access; the organization has the Team plan. On 16 October 2026 the owner explicitly authorized a one-time exception to independent human seed review for the initial starter publication after independent AI review and local validation. This is not a standing bootstrap bypass for adopters or later changes. The backup remains intentionally pending. CODEOWNERS lists only the verified primary until an eligible backup is established; future primary-authored changes cannot obtain independent code-owner approval during this gap. Required reviews, stale-approval dismissal, required checks, and administrator enforcement remain required. Contributor scope and live enforcement behavior remain unverified. License selection is deferred, with no default license. No first project is required.

## Native review and merge configuration

Use repository Settings and the account's supported native ruleset or branch-protection UI. Verify the effective state, including overlapping organization rules, rather than relying on a saved configuration screen. Both personal and organization destinations must satisfy the same outcomes.

1. In `.github/CODEOWNERS`, configure a single wildcard rule covering every file with the verified primary and backup accounts, both eligible with the required repository access. Use actual verified logins; do not activate sample identities. Listing two owners allows either to approve; it does not require two approvals or decide whether the primary is unavailable. Keep coverage for the CODEOWNERS file and workflow/check changes themselves.
2. In Settings → Rules → Rulesets (or the supported branch-protection equivalent), target `main`, activate enforcement, require pull requests and **one** approval, require code-owner review, and dismiss stale approvals after file/diff changes. Do not add a separate last-push approval requirement that would unintentionally demand a second reviewer. Comments alone must leave approval intact.
3. Require precisely these three documentation status contexts, selecting the expected GitHub App when the UI supports it:

   - `curator/internal-references`
   - `curator/evidence-provenance`
   - `curator/document-status`

   Require the PR branch to be up to date with `main` before merging (strict current-branch checks). If contexts are not yet available for selection, use the reviewed seed to obtain legitimate check runs, then bind the contexts before accepting project contributions. A missing required context must leave the PR blocked, never count as success.
4. Apply protections to administrators as well as other contributors; configure no bypass actors, and prevent direct protected-branch pushes, force pushes, and deletion. Inspect other applicable rules and privileged access paths for loopholes. An author cannot approve their own PR, including through an AI using their account. Repository administrators remain trusted to maintain settings; files cannot prevent an administrator from changing external configuration.
5. In Settings → General → Pull Requests, allow auto-merge and squash merging. Enable auto-merge **on each PR** through GitHub's native PR action or the authenticated native contribution path. After verifying effective protections, set the Actions repository variable `CURATOR_AUTOMERGE_ENABLED` to `true` to activate the included automatic enablement workflow. It remains dormant until then and only enables the native mechanism; it never grants approval or directly calls merge. This is a one-time setup switch, not another PR approval or required check. Approval is the final human publication authorization once required checks pass; do not introduce a second approval ceremony or custom merge service.
6. Review Actions permissions and the trusted workflow in [checks/README.md](checks/README.md). PR contents are untrusted input: run accepted validators against proposed files as data, never proposed scripts, dependencies, or workflows with privileged PR credentials. Maintenance is assessed by old trusted checks and existing review rules. Binding a required context to GitHub Actions identifies the App, not a specific workflow; it is not a complete same-App anti-spoof guarantee. Restrict trusted writers, review workflow changes, and preserve administrator accountability. There is no fourth authorization status.

Use [GitHub CODEOWNERS guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), [protected branch guidance](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), and [native auto-merge guidance](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request) to locate the controls for the account. These references describe building blocks, not verified enforcement in this repository.

## One-time reader and contributor access

Cowork is the minimum intended environment; Claude Code is also supported. Teammates may need repository access, folder or supported connector selection, and authentication once. Ordinary use should then be access-and-ask, with no mandatory skills or special commands. Reading access and contribution access are separate capabilities.

For Cowork, use the account's existing supported folder/project or native connection. Verify that shared instructions are actually available, relevant repository files can be read, and the accepted `main` SHA can be resolved and used for selective retrieval. A repository URL, successful folder opening, manual import, or ordinary Claude chat integration is not proof of automatic instruction loading, ongoing freshness, or PR capability. The thin `CLAUDE.md` import is for environments that support it; it does not establish Cowork behavior.

Bound account-specific verification to the authorized destination and capabilities: inspect available supported access, verify a selective read and current revision, and, only when separately authorized, use a real focused contribution to verify opening and reusing a PR. Record the actual account/surface, date, revision, result, and remaining limitation. Stop when the native path is unavailable or incompatible; do not build a connector, introduce a paid backend, or keep trying unrelated integrations. **Cowork PR support remains unverified.** Successful Claude Code operation does not substitute for a working Cowork path.

When PR submission is unavailable, provide the concrete contribution handoff from [CONTRIBUTING.md](CONTRIBUTING.md). When current revision access fails, answer from available material with its revision/date and explicit freshness limitation. Neither fallback is proof that the intended direct-submission or automatic-freshness behavior works. Do not overwrite a dirty checkout to refresh.

## Effective verification record

The following checks require observed evidence; publication alone does not mark them verified. Fill results only from observed behavior or effective settings on the authorized account; keep evidence and any diagnostic artifacts outside project knowledge unless explicitly contributed. Necessary implementation verification is not a pilot or teammate-trial prerequisite. Controlled external changes need authorization.

| Area | Evidence required to mark verified |
| --- | --- |
| Destination and access | Exact account/repository identity, visibility, qualifying plan, reader and contributor access; verified primary/backup eligibility |
| Seed trust | Independent human review of the initial seed and workflow/check implementation before relying on it |
| Effective protection | Active rules for `main`, no bypass, direct/force push and deletion restrictions, and administrative applicability |
| Review eligibility | One eligible code-owner approval suffices; author cannot approve; owner-authored work waits for backup |
| Check enforcement | Exact three contexts, expected App binding where supported, all required; failed or missing context blocks merge |
| Branch freshness | PR must be current with `main`; stale results do not permit merge after accepted-branch changes |
| Approval lifetime | File changes dismiss approval and rerun checks; comments do not dismiss it |
| Auto-merge | Repository enabled and individual PR enabled; merge follows valid approval and passing checks without an active AI session |
| Execution trust | Proposed code is never executed with privileged PR credentials; workflow/App attribution limits documented |
| Cowork access | Shared instructions, selective files at a coherent current SHA, repeated revision resolution, and honest failure behavior observed |
| Cowork contribution | Authorized direct PR creation and reuse observed, or explicit unresolved limitation and concrete handoff fallback |
| Claude Code access | Instruction loading and authorized read/contribution capabilities verified independently where used |
| Maintenance | Existing eligible reviewer checks recorded owner request/scope; approved settings changes applied and separately verified |

If an observation contradicts the intended behavior, record the failure and leave that capability unverified. Do not claim full setup from local validator results alone.

## Local checks

Use Python and an environment outside the repository; install pinned dependencies from `checks/requirements.lock` as explained in [checks/README.md](checks/README.md). Run from the repository root:

```sh
python3 checks/validate.py --root . --category internal-references --format text
python3 checks/validate.py --root . --category evidence-provenance --format text
python3 checks/validate.py --root . --category document-status --format text
PYTHONPATH=checks python3 -m unittest discover -s checks/tests -v
```

The validator also accepts `--format json`. Local checks verify only their three objective categories, not claim truth, external accessibility, native account compatibility, or GitHub enforcement.
