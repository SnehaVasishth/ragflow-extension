from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")

class APIResponseBase(BaseModel, Generic[T]):
    responseData: T
    responseCode: int = 200
    success: bool = True
    message: str = "Operation successful"