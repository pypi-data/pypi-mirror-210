import bcrypt
from typing import TYPE_CHECKING, Optional
from croydon import ctx
from croydon.models import StorableModel
from croydon.models.fields import StringField, DatetimeField
from croydon.util import now
if TYPE_CHECKING:
    from .token import Token


class User(StorableModel):

    COLLECTION = "users"
    KEY_FIELD = "username"

    username = StringField(required=True, unique=True)
    first_name = StringField(default="")
    last_name = StringField(default="")
    email = StringField(default="", unique=True)
    password_hash = StringField(default="-", rejected=True, restricted=True)
    avatar_url = StringField(default="")
    created_at = DatetimeField(required=True, rejected=True, default=now)
    updated_at = DatetimeField(required=True, rejected=True, default=now)

    def set_password(self, password: str) -> None:
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                self.password_hash.encode("utf-8")
            )
        except ValueError as e:
            ctx.log.error(e)
            # password not set leads to bcrypt raising ValueError("invalid salt")
            return False

    async def create_token(self, *, description: Optional[str] = None) -> "Token":
        from .token import Token
        t = Token({"user_id": self.id, "description": description})
        await t.save()
        return t
