from functools import wraps
from io import StringIO
from typing import Callable

from flask import request

from app.context import AppContext, function_context


def bulk(f: Callable):
    @wraps(f)
    @function_context
    def wrapper(ctx: AppContext):
        ctx.logger.warning(f"calling bulk api: {f.__name__} - hope it's you")

        if "file" not in request.files:
            return "Bulk API needs a file", 406

        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 406

        stream = StringIO(file.stream.read().decode("utf-8-sig"))
        return f(ctx, stream)

    return wrapper
