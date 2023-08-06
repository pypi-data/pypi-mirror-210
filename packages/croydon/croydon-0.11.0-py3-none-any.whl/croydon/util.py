from uuid import uuid4
from datetime import datetime
from bson.objectid import ObjectId, InvalidId


def uuid4_string() -> str:
    return str(uuid4())


def resolve_id(id_: str | ObjectId | None) -> ObjectId | str | None:
    # ObjectId(None) generates a new unique object id
    # We need to handle that case and return None instead
    if id_ is not None:
        if not isinstance(id_, ObjectId):
            try:
                objid_expr = ObjectId(id_)
                if str(objid_expr) == id_:
                    return objid_expr
            except (InvalidId, TypeError):
                pass
    return id_


# Mongo stores datetime rounded to milliseconds as its datetime
# capabilities are limited by v8 engine
def now() -> datetime:
    dt = datetime.utcnow()
    dt = dt.replace(microsecond=dt.microsecond // 1000 * 1000)
    return dt


NilObjectId: ObjectId = ObjectId("000000000000000000000000")
