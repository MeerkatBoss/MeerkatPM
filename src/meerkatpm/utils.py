from functools import partial
from typing import Callable, TypeVar
import string

from meerkatpm.exceptions import UsageError

do_nothing = lambda *args, **kwargs: None 

def assert_error(cond: bool, message: str, callback: Callable[[], None] = do_nothing) -> None:
    if not cond:
        callback()
        raise UsageError(message)

def has_whitespace(s: str) -> bool:
    return any(c in s for c in string.whitespace)

T = TypeVar('T', bound=Callable)
Decorator = Callable[[T], T]

progress_report: Callable[[str], Decorator] =\
        lambda msg: lambda func: lambda *args: progress_report_impl(msg, func, *args)

result_report: Callable[[str], Decorator]=\
        lambda msg: lambda func: lambda *args: result_report_impl(msg, func, *args)

def progress_report_impl(message: str, func: Callable, *args):
    print(message+'... ', end='', flush=True)
    func(*args)
    print('Done.')

def result_report_impl(message: str, func: Callable, *args):
    func(*args)
    print(message)
    

