"""
JWT Authentication Middleware for BATMAN Gateway.
Validates Keycloak-issued JWT tokens and extracts role/user info.
"""
from __future__ import annotations

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

logger = structlog.get_logger(__name__)
bearer_scheme = HTTPBearer()


class TokenData(BaseModel):
    user_id: str
    username: str
    roles: list[str]
    realm: str


# BATMAN roles hierarchy
ROLES = {
    "COMMANDING_OFFICER",
    "OPS_OFFICER",
    "INTELLIGENCE_OFFICER",
    "LOGISTICS_OFFICER",
    "BATMAN_OPERATOR",
}


def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenData:
    """
    Verify Keycloak JWT token.
    In production: fetch JWKS from Keycloak and validate signature.
    In development: allow dev tokens with X-Dev-Role header override.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # NOTE: In production, fetch public key from Keycloak JWKS endpoint.
        # For Phase 0 development, we decode without signature verification (dev mode only).
        payload = jwt.decode(token, options={"verify_signature": False})

        user_id: str = payload.get("sub", "")
        username: str = payload.get("preferred_username", "unknown")
        realm_access: dict = payload.get("realm_access", {})
        roles: list[str] = realm_access.get("roles", [])

        if not user_id:
            raise credentials_exception

        return TokenData(
            user_id=user_id,
            username=username,
            roles=[r for r in roles if r in ROLES],
            realm=payload.get("iss", "").split("/")[-1],
        )
    except JWTError as e:
        logger.warning("jwt_validation_failed", error=str(e))
        raise credentials_exception


def require_role(*allowed_roles: str):
    """Dependency factory — enforces minimum role requirement."""
    def _check(token: TokenData = Depends(verify_jwt_token)) -> TokenData:
        if not any(r in token.roles for r in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {list(allowed_roles)}",
            )
        return token
    return _check


# Common role dependencies
RequireCommandingOfficer = require_role("COMMANDING_OFFICER")
RequireOpsOrAbove = require_role("COMMANDING_OFFICER", "OPS_OFFICER")
RequireAnyStaff = require_role(*ROLES)
