from typing import Dict, Any, TypeVar, Type, Literal

T = TypeVar("T")  # any type
RT = TypeVar("RT")  # any func return type

TModel = TypeVar("TModel", bound="StorableModel")  # model type
TModelType = TypeVar("TModelType", bound=Type["StorableModel"])  # model class

QueryType = Dict[str, Any]
QueryExpression = str | QueryType

CommonDict = Dict[str, Any]
KwArgs = CommonDict

EnvironmentType = Literal["development", "testing", "staging", "production"]
CacheType = Literal["memcached", "simple", "none"]
LogLevel = Literal["critical", "error", "warning", "info", "debug"]

TConfig = TypeVar("TConfig", bound="BaseConfig")
TConfigType = Type[TConfig]
