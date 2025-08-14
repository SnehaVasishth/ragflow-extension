from typing import Any
from fastapi.responses import JSONResponse

def format_json_response(
    data: Any = None,
    message: Any = "Operation successful",
    success: bool = True,
    status_code: int = 200, 
) -> JSONResponse:
    response_content = {
        "responseData": data,
        "message": message,
        "success": success,
        "responseCode": status_code,
    }
    return JSONResponse(status_code=status_code, content=response_content)