"""Sample module in pkg/dir-c owned by a disjoint approver group (dir-c-approvers)."""


def name() -> str:
    return "dir-c"


def fork_owner_test() -> str:
    return "dir-c-fork-disjoint"
