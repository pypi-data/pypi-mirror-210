from typing import Any, Callable, Dict


class CitizenKError(ValueError):
    """Raised when there is an error in the fuzzy engine (not when the error is fuzzy :-) )"""


def annotate_function(f: Callable, name: str, doc: str, argument_types: Dict[str, Any]):
    f.__name__ = name
    f.__qualname__ = name
    f.__doc__ = doc
    for key, value in argument_types.items():
        f.__annotations__[key] = value
