from fastapi import APIRouter

from app.observability.metrics import Metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/")
async def get_metrics():
    return Metrics.get()
