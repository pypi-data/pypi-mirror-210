import tomllib
from typing import Literal, Optional, Self, List
from pydantic import BaseModel, Field
from datetime import timedelta
from .types import CacheType, LogLevel


_DEFAULT_TIMEOUT = timedelta(seconds=1, milliseconds=100)
_DEFAULT_COOKIE_TTL = timedelta(days=90)


class SessionConfig(BaseModel):
    cookie: str = "_croydon_session_id"
    ttl: timedelta = _DEFAULT_COOKIE_TTL


class DatabaseConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(3000, gt=0, lt=65536)
    dbname: str = "croydondb"
    timeout: timedelta = _DEFAULT_TIMEOUT

    @property
    def uri(self) -> str:
        return f"mongodb://{self.host}:{self.port}/{self.dbname}"


class LogConfig(BaseModel):
    level: LogLevel = "debug"
    filename: Optional[str] = None
    stdout: bool = True


class QueueConfig(BaseModel):
    type: Literal["mongo"] = "mongo"


class MongoQueueConfig(BaseModel):
    tasks_collection: str = "croydon_tasks"
    keep_done_tasks_for: timedelta = timedelta(days=30)
    cleanup_interval: timedelta = timedelta(hours=1)


class CacheConfig(BaseModel):
    level1: CacheType = "simple"
    level2: CacheType = "memcached"


class MemcachedConfig(BaseModel):
    backends: List[str] = ["127.0.0.1:11211"]


class OAuthConfig(BaseModel):
    id: str
    secret: str
    authorize_url: str


class WebConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(3000, gt=0, lt=65536)


class GeneralConfig(BaseModel):
    documents_per_page: int = 20


class BaseConfig(BaseModel):
    session: SessionConfig = Field(default_factory=SessionConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LogConfig = Field(default_factory=LogConfig)
    oauth: Optional[OAuthConfig] = Field(None)
    web: WebConfig = Field(default_factory=WebConfig)
    general: GeneralConfig = Field(default_factory=GeneralConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)
    mongo_queue: MongoQueueConfig = Field(default_factory=MongoQueueConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    memcached: MemcachedConfig = Field(default_factory=MemcachedConfig)

    @classmethod
    def parse(cls, filename) -> Self:
        with open(filename, "rb") as f:
            config = tomllib.load(f)
        return cls(**config)
