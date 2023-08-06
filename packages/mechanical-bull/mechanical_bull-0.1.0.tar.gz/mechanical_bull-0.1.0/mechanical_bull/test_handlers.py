import inspect

from .handlers import load_handlers


def test_load_handlers_simple():
    result = load_handlers({"mechanical_bull.actions.accept_follow_request": True})

    assert len(result) == 1

    assert inspect.iscoroutinefunction(result[0])


def test_load_handlers_with_argument():
    result = load_handlers(
        {"mechanical_bull.actions.log_to_file": {"filename": "logfile.txt"}}
    )

    assert len(result) == 1

    assert inspect.iscoroutinefunction(result[0])
