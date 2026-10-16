# Cowork folder setup

Status: current

Use this procedure for an existing local Curator checkout in Claude desktop. It records the route verified on 16 October 2026: a dedicated Cowork project, an attached local folder, saved project instructions, and the installed Desktop Commander connector with authenticated Git and GitHub CLI on the host. It does not establish support for every Cowork account or version. See the [verification record](#verification-record) for evidence and limits.

## Connect the intended folder

1. Create or select a dedicated Claude project. For verification, use a new test session so existing drafts and unrelated conversations stay untouched.
2. Use the project's **Add folder** control to select only the intended checkout. A project context upload is not the same as live folder access. In the tested app, File → Open Folder routed to Code mode instead of this Cowork flow.
3. Review the native folder permission prompts. The test granted access for the session, leaving persistent permission unchecked. Folder access permits file operations; a read-only instruction is a behavioral constraint, not an OS permission boundary. Files used by the cloud session are processed by Anthropic.
4. Save the bootstrap below in the project's **Instructions**. Attach the folder when starting a fresh session; do not assume one session's attachment automatically applies to the next.

## Save a bootstrap that reads the shared instructions

The tested folder flow automatically supplied a staged `CLAUDE.md` containing `@AGENTS.md`, but did not expand that import. The fresh session did automatically receive saved project instructions and then explicitly read the repository files. Keep the shared policy in [AGENTS.md](../AGENTS.md); the bootstrap tells Cowork to retrieve it rather than maintaining a second policy copy.

Suggested project instructions, adapted from the verified test:

> Before answering a repository question, explicitly read AGENTS.md and the relevant entry points (README.md and docs/index.md) from the connected local repository. Do not assume the @AGENTS.md line in CLAUDE.md was expanded. Resolve the latest accepted remote main SHA for each question and read relevant files at that same SHA. Compare it with local HEAD and disclose any freshness limitation. Do not reset, pull over, or overwrite local changes. Treat staged uploads and unmerged PRs as potentially stale or proposed, not accepted main. Follow the repository instructions and explicit owner scope. Keep access within the attached repository and do not touch unrelated folders or drafts. Distinguish automatically supplied instructions from explicit file reads.

For the initial read-only test, add: “No file edits, commits, pushes, PRs, approvals, merges, settings changes, or cloud repository attachments.” This was the saved test project's default; the owner later authorized a narrowly scoped contribution exception. For normal contributions, follow [CONTRIBUTING.md](../CONTRIBUTING.md) after an explicit capture request. The test exception does not authorize further writes.

In a fresh session, ask Cowork to state its automatically supplied context before tools, then read the shared instructions and entry points explicitly. Have it report the remote main SHA, local HEAD and dirty state, and answer a small question with file citations. Repeat a question to check that it resolves the accepted revision again. Successful folder opening alone is not proof of this behavior.

Use read-only Git queries such as `git ls-remote origin refs/heads/main` for the remote revision. If the accepted commit is locally available, retrieve files with `git show <accepted-sha>:<path>`. Do not use local HEAD or a staged snapshot as accepted main without comparison. If a new remote commit is unavailable locally, use an authorized retrieval path that preserves existing work, or disclose the limitation; a successful `ls-remote` alone does not retrieve its files.

## Contribute through the verified host route

Reading a folder does not supply GitHub write credentials. The successful test used the already-installed Desktop Commander connector to run commands on the Mac hosting the attached checkout, with existing authenticated `git` and `gh`. It did not use a cloud clone, native cloud repository attachment, or a local Claude Code session. This connector is a prerequisite of the tested route, not a mandatory Curator dependency; another route needs its own verification.

For an authorized contribution:

1. Re-read AGENTS.md and CONTRIBUTING.md, resolve accepted main, inspect local changes and related open PRs, and preserve all unrelated work. If isolation cannot be achieved safely, stop with a concrete handoff.
2. Create a uniquely named branch from the accepted commit. Prepare only the requested changes and run the three validators using the pinned dependencies documented in [checks/README.md](../checks/README.md). Missing dependencies are not a passing result.
3. Use the host's existing GitHub authentication to commit, push the branch and open the focused PR. Do not copy host tokens to a cloud runtime or print credentials. Use a scoped commit identity if needed, rather than changing global Git configuration. If authorization is unavailable, report the blocked capability instead of substituting another environment silently.
4. Verify the PR URL, base/head SHAs, exact diff, required checks and review state. Report an open PR as pending, not published. Normal publication follows CONTRIBUTING.md and the effective review rules; AI acting through the author account is not independent human approval.

For a separately authorized capability test, use a disposable Markdown fixture marked `Status: template`, explicitly require a **draft PR**, and leave auto-merge disabled. Do not approve or merge it. After the owner requests cleanup, close it unmerged, delete only its test branches and return the clean checkout to main. Preserve existing drafts throughout.

## Verification record

Observed by Codex while operating the owner's isolated Claude desktop Cowork project on 16 October 2026; command execution was performed by the Cowork agent. This is a documented verification, not a verbatim transcript. The tested accepted revision was `e4192e5a040185efb383d329f68175d9c7c92a45` in `subvisual/curator`.

| Capability | Observed result and scope |
| --- | --- |
| Local reads | Cowork read repository instructions and relevant files through the attached checkout on the host. |
| Instruction loading | Saved project bootstrap loaded automatically in a fresh session; AGENTS.md was subsequently read explicitly. The staged CLAUDE.md import did not expand. |
| Freshness | Repeated remote-main resolution matched local HEAD. Cowork distinguished unmerged PR #3 from accepted main and disclosed the possible conflict between old docs and live settings. No advancing-main scenario was exercised. |
| Contribution | [Test PR #4](https://github.com/subvisual/curator/pull/4) was created from the local folder through Desktop Commander and host credentials. Head `19f9de2a02e38fa9c9f0a422b2b9c1016c32fe58` added only a seven-line disposable template. |
| Live checks and boundary | [GitHub Actions run](https://github.com/subvisual/curator/actions/runs/38928927315) passed all three required statuses. Codex independently verified draft state, review required, no auto-merge request and unchanged main. This was not a test of successful approved auto-merge. |
| Cleanup | PR #4 closed unmerged; remote/local test branches deleted; checkout returned clean to main. No existing drafts were modified. |

The PR body's generated Claude Code footer does not identify the execution route: the observed contribution used Cowork's host connector. A separate cloud attachment test in PR #2 is not evidence for folder behavior.

Still unverified: reuse/update of an existing PR through this folder route, refresh after accepted main advances, and independent local Claude Code CLI instruction/read/contribution behavior. The CLI was logged out at the last check. Automatic instruction import remains unsupported in this observed folder flow; keep the explicit bootstrap and verify again after relevant environment changes.

This record changes no review policy or GitHub settings. [PR #3](https://github.com/subvisual/curator/pull/3) separately proposes the team-review documentation update; its unmerged text is not treated as accepted main here. Keep that governance change independently reviewable.
