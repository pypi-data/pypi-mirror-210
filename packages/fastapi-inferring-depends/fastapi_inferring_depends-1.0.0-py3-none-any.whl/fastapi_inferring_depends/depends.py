import typing as t

from fastapi import params  # type: ignore

TDepends = t.TypeVar("TDepends")


@t.overload
def Depends(
    dependency: t.Callable[..., t.AsyncGenerator[TDepends, None]],
    *,
    use_cache: bool = True,
) -> TDepends:
    ...


@t.overload
def Depends(
    dependency: t.Callable[..., t.Coroutine[None, None, TDepends]],
    *,
    use_cache: bool = True,
) -> TDepends:
    ...


@t.overload
def Depends(
    dependency: t.Callable[..., t.Generator[TDepends, None, None]],
    *,
    use_cache: bool = True,
) -> TDepends:
    ...


@t.overload
def Depends(
    dependency: t.Callable[..., TDepends], *, use_cache: bool = True
) -> TDepends:
    ...


@t.overload
def Depends(dependency: None = None, *, use_cache: bool = True) -> t.Any:
    ...


def Depends(
    dependency: t.Optional[t.Callable[..., t.Any]] = None,
    *,
    use_cache: bool = True,
) -> t.Any:
    return params.Depends(dependency=dependency, use_cache=use_cache)  # type: ignore


__all__ = ("Depends",)
