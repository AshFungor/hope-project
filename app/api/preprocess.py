from functools import wraps
from typing import Type, Callable

from flask import request
from betterproto import Message


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
    
