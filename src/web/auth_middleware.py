"""Authentication middleware and helpers for Twitch Drops Miner Web UI.

Supports HTTP Basic Authentication and session cookies via environment variables:
- WEB_USERNAME / AUTH_USERNAME / AUTH_USER
- WEB_PASSWORD / AUTH_PASSWORD / AUTH_PASS
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import secrets
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("TwitchDrops.auth")

# Read credentials from environment variables
WEB_USERNAME = (
    os.getenv("WEB_USERNAME")
    or os.getenv("AUTH_USERNAME")
    or os.getenv("AUTH_USER")
    or ""
).strip()

WEB_PASSWORD = (
    os.getenv("WEB_PASSWORD")
    or os.getenv("AUTH_PASSWORD")
    or os.getenv("AUTH_PASS")
    or ""
).strip()

AUTH_ENABLED = bool(WEB_USERNAME and WEB_PASSWORD)

# Generate an internal session secret for cookie signing
_SESSION_SECRET = hashlib.sha256(
    f"{WEB_USERNAME}:{WEB_PASSWORD}:tdm_session_secret".encode()
).hexdigest()
_COOKIE_NAME = "tdm_session"

if AUTH_ENABLED:
    logger.info("Web authentication is ENABLED for user: %s", WEB_USERNAME)
else:
    logger.info("Web authentication is DISABLED (WEB_USERNAME / WEB_PASSWORD not set)")


def get_session_token() -> str:
    """Generate a token for the session cookie."""
    return hmac.new(
        _SESSION_SECRET.encode(),
        f"{WEB_USERNAME}:authenticated".encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_session_token(token: str | None) -> bool:
    """Verify session cookie token."""
    if not token or not AUTH_ENABLED:
        return False
    expected = get_session_token()
    return secrets.compare_digest(token, expected)


def verify_basic_auth_header(auth_header: str | None) -> bool:
    """Verify Authorization header with Basic auth."""
    if not auth_header or not AUTH_ENABLED:
        return False
    try:
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "basic":
            return False
        decoded = base64.b64decode(parts[1]).decode("utf-8")
        if ":" not in decoded:
            return False
        username, password = decoded.split(":", 1)
        return secrets.compare_digest(username, WEB_USERNAME) and secrets.compare_digest(
            password, WEB_PASSWORD
        )
    except Exception:
        return False


def is_authenticated_socket(environ: dict) -> bool:
    """Check if a Socket.IO connection is authorized."""
    if not AUTH_ENABLED:
        return True

    # Check HTTP_AUTHORIZATION
    auth_header = environ.get("HTTP_AUTHORIZATION")
    if verify_basic_auth_header(auth_header):
        return True

    # Check cookies from HTTP_COOKIE
    cookie_str = environ.get("HTTP_COOKIE", "")
    for item in cookie_str.split(";"):
        item = item.strip()
        if item.startswith(f"{_COOKIE_NAME}="):
            token = item.split("=", 1)[1]
            if verify_session_token(token):
                return True

    # Check ASGI scope headers if present
    asgi_scope = environ.get("asgi.scope")
    if asgi_scope and "headers" in asgi_scope:
        for name, value in asgi_scope["headers"]:
            header_name = name.decode("latin1").lower()
            if header_name == "authorization":
                if verify_basic_auth_header(value.decode("latin1")):
                    return True
            elif header_name == "cookie":
                for item in value.decode("latin1").split(";"):
                    item = item.strip()
                    if item.startswith(f"{_COOKIE_NAME}="):
                        token = item.split("=", 1)[1]
                        if verify_session_token(token):
                            return True

    return False


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing HTTP Basic Auth if configured."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not AUTH_ENABLED:
            return await call_next(request)

        # Allow health checks without credentials
        path = request.url.path
        if path in ("/health", "/healthz", "/api/health"):
            return await call_next(request)

        # Allow local Docker healthcheck to /api/status from loopback
        client_host = request.client.host if request.client else ""
        if path == "/api/status" and client_host in ("127.0.0.1", "::1", "localhost"):
            return await call_next(request)

        # Check existing session cookie
        session_token = request.cookies.get(_COOKIE_NAME)
        if verify_session_token(session_token):
            return await call_next(request)

        # Check Basic Auth header
        auth_header = request.headers.get("authorization")
        if verify_basic_auth_header(auth_header):
            response = await call_next(request)
            # Set session cookie so subsequent requests / websockets stay authenticated
            response.set_cookie(
                key=_COOKIE_NAME,
                value=get_session_token(),
                path="/",
                httponly=True,
                samesite="lax",
            )
            return response

        # Unauthorized
        return Response(
            content="401 Unauthorized - Authentication Required",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Twitch Drops Miner"'},
            media_type="text/plain",
        )
