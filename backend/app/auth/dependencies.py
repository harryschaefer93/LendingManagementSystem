import json

from fastapi import Depends, HTTPException, Request, status

from app.config import settings

DEFAULT_MOCK_USER = {
    "id": "officer-1",
    "name": "Jane Smith",
    "role": "officer",
}


async def get_current_user(request: Request) -> dict:
    """
    Auth dependency.
    - In mock mode: reads X-Mock-User header or returns default mock user.
    - In entra mode: validates JWT from Authorization header (to be implemented).
    """
    if settings.AUTH_MODE == "mock":
        mock_header = request.headers.get("X-Mock-User")
        if mock_header:
            try:
                user = json.loads(mock_header)
                if not all(k in user for k in ("id", "name", "role")):
                    raise ValueError("Missing required fields")
                return user
            except (json.JSONDecodeError, ValueError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid X-Mock-User header. Expected JSON with id, name, role.",
                )
        return DEFAULT_MOCK_USER.copy()

    # --------------------------------------------------------------------------
    # Entra ID JWT Validation (activate when AUTH_MODE="entra")
    # --------------------------------------------------------------------------
    # from jose import jwt, JWTError
    # import httpx
    #
    # auth_header = request.headers.get("Authorization")
    # if not auth_header or not auth_header.startswith("Bearer "):
    #     raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    #
    # token = auth_header.split(" ", 1)[1]
    #
    # # Fetch JWKS from Microsoft
    # jwks_url = f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}/discovery/v2.0/keys"
    # async with httpx.AsyncClient() as client:
    #     resp = await client.get(jwks_url)
    #     jwks = resp.json()
    #
    # try:
    #     payload = jwt.decode(
    #         token,
    #         jwks,
    #         algorithms=["RS256"],
    #         audience=settings.ENTRA_CLIENT_ID,
    #         issuer=f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}/v2.0",
    #     )
    #     return {
    #         "id": payload.get("oid", payload.get("sub")),
    #         "name": payload.get("name", "Unknown"),
    #         "role": payload.get("roles", ["officer"])[0],
    #     }
    # except JWTError as e:
    #     raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    # --------------------------------------------------------------------------

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Unsupported AUTH_MODE: {settings.AUTH_MODE}",
    )
