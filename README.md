# prow-owners-experiment

Live sandbox repository for testing [`cncf/prow-github-actions`](https://github.com/cncf/prow-github-actions) (`v3.5.0`), hierarchical Kubernetes-style `OWNERS` files, file-defined `OWNERS_ALIASES` groups, and GitHub Merge Queue before rolling out folder-level ownership to `agent-substrate/substrate`.

## Repository layout and folder rules

GitHub `.github/CODEOWNERS` is intentionally absent (`./hack/verify-owners.sh` fails CI if a `CODEOWNERS` file is added) so folder-level `Approvers` and `Reviewers` **never need repository `Write` access**.

Instead, group memberships live in [`OWNERS_ALIASES`](OWNERS_ALIASES), directory inputs live in `OWNERS.in`, and `./hack/update-owners.sh` compiles flat `OWNERS` files read by `cncf/prow-github-actions`:

| Path | `no_parent_owners` | `approvers` group | `reviewers` group | Auto-applied `labels` | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/OWNERS` | `false` | `maintainers` | `root-reviewers` | *(none)* | Root Maintainers inherited by normal subsystems |
| `/.github/OWNERS` | **`true`** | `maintainers` | `root-reviewers` | `area/dev-infra` | Protects workflows and Prow config |
| `/api/OWNERS` | **`true`** | `api-approvers` | `api-reviewers` | `area/api` | Strict API tree (root Maintainers not in `api-approvers` cannot bypass) |
| `/pkg/dir-a/OWNERS` | **`true`** | `dir-a-approvers` | `dir-a-reviewers` | `area/node` | Scenario 1 & 2 folder A (shares approver `U` with `dir-b`) |
| `/pkg/dir-b/OWNERS` | **`true`** | `dir-b-approvers` | `dir-b-reviewers` | `area/storage` | Scenario 1 folder B (shares approver `U` with `dir-a`) |
| `/pkg/dir-c/OWNERS` | **`true`** | `dir-c-approvers` | `dir-c-reviewers` | `area/network` | Scenario 2 folder C (disjoint approver `V`) |
| `/site/OWNERS` | `false` | `site-approvers` | `site-reviewers` | `area/site`, `area/docs` | Subsystem inheriting root `maintainers` |
| `/docs/OWNERS` | `false` | `site-approvers` | `site-reviewers` | `area/docs` | Docs subsystem inheriting root `maintainers` |

## Adding non-`Write` test accounts (`Read` or `Triage` only)

Note that `gke-demos` organization owners (`moficodes`, `bwsalmon`, `mastersingh24`) automatically inherit `admin` (`Write`) on `gke-demos` repos. To test **true non-`Write` folder approval** (`push: false`):

1. Invite two non-owner GitHub accounts (`USER_U` and `USER_V`) with `triage` (or `pull` / `Read`) access only:

   ```bash
   gh api -X PUT repos/gke-demos/prow-owners-experiment/collaborators/USER_U -f permission=triage
   gh api -X PUT repos/gke-demos/prow-owners-experiment/collaborators/USER_V -f permission=triage

   # Confirm push=false (`role_name` is "triage", NOT "write" or "admin"):
   gh api repos/gke-demos/prow-owners-experiment/collaborators/USER_U/permission --jq '{permission, role_name}'
   ```

2. Add `USER_U` to `dir-a-approvers` and `dir-b-approvers` (and `USER_V` to `dir-c-approvers`) in [`OWNERS_ALIASES`](OWNERS_ALIASES), regenerate `OWNERS`, and merge to `main`:

   ```bash
   ./hack/update-owners.sh
   ./hack/run-tests.sh
   ```

## 6-scenario experiment checklist

1. **Common non-`Write` approver across two directories (Tim #1):**
   Open a fork PR modifying `pkg/dir-a/service.py` and `pkg/dir-b/store.py`. Have `USER_U` (`push: false`) comment `/approve`, and have a second reviewer comment `/lgtm`. Verify `approved` + `lgtm` + `prow/lgtm` turn green and `tide` enqueues the PR into the Merge Queue to squash-merge.
2. **Disjoint non-`Write` approvers across directories (Tim #2):**
   Open a fork PR modifying `pkg/dir-a/service.py` and `pkg/dir-c/router.py`. Verify `USER_U` commenting `/approve` alone leaves `approved` unset in `[APPROVALNOTIFIER]`, and once `USER_V` also comments `/approve`, `approved` is applied.
3. **File-defined groups (`OWNERS_ALIASES`, Tim #3):**
   Edit [`OWNERS_ALIASES`](OWNERS_ALIASES) without running `./hack/update-owners.sh` and open a PR; verify `run-tests` fails until `./hack/update-owners.sh` is run.
4. **Separate `/approve` vs. `/lgtm` checks (Tim #4):**
   On a PR touching `site/index.md`, have a `site-approvers` member comment `/approve` (or click GitHub's `Approve` review button) without `/lgtm`. Verify `approved` is set while `lgtm` stays missing and the PR does not merge until a non-author reviewer comments `/lgtm`. Then push a new commit and verify `lgtm` and `prow/lgtm` reset while `approved` stays.
5. **Strict `no_parent_owners` (`/api/`):**
   Temporarily remove a root maintainer from `api-approvers` and verify they cannot satisfy `/approve` on a PR touching `api/v1/actor.yaml`.
6. **Non-`Write` `/ok-to-test` and `/retest`:**
   Open a PR from a first-time external fork or trigger a failed job, and verify `USER_U` (`Triage`/`Read` in `OWNERS`) can run `/ok-to-test` and `/retest` without repository `Write`.
