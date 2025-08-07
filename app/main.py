from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import health_check_router, router
from app.utils.logger import logger
from app.utils.utils import format_json_response


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check_router)
app.include_router(router)


@app.exception_handler(Exception)
async def exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled error: {exc}", exc_info=exc)
    return format_json_response(message=str(exc), success=False, status_code=500)

@app.exception_handler(HTTPException)
async def exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    logger.error(f"HTTPException: {exc.detail}")

    status_code = exc.status_code if isinstance(exc.status_code, int) else 500  
    return format_json_response(
        message=str(exc.detail) if exc.detail else str(exc),
        status_code=status_code,
        success=False,
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        field = error["loc"][-1]
        message = error["msg"]
        errors.append({"field": field, "message": message})

    return format_json_response(errors, message="Invalid request", status_code=400, success=False)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True)