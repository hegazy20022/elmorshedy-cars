import time
from collections import defaultdict, deque

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.storage: dict[str, deque] = defaultdict(deque)

    def _get_client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in ("/health",):
            return await call_next(request)

        client_key = self._get_client_key(request)
        now = time.time()
        q = self.storage[client_key]

        while q and now - q[0] > self.window_seconds:
            q.popleft()

        if len(q) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "تم تجاوز الحد المسموح من الطلبات مؤقتًا حاول مرة أخرى بعد قليل"
                },
            )

        q.append(now)
        return await call_next(request)
