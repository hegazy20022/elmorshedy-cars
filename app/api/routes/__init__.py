from .bookings import router as bookings_router
from .cars import router as cars_router
from .conversations import router as conversations_router
from .control import router as control_router
from .dashboard import router as dashboard_router
from .telegram_webhook import router as telegram_webhook_router
from .cache import router as cache_router
from .dashboard_auth import router as dashboard_auth_router
from .metrics import router as metrics_router
from .settings import router as settings_router
from .car_images import router as car_images_router
from .sold_cars import router as sold_cars_router
from .purchase_requests import router as purchase_requests_router
from .analytics import router as analytics_router

__all__ = [
    "bookings_router",
    "cars_router",
    "conversations_router",
    "control_router",
    "dashboard_router",
    "telegram_webhook_router",
    "cache_router",
    "dashboard_auth_router",
    "metrics_router",
    "settings_router",
    "car_images_router",
    "sold_cars_router",
    "purchase_requests_router",
    "analytics_router",
]
