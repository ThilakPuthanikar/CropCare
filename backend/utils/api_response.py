from typing import Any, List, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class APIResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    detail: Optional[str] = None  # Preserved for backward compatibility


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = 200,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "message": message, "data": data, "errors": None},
    )


def error_response(
    message: str = "An error occurred",
    errors: Optional[List[str]] = None,
    status_code: int = 400,
    detail: Optional[str] = None,
) -> JSONResponse:
    if detail is None:
        detail = message
    if errors is None:
        errors = [message]
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "detail": detail,  # Preserved for backward compatibility with existing frontend
            "data": None,
            "errors": errors,
        },
    )
