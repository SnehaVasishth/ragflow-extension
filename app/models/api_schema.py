from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class RawFlowProcessChunks(BaseModel):
    s3URL: str
    tenantId: str
    chunkingMethod:str = None
    chunkingTokenSize:str = None
    chunkingLayout:str = None
    outputFile:str = None