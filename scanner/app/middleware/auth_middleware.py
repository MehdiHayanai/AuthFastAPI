from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_jwt_token, create_token_payload, decode_jwt_token
from app.core.utils import get_current_datetime
from app.db.models.token import Token
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AutoRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip for non-authenticated routes
        api_version = settings.API_VERSION
        public_paths = [
            f"/api/{api_version}/auth/login",
            f"/api/{api_version}/auth/register",
            "/",
            "ping",
            "/health",
        ]
        if any(request.url.path.startswith(p) for p in public_paths):
            return await call_next(request)

        # Get the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)

        # Extract token
        token = auth_header.replace("Bearer ", "")

        # Get client info
        ip_address = request.client.host
        user_agent = request.headers.get("User-Agent", "")

        # Process the request first
        response = await call_next(request)

        # Only refresh if the request was successful
        if response.status_code < 400:
            # Get DB connection
            db = SessionLocal()

            try:
                # Decode token without verification to check expiration
                payload = decode_jwt_token(token)
                if not payload:
                    return response

                # Check if token is near expiration
                exp_timestamp = payload.get("exp", 0)
                current_timestamp = get_current_datetime().timestamp()
                remaining_time = exp_timestamp - current_timestamp
                total_lifetime = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
                threshold = total_lifetime * settings.TOKEN_REFRESH_THRESHOLD_PERCENT

                # If token is near expiration, refresh it
                if 0 < remaining_time < threshold:
                    user_id = int(payload.get("user_id"))

                    # Get existing token from database
                    db_token = db.query(Token).filter(Token.token == token).first()

                    if db_token:
                        # Create new token
                        new_payload = create_token_payload(
                            user_id,
                            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                        )
                        new_token = create_jwt_token(new_payload)

                        # Update token in database
                        new_expires_at = datetime.fromtimestamp(new_payload["exp"])
                        db_token.token = new_token
                        db_token.expires_at = new_expires_at
                        db_token.last_used_at = get_current_datetime()
                        db_token.ip_address = ip_address
                        db_token.user_agent = user_agent

                        db.commit()

                        # Add new token to response
                        response.headers["X-New-Token"] = new_token

            except Exception:
                # If any error occurs during token processing, continue with the response
                pass
            finally:
                db.close()

        return response
