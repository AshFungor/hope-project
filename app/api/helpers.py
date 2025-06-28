from betterproto import which_one_of
from functools import wraps
from datetime import datetime
from typing import Callable, Type

from betterproto import Message
from flask import request, Response as FlaskResponse

from app.context import AppContext, function_context
from app.codegen.hope import Response, Request


@function_context
def pythonify(ctx: AppContext, cls: Type[Message], might_be_empty: bool = True):
    def factory(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                req = Request().parse(request.data)
            except (ValueError, KeyError) as err:
                ctx.logger.debug(
                    f"{f.__name__}: failed to parse incoming request: {err}"
                )
                return "bad request", 406

            msg, payload = which_one_of(req, "payload")
            # if empty, this check passes even for goog payloads
            if not isinstance(payload, cls) and not might_be_empty:
                ctx.logger.debug(
                    f"{f.__name__}: failed to parse incoming request: want type: {cls.__name__}; "
                    f"got instead: {msg}"
                )
                return f"bad request: expected {cls.__name__}", 406

            return f(ctx, payload, *args, **kwargs)

        return wrapper

    return factory


def protobufify(obj: Response, status: int = 200) -> FlaskResponse:
    """
    Serialize as top-level Response, wrapping payload if needed.
    """
    try:
        return FlaskResponse(
            bytes(obj),
            content_type="application/protobuf",
            status=status
        )
    except (ValueError, KeyError):
        return FlaskResponse(
            "failed to serialize response",
            status=500
        )


def local_datetime(ctx: AppContext, dt: datetime) -> datetime:
    return dt.astimezone(ctx.config.timezone)
