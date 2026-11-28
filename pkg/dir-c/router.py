"""Sample module in pkg/dir-c owned by a disjoint approver group (dir-c-approvers)."""


def name() -> str:
    return "dir-c"


def owner_test() -> str:
    return "dir-c-disjoint"
