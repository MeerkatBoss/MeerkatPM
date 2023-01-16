from typing import Callable
import string

def assert_error(cond: bool, message: str, callback: Callable[[], None] = exit) -> None:
    if not cond:
        print(message)
        callback()

def assert_raise(cond: bool, message: str, error: type = ValueError) -> None:
    if not cond:
        raise error(message)

def has_whitespace(s: str) -> bool:
    return any(c in s for c in string.whitespace)