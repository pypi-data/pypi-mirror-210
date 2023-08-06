import importlib
from functools import partial


def load_handlers(handlers):
    return [build_handler(handler, value) for handler, value in handlers.items()]


def build_handler(handler, value):
    func = importlib.import_module(handler).handle

    if isinstance(value, dict):
        return partial(func, **value)
    return func
