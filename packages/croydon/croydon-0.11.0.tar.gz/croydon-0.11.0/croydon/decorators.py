import inspect
from typing import Callable, Awaitable, Any, List
from functools import wraps, update_wrapper
from time import time

from .types import KwArgs, TModel, TModelType, RT
from .errors import ObjectSaveRequired


def save_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    save_required decorator is meant to decorate model methods that
    require a model instance to be saved first.

    For example, StorableModel's own db_update method makes no sense
    until the instance is persisted in the database
    """
    @wraps(func)
    def wrapper(self, *args: List[Any], **kwargs: KwArgs) -> Any:
        if self.is_new:
            raise ObjectSaveRequired("This object must be saved first")
        return func(self, *args, **kwargs)

    return wrapper


class api_field:
    """
    api_field is a decorator for model no-args methods (including async),
    allowing API users to access certain methods, i.e. implementing computed fields
    """

    def __init__(self, fn):
        if not inspect.isfunction(fn):
            raise RuntimeError("only functions and methods can be decorated with api_field")
        self.fn = fn

    def __set_name__(self, owner, name):
        from .models.fields import ComputedField
        fd = ComputedField(is_async=inspect.iscoroutinefunction(self.fn))

        # computed_fields are inherited from MetaModel down the class tree
        # here we make sure every descendant does not modify parent's computed fields
        owner._computed_fields = owner._computed_fields.copy()
        owner._computed_fields[name] = fd
        setattr(owner, name, self.fn)


class model_cached_method:
    """
    model_cached_method decorates model methods. The wrapper provided
    generates a unique cache key out of
    - model class name
    - model id
    - method name

    e.g. User.6433d2bfd5a353b0a6822d7f.full_name

    and tries to fetch the value from cache. If value is not there, the
    original method is called and the value is stored to cache before
    being returned

    The methods wrapped with this decorator are automatically added to a
    class property called _cached_methods: set. This allows StorableModel.invalidate
    method to invalidate these cached values along with other model-provided cache.
    """

    orig_func: Callable[[TModel, ...], Awaitable[RT]] = None

    def __init__(self, func: Callable[[TModel, ...], Awaitable[RT]]) -> None:
        self.orig_func = func

    def __set_name__(self, owner: TModelType, name: str) -> None:

        @wraps(self.orig_func)
        async def wrapper(this: TModel, *args, **kwargs) -> RT:
            from .context import ctx
            cache_key = f"{this.collection}.{this.id}.{self.orig_func.__name__}"

            t1 = time()
            value = await ctx.cache_l1.get(cache_key)
            if value is not None:
                td = time() - t1
                ctx.log.debug(
                    "%s L1 hit %s %.3f secs", ctx.cache_l1.NAME, cache_key, td
                )
                return value

            t1 = time()
            value = await ctx.cache_l2.get(cache_key)
            if value is not None:
                td = time() - t1
                ctx.log.debug(
                    "%s L2 hit %s %.3f secs", ctx.cache_l2.NAME, cache_key, td
                )
                await ctx.cache_l1.set(cache_key, value)
                return value

            t1 = time()
            value = await self.orig_func(this, *args, **kwargs)
            td = time() - t1
            ctx.log.debug("%s miss %s %.3f secs", ctx.cache_l2.NAME, cache_key, td)
            await ctx.cache_l2.set(cache_key, value)
            await ctx.cache_l1.set(cache_key, value)

            return value

        owner._cached_methods.add(name)
        setattr(owner, name, wrapper)
