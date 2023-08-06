from __future__ import annotations

from inspect import currentframe
from types import TracebackType
from typing import TypeVar

from result import Err

T = TypeVar("T", bound=Exception)


def enriched_error(exception: T, msg: str | None = None, cause: Exception | None = None, _number_of_f_backs: int = 3) -> Err[T]:  # noqa: E501
    exception = enrich_exception(exception, msg, cause, _number_of_f_backs)
    return Err(exception)


def enrich_exception(exception: T, msg: str | None = None, cause: Exception | None = None, _number_of_f_backs: int = 2) -> T:  # noqa: E501
    exception.__cause__ = cause
    old_trace_back = exception.__traceback__
    exception.__traceback__ = _get_callers_traceback(_number_of_f_backs)

    if old_trace_back is not None:
        exception.add_note(msg or "")

    if old_trace_back is None and cause is not None:
        exception.__traceback__.tb_next = cause.__traceback__
    else:
        exception.__traceback__.tb_next = old_trace_back

    return exception


def _get_callers_traceback(number_of_f_backs: int = 2) -> TracebackType:
    frame = currentframe()
    if frame is None:
        raise RuntimeError("`currentframe` for the _get_callers_traceback function was not found!")

    for i in range(number_of_f_backs):
        frame = frame.f_back

        if frame is None:
            raise RuntimeError(f"`currentframe` for the {i+1}th f_back was not found!")

    return TracebackType(
        None,
        tb_frame=frame,
        tb_lasti=frame.f_lasti,
        tb_lineno=frame.f_lineno,
    )
