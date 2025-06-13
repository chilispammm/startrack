from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
import jwt
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM

    async def dispatch(self, request: Request, call_next):
        try:
            # Get token from Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header:
                token = auth_header.split(" ")[1] if " " in auth_header else auth_header
                try:
                    # Verify and decode token
                    payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                    request.state.user = payload.get("sub")
                    request.state.token = token
                except jwt.ExpiredSignatureError:
                    logger.warning("Expired token detected")
                    request.state.token_expired = True
                except jwt.InvalidTokenError:
                    logger.warning("Invalid token detected")
                    request.state.invalid_token = True

            response = await call_next(request)
            return response

        except Exception as e:
            logger.error(f"Session middleware error: {str(e)}")
            raise

    def create_token(self, user_id: str) -> str:
        """
        Create a new JWT token.
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user_id,
            "exp": expire
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify a JWT token.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
