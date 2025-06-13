from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "message": "Validation error",
                    "errors": {
                        "fields": e.errors()
                    }
                }
            )
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Validation error",
                    "errors": {
                        "fields": e.errors()
                    }
                }
            )
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "errors": {
                        "general": str(e)
                    }
                }
            )
