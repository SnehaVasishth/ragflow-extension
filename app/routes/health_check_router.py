
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.common.constants import SERVICE_STATUS_HTML

health_check_router = APIRouter(tags=["Health Check"])

@health_check_router.get("/")
async def root():
    return HTMLResponse(content=SERVICE_STATUS_HTML, status_code=200)

@health_check_router.get("/health")
async def health():
    return {"status": "ok"}
