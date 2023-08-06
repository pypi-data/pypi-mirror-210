from typing import Dict, Any, Iterable, Optional, TypeVar, Type, List
from copy import deepcopy
from pydantic import BaseModel as PydanticModel
from pymongo.errors import OperationFailure
from ..context import ctx
from ..errors import DoNotSave
from ..db import Shard, ObjectsCursor
from .fields import ObjectIdField
from .meta_model import MetaModel
from ..types import KwArgs

TBaseModel = TypeVar("TBaseModel", bound="BaseModel")
TPydanticModel = TypeVar("TPydanticModel", bound=PydanticModel)
undef = object()


class BaseModel(MetaModel):

    id: ObjectIdField = ObjectIdField()
    _initial_state: dict[str, Any]

    def __init__(self, attrs: Optional[Dict[str, Any]] = None, **_kwargs: KwArgs) -> None:
        if attrs is None:
            attrs = {}

        for field, descriptor in self._fields.items():
            if field == "id":
                value = attrs.get("_id", undef)
            else:
                value = attrs.get(field, undef)
            if value is undef:
                descriptor.set_default(self)
            else:
                # setting via __dict__ will ignore descriptors
                setattr(self, field, value)
        self._set_initial_state()

    async def validate_all(self) -> None:
        for descriptor in self._fields.values():
            await descriptor.validate(self)
        await self.validate()

    async def validate(self) -> None:
        pass

    @property
    def is_new(self) -> bool:
        return self.id is None

    def _set_initial_state(self) -> None:
        self._initial_state = {
            field: deepcopy(getattr(self, field))
            for field in self._fields
        }

    def is_modified(self) -> bool:
        for field in self._fields:
            value = self.__dict__[field]
            if value != self._initial_state[field]:
                return True
        return False

    async def _before_save(self) -> None:
        pass

    async def _before_validation(self) -> None:
        pass

    async def _before_delete(self) -> None:
        pass

    async def _after_save(self, is_new: bool) -> None:
        pass

    async def _after_delete(self) -> None:
        pass

    async def _save_to_db(self) -> None:
        pass

    async def _delete_from_db(self) -> None:
        pass

    async def invalidate(self, **kwargs: Dict[str, Any]) -> None:
        pass

    async def destroy(self: TBaseModel, skip_callback: bool = False, invalidate_cache: bool = True) -> TBaseModel:
        if self.is_new:
            return self
        if not skip_callback:
            await self._before_delete()

        if invalidate_cache:
            await self.invalidate()

        await self._delete_from_db()
        if not skip_callback:
            await self._after_delete()

        self.id = None
        return self

    async def save(self: TBaseModel, skip_callback: bool = False, invalidate_cache: bool = True) -> TBaseModel:
        is_new = self.is_new

        if not skip_callback:
            try:
                await self._before_validation()
            except DoNotSave:
                return self
        await self.validate_all()

        if not skip_callback:
            try:
                await self._before_save()
            except DoNotSave:
                return self

        if invalidate_cache:
            await self.invalidate()

        await self._save_to_db()

        self._set_initial_state()
        if not skip_callback:
            await self._after_save(is_new)

        return self

    def __repr__(self) -> str:
        attributes = ["%s=%r" % (a, getattr(self, a)) for a in self._fields]
        return "%s(\n    %s\n)" % (self.__class__.__name__, ",\n    ".join(attributes))

    def __eq__(self: "BaseModel", other: "BaseModel") -> bool:
        if self.__class__ != other.__class__:
            return False
        for field in self._fields:
            if hasattr(self, field):
                if not hasattr(other, field):
                    return False
                if getattr(self, field) != getattr(other, field):
                    return False
            elif hasattr(other, field):
                return False
        return True

    def __ne__(self: "BaseModel", other: "BaseModel") -> bool:
        return not self.__eq__(other)

    async def to_dict_ext(self,
                          fields: Iterable[str] | None = None,
                          include_restricted: bool = False,
                          convert_id: bool = False) -> Dict[str, Any]:
        if fields is None:
            fields = self._fields.keys()

        result = {}
        for field_name in fields:
            descriptor = self._fields.get(field_name)
            if descriptor is not None:
                if descriptor.restricted and not include_restricted:
                    continue
                value = getattr(self, field_name)
                if field_name == "id" and convert_id:
                    field_name = "_id"
                if callable(value):
                    continue
            else:
                computed = self._computed_fields.get(field_name)
                if not computed:
                    continue
                value = getattr(self, field_name)()
                if computed.is_async:
                    value = await value
                if isinstance(value, ObjectsCursor):
                    value = [x.to_dict() for x in await value.all()]

            result[field_name] = value

        return result

    def to_dict(self, fields: Iterable[str] | None = None,
                include_restricted: bool = False,
                convert_id: bool = False) -> Dict[str, Any]:
        if fields is None:
            fields = self._fields.keys()
        field_descriptors = ((f, self._fields.get(f)) for f in fields)

        result = {}
        for field, descriptor in field_descriptors:
            if descriptor is None:
                continue
            if descriptor.restricted and not include_restricted:
                continue
            value = getattr(self, field)
            if callable(value):
                continue
            if field == "id" and convert_id:
                field = "_id"
            result[field] = value
        return result

    @classmethod
    def create(cls: Type[TBaseModel], **attrs: Any) -> TBaseModel:
        return cls(attrs)

    @classmethod
    def from_pydantic(cls: Type[TBaseModel], model: TPydanticModel) -> TBaseModel:
        return cls(model.dict(exclude_unset=True))

    @classmethod
    def _ctor(cls: Type[TBaseModel], attrs: dict[str, Any] | None, **kwargs: Any) -> TBaseModel:
        """
        This method must be passed as a constructor to ObjectsCursor instead of the class itself
        By default, it does the same that the __init__() would do, however it does additional things
        for Submodels to instantiate a different (final Submodel) class
        """
        return cls(attrs, **kwargs)

    @staticmethod
    def __get_possible_databases() -> list["Shard"]:
        return [ctx.db.meta]

    @classmethod
    async def ensure_indexes(cls, loud: bool = False, overwrite: bool = False) -> None:
        dbs = cls.__get_possible_databases()
        for index in cls._indexes:
            for _db in dbs:
                try:
                    await _db.conn[cls.collection].create_index(index.keys, **index.options)
                except OperationFailure as e:
                    details = e.details
                    if details is not None:
                        code = details.get("code")
                        code_name = details.get("codeName")
                        if code == 85 or code_name == "IndexOptionsConflict":
                            if overwrite:
                                if loud:
                                    ctx.log.debug("Dropping index %s as conflicting", index.keys)
                                await _db.conn[cls.collection].drop_index(index.keys)
                                if loud:
                                    ctx.log.debug(
                                        "Creating index with options: %s, %s", index.keys, index.options
                                    )
                                await _db.conn[cls.collection].create_index(index.keys, **index.options)
                            else:
                                ctx.log.error(
                                    "Index %s conflicts with an existing one, use overwrite param to fix it",
                                    index.keys,
                                )

    def _reload_from_model(self: TBaseModel, obj: TBaseModel) -> None:
        for field in self._fields:
            if field == "_id":
                continue
            value = getattr(obj, field)

            # setting via __dict__ will ignore descriptors
            setattr(self, field, value)

    @classmethod
    def exposed_fields(cls) -> List[str]:
        fields = cls.exposed_base_fields()
        fields.extend(cls._computed_fields.keys())
        return fields

    @classmethod
    def exposed_base_fields(cls) -> List[str]:
        return [field for field, descriptor in cls._fields.items() if not descriptor.restricted]
