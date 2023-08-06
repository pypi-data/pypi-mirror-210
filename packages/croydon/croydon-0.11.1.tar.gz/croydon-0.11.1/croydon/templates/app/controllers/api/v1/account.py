from fastapi import APIRouter, Depends, Body
from croydon import ctx
from croydon.errors import AuthenticationError, BadRequest
from app.extractors import authenticated_user, current_session
from app.models import User, Session
from .response_types.account import AccountMeResponse, LogoutResponse, AuthenticationRequest

account_ctrl = APIRouter(prefix="/api/v1/account")


@account_ctrl.get("/me")
async def me(user: User = Depends(authenticated_user())) -> AccountMeResponse:
    return AccountMeResponse(**user.to_dict())


@account_ctrl.post("/authenticate")
async def authenticate(
        auth_request: AuthenticationRequest = Body(),
        session: Session = Depends(current_session)) -> AccountMeResponse:

    user = await session.user()
    if user:
        raise BadRequest("already authenticated")

    user = await User.get(auth_request.username)
    if user is None or not user.check_password(auth_request.password):
        raise AuthenticationError()
    session.user_id = user.id

    return AccountMeResponse(**user.to_dict())


@account_ctrl.post("/logout")
async def logout(session: Session = Depends(current_session)) -> LogoutResponse:
    session.user_id = None
    return LogoutResponse(detail="logged out")
