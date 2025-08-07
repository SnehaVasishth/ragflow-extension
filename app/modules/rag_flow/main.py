"""
Example code for a FastAPI module that handles product management.
This code includes CRUD operations for products, including creating, reading, updating, and deleting products.
Remove this code if it's not relevant to your project.
"""

from fastapi import APIRouter, HTTPException, Depends, Request

from app.models.api_schema import RawFlowProcessChunks

from .manager import Manager
from app.schemas import APIResponseBase

router = APIRouter(
    prefix="/rag-flow",
    tags=["RagFlow"],
)


@router.post("/chunks/process")
async def process_chunks(request: Request, data: RawFlowProcessChunks):
    try:
        result = await Manager(request, data).process_chunks()
        return APIResponseBase(responseData=result, message="Fetch Chunks executed successfully.")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))