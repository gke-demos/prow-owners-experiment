# prow-owners-experiment

Live sandbox repository for testing [`cncf/prow-github-actions`](https://github.com/cncf/prow-github-actions) (`v3.5.0`), hierarchical Kubernetes-style `OWNERS` files, file-defined `OWNERS_ALIASES` groups, and GitHub Merge Queue before rolling out folder-level ownership to `agent-substrate/substrate`.

## Configured test accounts and permissions

`moficodes` is the repository admin (`maintainers`). To prove that folder-level `Approvers` and `Reviewers` **do not need repository `Write` access**, three Agent Substrate contributors are wired into [`OWNERS_ALIASES`](OWNERS_ALIASES) and invited strictly at **`Triage` (`push: false`)**:

- **`thockin`** (Tim Hockin) — `Triage` (`push: false`)
- **`destijl`** (Greg Castle) — `Triage` (`push: false`)
- **`HavenXia`** (Haven Xia) — `Triage` (`push: false`)

*(Note: `/approve`, `/lgtm`, `/retest`, and `/ok-to-test` work immediately from `OWNERS` on `main` even before accepting the GitHub `Triage` invitation; accepting the invitation enables `blunderbuss` auto-review requests and UI label controls.)*

## Repository layout and folder rules

GitHub `.github/CODEOWNERS` is intentionally absent (`./hack/verify-owners.sh` fails CI if a `CODEOWNERS` file is added) so GitHub never imposes a `Write` permission check on folder owners.

Group memberships live in [`OWNERS_ALIASES`](OWNERS_ALIASES), directory inputs live in `OWNERS.in`, and `./hack/update-owners.sh` compiles flat `OWNERS` files read by `cncf/prow-github-actions`:

| Path | `no_parent_owners` | `approvers` | `reviewers` | Auto-applied `labels` | Scenario tested |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/OWNERS` | `false` | `moficodes` | `thockin`, `destijl`, `HavenXia` | *(none)* | Root Maintainers inherited by normal subsystems |
| `/.github/OWNERS` | **`true`** | `moficodes` | `thockin`, `destijl`, `HavenXia` | `area/dev-infra` | Protects workflows and Prow config |
| `/api/OWNERS` | **`true`** | `thockin`, `moficodes` | `HavenXia`, `destijl` | `area/api` | Strict API tree (`no_parent_owners: true`) |
| `/pkg/dir-a/OWNERS` | **`true`** | `thockin`, `destijl` | `HavenXia` | `area/node` | Scenario 1 & 2 folder A (common non-`Write` approvers with `dir-b`) |
| `/pkg/dir-b/OWNERS` | **`true`** | `thockin`, `destijl` | `HavenXia` | `area/storage` | Scenario 1 folder B (common non-`Write` approvers with `dir-a`) |
| `/pkg/dir-c/OWNERS` | **`true`** | `HavenXia` | `thockin`, `destijl` | `area/network` | Scenario 2 folder C (disjoint non-`Write` approver from `dir-a`) |
| `/site/OWNERS` | `false` | `HavenXia`, `destijl` *(+ root `moficodes`)* | `thockin` | `area/site`, `area/docs` | Subsystem inheriting root `maintainers` |
| `/docs/OWNERS` | `false` | `HavenXia`, `destijl` *(+ root `moficodes`)* | `thockin` | `area/docs` | Docs subsystem inheriting root `maintainers` |

## Ready-to-try pull requests

- **PR #1 (`site/index.md`):** Tests root `OWNERS` inheritance + separate `/approve` vs. `/lgtm` (Tim #4). Already carries `approved`; commenting `/lgtm` from `thockin`, `destijl`, or `HavenXia` sets commit-bound `prow/lgtm` and enqueues into GitHub Merge Queue.
- **PR #2 (`pkg/dir-a/` + `pkg/dir-c/`):** Tests **disjoint non-`Write` approvers** (Tim #2). Even repo admin `moficodes` cannot approve this PR (`no_parent_owners: true`); neither `thockin`/`destijl` alone nor `HavenXia` alone suffices, and once `{thockin or destijl}` **and** `HavenXia` both `/approve` (plus `/lgtm`), it enqueues and merges.
- **PR #3 (`pkg/dir-a/` + `pkg/dir-b/`):** Tests **single common non-`Write` approver** across multiple folders (Tim #1). Either `thockin` or `destijl` alone (with `push: false`) covers both folders with a single `/approve`.
