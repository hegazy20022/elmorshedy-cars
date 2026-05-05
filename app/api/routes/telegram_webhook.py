from fastapi import APIRouter

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.get("/webhook-status")
async def webhook_status():
    return {
        "configured": False,
        "message": "لسه ما تمش ضبط Telegram webhook URL"
    }
