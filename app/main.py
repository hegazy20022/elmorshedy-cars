from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.logger import setup_logging
from app.core.database import init_db
from app.api.routes import (
    bookings_router,
    cars_router,
    conversations_router,
    control_router,
    dashboard_router,
    telegram_webhook_router,
    cache_router,
    dashboard_auth_router, 
    metrics_router,
    settings_router,
    car_images_router,
    sold_cars_router,
    purchase_requests_router,
    analytics_router,
)
from app.observability.health import router as health_router
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.middlewares.request_logger import RequestLoggerMiddleware
from app.middlewares.rate_limiter import RateLimitMiddleware

setup_logging()

app = FastAPI(title="Elmorshedy Cars Agent")

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

app.mount("/uploads",StaticFiles(directory="uploads"),name="uploads")
@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {
        "service": "Elmorshedy Cars Agent",
        "status": "running"
    }


app.include_router(health_router)
app.include_router(bookings_router)
app.include_router(cars_router)
app.include_router(conversations_router)
app.include_router(control_router)
app.include_router(dashboard_router)
app.include_router(telegram_webhook_router)
app.include_router(cache_router)
app.include_router(dashboard_auth_router)
app.include_router(metrics_router)
app.include_router(settings_router)
app.include_router(car_images_router)
app.include_router(purchase_requests_router)
app.include_router(sold_cars_router)
app.include_router(analytics_router)
