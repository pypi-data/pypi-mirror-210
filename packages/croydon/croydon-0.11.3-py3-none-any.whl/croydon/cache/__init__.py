from typing import TypeVar
from .abc import AbstractCache
from .no_cache import NoCache
from .trace_cache import TraceCache
from .simple import SimpleCache
from .memcached import MemcachedCache

TCache = TypeVar("TCache", bound=AbstractCache)
