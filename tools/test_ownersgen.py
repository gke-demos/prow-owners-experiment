import tempfile
from pathlib import Path
import unittest

import ownersgen


class OwnersGenTest(unittest.TestCase):
    def test_expands_aliases_and_preserves_no_parent_owners(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "OWNERS_ALIASES").write_text(
                """
aliases:
  maintainers:
    - alice
    - bob
  api-leads:
    - bob
    - carol
""",
                encoding="utf-8",
            )
            (root / "OWNERS.in").write_text(
                "approvers:\n  - maintainers\n",
                encoding="utf-8",
            )
            api_dir = root / "api"
            api_dir.mkdir()
            (api_dir / "OWNERS.in").write_text(
                """
options:
  no_parent_owners: true
approvers:
  - api-leads
reviewers:
  - dave
labels:
  - area/api
""",
                encoding="utf-8",
            )

            self.assertEqual(ownersgen.run(root, check_only=False), 0)
            self.assertEqual(ownersgen.run(root, check_only=True), 0)

            api_owners = (api_dir / "OWNERS").read_text(encoding="utf-8")
            self.assertIn("no_parent_owners: true", api_owners)
            self.assertIn("  - bob\n  - carol\n", api_owners)
            self.assertIn("labels:\n  - area/api\n", api_owners)

    def test_rejects_codeowners_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "OWNERS_ALIASES").write_text("aliases:\n  m:\n    - a\n", encoding="utf-8")
            (root / "OWNERS.in").write_text("approvers:\n  - m\n", encoding="utf-8")
            gh = root / ".github"
            gh.mkdir()
            (gh / "CODEOWNERS").write_text("* @m\n", encoding="utf-8")

            self.assertEqual(ownersgen.run(root, check_only=False), 1)


if __name__ == "__main__":
    unittest.main()
