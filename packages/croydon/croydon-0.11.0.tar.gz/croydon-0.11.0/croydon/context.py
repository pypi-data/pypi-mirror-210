import logging
import logging.handlers
import os
import sys
from logging import Logger, getLogger
from typing import Generic, TypeVar, Type, Optional
from .types import EnvironmentType, CacheType
from .config import BaseConfig
from .taskq.types import TBaseQueue
from .cache import TCache, NoCache, SimpleCache, MemcachedCache
from .db import DB
from .errors import ConfigurationError

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

C = TypeVar("C", bound=BaseConfig)
CT = Type[C]


# To avoid initialization issues Context must be fully synchronous
# i.e. no properties requiring async initialization are allowed.
# Thus, db moved out. It's not going to be needed anywhere besides
# StorableModel anyway.
class Context(Generic[C]):
    _env: Optional[EnvironmentType] = None
    _cfg: Optional[C] = None
    _log: Optional[Logger] = None
    _queue: Optional[TBaseQueue] = None
    _cache_l1: Optional[TCache] = None
    _cache_l2: Optional[TCache] = None
    _db: DB = None

    _project_dir: str
    _initialised = False

    @property
    def project_dir(self):
        return self._project_dir

    @property
    def initialised(self):
        return self._initialised

    @property
    def env(self) -> EnvironmentType:
        if self._env is None:
            raise RuntimeError("attempted to use uninitialised env")
        return self._env

    @property
    def cfg(self) -> C:
        if self._cfg is None:
            raise RuntimeError("attempted to use uninitialised config")
        return self._cfg

    @property
    def log(self) -> Logger:
        if self._log is None:
            raise RuntimeError("attempted to use uninitialised logging")
        return self._log

    @property
    def queue(self) -> TBaseQueue:
        if self._queue is None:
            raise RuntimeError("attempted to use uninitialised queue")
        return self._queue

    @property
    def cache_l1(self) -> TCache:
        if self._cache_l1 is None:
            raise RuntimeError("attempted to use uninitialised cache l1")
        return self._cache_l1

    @property
    def cache_l2(self) -> TCache:
        if self._cache_l2 is None:
            raise RuntimeError("attempted to use uninitialised cache l2")
        return self._cache_l2

    @property
    def db(self) -> DB:
        if self._db is None:
            raise RuntimeError("attempted to use uninitialised DB")
        return self._db

    def setup(self,
              project_dir: str,
              config: CT | C,
              env: Optional[EnvironmentType] = None) -> None:

        self._project_dir = project_dir

        if self._env is None:
            self._setup_env(env)

        if isinstance(config, BaseConfig):
            self._cfg = config
        else:
            self._cfg = self._setup_config(config)

        self._setup_logging()

        self._setup_cache()
        self._setup_db()  # needs logging and cache
        self._setup_queue()  # needs db
        self._initialised = True

    def _setup_db(self):
        self._db = DB(
            config=self._cfg.database,
            mock=False,
        )

    def _setup_cache(self):
        for prop in ["level1", "level2"]:
            cache_type: CacheType = getattr(self._cfg.cache, prop)

            if cache_type == "none":
                cache = NoCache()
            elif cache_type == "simple":
                cache = SimpleCache()
            elif cache_type == "memcached":
                backends = self._cfg.memcached.backends
                cache = MemcachedCache(backends)
            else:
                raise ConfigurationError(f"invalid cache type {cache_type}")

            if prop == "level1":
                self._cache_l1 = cache
            else:
                self._cache_l2 = cache

    def _setup_queue(self):
        if self._cfg.queue.type == "mongo":
            from .taskq.mongo_queue import MongoQueue
            self._queue = MongoQueue(self._cfg.mongo_queue)
        else:
            raise TypeError(f"queue type {self._cfg.queue.type} is invalid")

    def _setup_config(self, cfgcls: CT) -> C:
        config_filename = os.path.join(self._project_dir, f"{self._env}.toml")
        return cfgcls.parse(config_filename)

    def _setup_env(self, env: EnvironmentType = None):
        if env is None:
            env = "development"
            ext_env = os.getenv("CROYDON_ENV")
            if ext_env in ["development", "testing", "staging", "production"]:
                env = ext_env
        self._env = env

    def _setup_logging(self):
        logger = getLogger(__name__)
        logger.propagate = False

        lvl = _LOG_LEVELS.get(
            self._cfg.logging.level.lower(),
            logging.DEBUG
        )
        logger.setLevel(lvl)

        for handler in logger.handlers:
            logger.removeHandler(handler)

        log_format = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(message)s"
        )

        if self._cfg.logging.stdout:
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setLevel(lvl)
            handler.setFormatter(log_format)
            logger.addHandler(handler)

        if self._cfg.logging.filename is not None:
            handler = logging.handlers.WatchedFileHandler(self.cfg.logging.filename)
            handler.setLevel(lvl)
            handler.setFormatter(log_format)
            logger.addHandler(handler)

        self._log = logger


ctx = Context()
