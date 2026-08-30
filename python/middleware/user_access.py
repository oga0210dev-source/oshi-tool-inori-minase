from starlette.middleware.base import BaseHTTPMiddleware

from python.core.auth import update_last_access


class UserAccessMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        response = await call_next(request)

        update_last_access(request)

        return response
