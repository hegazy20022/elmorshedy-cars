from pydantic import BaseModel


class SuccessResponse(BaseModel):
    ok: bool = True
    message: str | None = None


class ErrorResponse(BaseModel):
    ok: bool = False
    detail: str
