from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel
from . import ObjectIdStr


class AccountMeResponse(BaseModel):
    id: Optional[ObjectIdStr]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    ext_id: Optional[str]
    avatar_url: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class LogoutResponse(BaseModel):
    detail: Literal["logged out"] = "logged out"


class AuthenticationRequest(BaseModel):
    username: str
    password: str
