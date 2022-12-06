import logging

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from fastapi_sqlalcmemy.extension import session_ctx

logger = logging.getLogger(__name__)


def init_middleware(app: FastAPI):
    """"""
    app.add_middleware(DBMiddleware)


class DBMiddleware(BaseHTTPMiddleware):
    @session_ctx
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        return response
