from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("request_logger")
        self.logger.setLevel(logging.INFO)

    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        
        # Log request details
        self.logger.info(
            f"Request: {request.method} {request.url.path}"
            f" - IP: {request.client.host}"
            f" - Headers: {dict(request.headers)}"
        )

        try:
            response = await call_next(request)
            
            # Log response details
            response_time = datetime.now() - start_time
            self.logger.info(
                f"Response: {request.method} {request.url.path}"
                f" - Status: {response.status_code}"
                f" - Time: {response_time.total_seconds():.2f}s"
            )
            
            return response

        except Exception as e:
            # Log error
            self.logger.error(
                f"Error: {request.method} {request.url.path}"
                f" - Error: {str(e)}"
            )
            raise

    def format_request(self, request: Request) -> Dict:
        """Format request details for logging"""
        return {
            "method": request.method,
            "path": request.url.path,
            "ip": request.client.host,
            "headers": dict(request.headers),
            "timestamp": datetime.now().isoformat()
        }

    def format_response(self, response: Response) -> Dict:
        """Format response details for logging"""
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "timestamp": datetime.now().isoformat()
        }
