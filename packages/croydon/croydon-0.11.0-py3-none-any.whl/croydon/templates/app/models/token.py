from typing import Optional
from croydon.models import StorableModel
from croydon.models.fields import StringField, DatetimeField, ReferenceField
from croydon.models.index import Index, IndexDirection, IndexKey
from croydon.util import now, uuid4_string
from .user import User


class Token(StorableModel):

    COLLECTION = "tokens"
    KEY_FIELD = "token"
    INDEXES = [
        Index(
            keys=[
                IndexKey("user_id", IndexDirection.ASCENDING),
                IndexKey("token_type", IndexDirection.ASCENDING),
            ]
        )
    ]

    token_type = StringField(default="auth", required=True, rejected=True)
    token = StringField(default=uuid4_string, required=True, rejected=True, unique=True)
    created_at = DatetimeField(default=now, required=True, rejected=True)
    updated_at = DatetimeField(default=now, required=True, rejected=True)
    description = StringField(default="")
    user_id: ReferenceField[User] = ReferenceField(
        reference_model=User,
        required=True,
        rejected=True,
        restricted=True
    )

    def touch(self):
        self.updated_at = now()

    async def user(self) -> Optional[User]:
        return await User.get(self.user_id)
