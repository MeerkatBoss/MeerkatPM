from typing import Callable
import string

from meerkatpm.exceptions import UsageError

do_nothing = lambda *args, **kwargs: None 

def assert_error(cond: bool, message: str, callback: Callable[[], None] = do_nothing) -> None:
    if not cond:
        callback()
        raise UsageError(message)

def has_whitespace(s: str) -> bool:
    return any(c in s for c in string.whitespace)
