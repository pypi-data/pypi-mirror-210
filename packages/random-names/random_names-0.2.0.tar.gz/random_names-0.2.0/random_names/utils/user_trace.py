"""
Output for user to see.
"""
from random_names import settings as settings


def inform(value: str) -> None:
    """(Pretty) print progress"""
    if not settings.QUIET:
        print(value)
