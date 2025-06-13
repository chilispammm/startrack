from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "object-src 'none'"
            ),
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "speaker=(), "
                "vibrate=(), "
                "fullscreen=()"
            )
        }

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Add security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            return response

        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            raise

    def customize_headers(self, headers: Dict[str, str]) -> None:
        """
        Customize security headers.
        """
        self.security_headers.update(headers)

    def remove_header(self, header: str) -> None:
        """
        Remove a security header.
        """
        if header in self.security_headers:
            del self.security_headers[header]
