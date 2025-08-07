from fastapi import APIRouter

from app.modules import rag_flow_router 

router = APIRouter(prefix="/api")

router.include_router(rag_flow_router)