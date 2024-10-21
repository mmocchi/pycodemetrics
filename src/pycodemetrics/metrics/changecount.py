from collections import Counter

from pycodemetrics.gitclient.models import GitFileCommitLog


def calculate_changecount(gitlogs: list[GitFileCommitLog]) -> Counter:
    """
    Calculate the change count.

    Args:
        gitlogs (list[GitFileCommitLog]): A list of GitFileCommitLog.

    Returns:
        Counter: The change count by commiter.
    """

    changecount_by_commiter = Counter([gitlog.author for gitlog in gitlogs])
    return changecount_by_commiter
