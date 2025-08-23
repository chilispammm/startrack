from typing import Any, Dict, Optional, Union
from fastapi.responses import JSONResponse, Response
from fastapi import status
import json

class APIResponse(JSONResponse):
    """Custom API response formatter"""
    
    def __init__(
        self,
        success: bool = True,
        data: Optional[Union[dict, list, str]] = None,
        message: str = "",
        status_code: int = status.HTTP_200_OK,
        **kwargs
    ):
        content = {
            "success": success,
            "message": message,
            "data": data or {}
        }
        
        # Add any additional fields to the response
        content.update(kwargs)
        
        super().__init__(
            content=content,
            status_code=status_code
        )
        
        # Set content type header
        self.media_type = "application/json"


def error_response(
    message: str = "An error occurred",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_details: Optional[Dict[str, Any]] = None,
) -> APIResponse:
    """Helper function to create error responses"""
    return APIResponse(
        success=False,
        message=message,
        status_code=status_code,
        error=error_details or {}
    )

def success_response(
    data: Optional[Union[dict, list]] = None,
    message: str = "Operation successful",
    status_code: int = status.HTTP_200_OK,
    **kwargs
) -> APIResponse:
    """Helper function to create success responses"""
    return APIResponse(
        success=True,
        data=data,
        message=message,
        status_code=status_code,
        **kwargs
    )

def image_response(
    image_data: bytes,
    media_type: str = "image/png"
) -> Response:
    """Helper function to create image responses"""
    return Response(
        content=image_data,
        media_type=media_type,
        headers={"Cache-Control": "max-age=3600"}  # Cache for 1 hour
    )
