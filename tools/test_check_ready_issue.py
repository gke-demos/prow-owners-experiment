import unittest

import check_ready_issue


REPO = "gke-demos/prow-owners-experiment"


class CheckReadyIssueTest(unittest.TestCase):
    def test_extracts_fixes_and_part_of_while_ignoring_comments_and_code(self) -> None:
        body = """
<!-- Keep `Fixes #999` or replace with `Part of #998` -->
```markdown
Fixes #997
```
Why is this needed?

Part of #12
Also closes https://github.com/gke-demos/prow-owners-experiment/issues/34
and Fixes gke-demos/prow-owners-experiment#56.
"""
        self.assertEqual(
            check_ready_issue.extract_linked_issues(body, REPO),
            [12, 34, 56],
        )

    def test_rejects_missing_issue_link(self) -> None:
        ok, reason = check_ready_issue.evaluate_pr("Just a quick fix", "alice", REPO, lambda _: None)
        self.assertFalse(ok)
        self.assertIn("No linked issue", reason)

    def test_rejects_pr_reference_closed_issue_and_unlabeled_issue(self) -> None:
        fake_db = {
            1: {"state": "open", "pull_request": {}, "labels": [{"name": "ready-for-pr"}]},
            2: {"state": "closed", "labels": [{"name": "ready-for-pr"}]},
            3: {"state": "open", "labels": [{"name": "kind/bug"}]},
        }
        body = "Part of #1\nPart of #2\nFixes #3"
        ok, reason = check_ready_issue.evaluate_pr(body, "alice", REPO, fake_db.get)
        self.assertFalse(ok)
        self.assertIn("pull request, not an issue", reason)
        self.assertIn("is closed", reason)
        self.assertIn("does not carry the `ready-for-pr` label", reason)

    def test_accepts_open_ready_for_pr_issue(self) -> None:
        fake_db = {
            10: {"state": "open", "labels": [{"name": "area/site"}, {"name": "ready-for-pr"}]},
        }
        ok, reason = check_ready_issue.evaluate_pr("Part of #10", "alice", REPO, fake_db.get)
        self.assertTrue(ok)
        self.assertIn("#10", reason)


if __name__ == "__main__":
    unittest.main()
