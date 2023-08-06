from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response
from croydon import ctx
from app.models.session import Session


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        session_key = ctx.cfg.session.cookie
        session_id = request.cookies.get(session_key)
        need_cookie = session_id is None
        session: Optional[Session] = None

        if session_id is not None:
            session = await Session.cache_get(session_id)

        if session is None:
            session = Session()
            need_cookie = True
            await session.save()

        request.state.session = session
        response = await call_next(request)

        if request.state.session.is_modified():
            try:
                await request.state.session.save()
            except Exception as e:
                ctx.log.error(f"can't save session: {e}")

        if need_cookie:
            response.set_cookie(ctx.cfg.session.cookie, session.key)
        return response
