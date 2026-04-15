import enum
from functools import wraps
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user


class Role(str, enum.Enum):
    officer = "officer"
    underwriter = "underwriter"
    admin = "admin"


def require_role(*roles: Role) -> Callable:
    """Dependency factory that checks the current user's role against allowed roles."""

    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "")
        if user_role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' is not authorized. Required: {[r.value for r in roles]}",
            )
        return current_user

    return role_checker
