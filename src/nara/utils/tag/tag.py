import typing as tp
from functools import wraps

def deleg(deleg, **kwargs):
    if type(deleg) != list:
        deleg = [deleg]
    def _deleg(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        inner.func = func
        inner.deleg = deleg
        inner.hasDelegate = True
        inner.kwargs = kwargs
        return inner
    return _deleg

def tag(
    key: tp.Union[str, tp.List[str]] = None,
    modes: tp.List[str] = [],
    canDigitalize: bool = True,
    prefix: bool = True,
    **kwargs,
) -> tp.Callable[..., tp.Any]:
    """A key tagger"""

    if type(key) != list:
        key = [key]

    def _tag(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        inner.key = key
        inner.func = func
        inner.modes = modes
        inner.tagged = True
        inner.kwargs = kwargs
        inner.hasTaggedKey = True
        inner.name = func.__name__
        inner.prefix = prefix
        inner.canDigitalize = canDigitalize
        return inner

    return _tag
