import typing as tp

_T = tp.TypeVar('_T')


def notnull(value: _T | None) -> _T:
    if value is None:
        raise ValueError('value cannot be None')  # noqa: TRY003, EM101
    assert value is not None  # noqa: S101
    return value
