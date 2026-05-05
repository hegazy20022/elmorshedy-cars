import logging

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.metrics import Metrics

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception:
            Metrics.inc_errors()
            logger.exception(
                "Unhandled error in API",
                extra={
                    "extra_data": {
                        "path": request.url.path,
                        "method": request.method,
                    }
                },
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "حصلت مشكلة مؤقتة في الخدمة"},
            )
