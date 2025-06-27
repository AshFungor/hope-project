from functools import wraps
from datetime import datetime
from typing import Callable, Type

from betterproto import Message
from flask import request, Response

from app.context import AppContext


def preprocess(cls: Type[Message]):
    def factory(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                req = cls().parse(request.data)
            except (ValueError, KeyError):
                return "bad request", 406

            return f(*args, req, **kwargs)

        return wrapper

    return factory


def protobufify(obj: Message, status: int = 200) -> Response:
    try:
        return Response(
            bytes(obj),
            content_type="application/protobuf",
            status=status
        )
    except ValueError:
        return Response(
            "failed to serialize response",
            status=500
        )
    

def local_datetime(ctx: AppContext, dt: datetime) -> datetime:
    return dt.astimezone(ctx.config.timezone)
