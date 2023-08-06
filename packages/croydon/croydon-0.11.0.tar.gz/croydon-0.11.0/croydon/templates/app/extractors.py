from typing import Optional, Callable, Awaitable
from fastapi import Header, Depends, Request
from croydon.errors import AuthenticationError
from app.models import Token, User, Session


async def auth_token(authorization: Optional[str] = Header(default=None)) -> Optional[Token]:
    if authorization is None:
        return None

    parts = authorization.split(" ")
    if len(parts) != 2:
        return None
    token_type, token = parts
    if token_type != "Token":
        return None

    return await Token.cache_get(token)


def authenticated_user(required: bool = True) -> Callable[[Optional[Token]], Awaitable[Optional[User]]]:
    async def inner(token: Optional[Token] = Depends(auth_token)) -> Optional[User]:
        user: Optional[User] = None
        if token is not None:
            user = await token.user()
        if user is None and required:
            raise AuthenticationError()
        return user
    return inner


async def current_session(request: Request) -> Session:
    return request.state.session
