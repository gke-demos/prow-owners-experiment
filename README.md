# prow-owners-experiment

Live sandbox repository for testing [`cncf/prow-github-actions`](https://github.com/cncf/prow-github-actions) (`v3.5.0`), hierarchical Kubernetes-style `OWNERS` files, file-defined `OWNERS_ALIASES` groups, the `ready-for-pr` linked-issue gate (`#3922` / `#4055`), and GitHub Merge Queue before rolling out to `agent-substrate/substrate`.

## Configured test accounts and permissions

`moficodes` is the repository admin (`maintainers`). To prove that folder-level `Approvers` and `Reviewers` **do not need repository `Write` access**, four Agent Substrate contributors are wired into [`OWNERS_ALIASES`](OWNERS_ALIASES) and invited strictly at **`Triage` (`push: false`)**:

- **`thockin`** (Tim Hockin) — `Triage` (`push: false`)
- **`BenTheElder`** (Benjamin Elder) — `Triage` (`push: false`)
- **`destijl`** (Greg Castle) — `Triage` (`push: false`)
- **`HavenXia`** (Haven Xia) — `Triage` (`push: false`)

*(Note: `/approve`, `/lgtm`, `/retest`, `/ok-to-test`, and `/reopen` work immediately from `OWNERS` on `main` even before accepting the GitHub `Triage` invitation; accepting the invitation enables `blunderbuss` auto-review requests and `ready-for-pr` UI label management.)*

## `ready-for-pr` linked-issue enforcement (`check-ready-issue`)

Every PR (including Drafts) runs `check-ready-issue` ([`tools/check_ready_issue.py`](tools/check_ready_issue.py)) **before** Prow runs `blunderbuss` or `[APPROVALNOTIFIER]`:

1. The PR description must include `Fixes #NNN` (or `Closes`/`Resolves`) or `Part of #NNN` pointing to an **open** issue in this repo carrying the **`ready-for-pr`** label.
2. If missing, `check-ready-issue` immediately **closes the PR** with instructions and skips the `prow` job so domain reviewers are never spammed.
3. Once the author links a `ready-for-pr` issue in the PR description and comments **`/reopen`**, Prow reopens the PR and runs `check-ready-issue` + `OWNERS` routing automatically.

## Repository layout and folder rules

GitHub `.github/CODEOWNERS` is intentionally absent (`./hack/verify-owners.sh` fails CI if a `CODEOWNERS` file is added) so GitHub never imposes a `Write` permission check on folder owners.

| Path | `no_parent_owners` | `approvers` | `reviewers` | Auto-applied `labels` | Scenario tested |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/OWNERS` | `false` | `moficodes` | `thockin`, `BenTheElder`, `destijl`, `HavenXia` | *(none)* | Root Maintainers inherited by normal subsystems |
| `/.github/OWNERS` | **`true`** | `moficodes` | `thockin`, `BenTheElder`, `destijl`, `HavenXia` | `area/dev-infra` | Protects workflows and Prow config |
| `/api/OWNERS` | **`true`** | `thockin`, `BenTheElder`, `moficodes` | `HavenXia`, `destijl` | `area/api` | Strict API tree (`no_parent_owners: true`) |
| `/pkg/dir-a/OWNERS` | **`true`** | `thockin`, `BenTheElder`, `destijl` | `HavenXia` | `area/node` | Scenario 1 & 2 folder A (common non-`Write` approvers with `dir-b`) |
| `/pkg/dir-b/OWNERS` | **`true`** | `thockin`, `BenTheElder`, `destijl` | `HavenXia` | `area/storage` | Scenario 1 folder B (common non-`Write` approvers with `dir-a`) |
| `/pkg/dir-c/OWNERS` | **`true`** | `HavenXia` | `thockin`, `BenTheElder`, `destijl` | `area/network` | Scenario 2 folder C (disjoint non-`Write` approver from `dir-a`) |
| `/site/OWNERS` | `false` | `HavenXia`, `BenTheElder`, `destijl` *(+ root `moficodes`)* | `thockin` | `area/site`, `area/docs` | Subsystem inheriting root `maintainers` |
| `/docs/OWNERS` | `false` | `HavenXia`, `BenTheElder`, `destijl` *(+ root `moficodes`)* | `thockin` | `area/docs` | Docs subsystem inheriting root `maintainers` |
