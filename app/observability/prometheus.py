from fastapi import APIRouter

router = APIRouter(tags=["observability"])


@router.get("/metrics")
async def metrics():

    return {
        "message": "Prometheus metrics not configured yet"
    }
