from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

def to_serializable(obj: Any) -> Any:
    """
    Recursively converts Pydantic model instances to standard dictionaries
    and maps nested attributes to JSON-serializable types.
    """
    if isinstance(obj, BaseModel):
        return to_serializable(obj.model_dump())
    if isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    if isinstance(obj, dict):
        return {key: to_serializable(val) for key, val in obj.items()}
    return jsonable_encoder(obj)

def success_response(
    data: Any = None, 
    message: str = "Operation completed successfully", 
    status_code: int = 200
) -> JSONResponse:
    """
    Generates a standardized JSON response format for successful API actions.
    Conforms to: {"success": true, "message": message, "data": data}
    """
    content = {
        "success": True,
        "message": message,
        "data": to_serializable(data)
    }
    return JSONResponse(
        status_code=status_code,
        content=content
    )

def error_response(
    code: str = "BAD_REQUEST", 
    message: str = "An error occurred during execution", 
    status_code: int = 400,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Generates a standardized JSON response format for failed API actions.
    Conforms to: {"success": false, "message": message, "error_code": code}
    """
    content = {
        "success": False,
        "message": message,
        "error_code": code,
        "error": {
            "code": code,
            "message": message
        }
    }
    if request_id:
        content["error"]["request_id"] = request_id
        
    return JSONResponse(
        status_code=status_code,
        content=to_serializable(content)
    )
