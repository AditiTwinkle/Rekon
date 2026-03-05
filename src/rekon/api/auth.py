"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from rekon.core.config import settings
from rekon.core.exceptions import AuthenticationError, AuthorizationError

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT (should be loaded from environment in production)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


class TokenData(BaseModel):
    """Token data model."""

    user_id: str
    email: str
    roles: list[str]


class User(BaseModel):
    """User model."""

    user_id: str
    email: str
    name: str
    roles: list[str]


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user.

    Args:
        token: JWT token

    Returns:
        Current user

    Raises:
        AuthenticationError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        name: str = payload.get("name")
        roles: list[str] = payload.get("roles", [])

        if user_id is None:
            raise AuthenticationError("Invalid token")

        token_data = TokenData(user_id=user_id, email=email, roles=roles)
    except JWTError:
        raise AuthenticationError("Invalid token")

    return User(user_id=user_id, email=email, name=name, roles=roles)


def require_role(required_roles: list[str]):
    """Require specific roles.

    Args:
        required_roles: List of required roles

    Returns:
        Dependency function
    """

    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        """Check if user has required role.

        Args:
            current_user: Current user

        Returns:
            Current user

        Raises:
            AuthorizationError: If user doesn't have required role
        """
        if not any(role in current_user.roles for role in required_roles):
            raise AuthorizationError(
                f"User does not have required role. Required: {required_roles}"
            )
        return current_user

    return check_role


def create_access_token(
    user_id: str,
    email: str,
    name: str,
    roles: list[str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token.

    Args:
        user_id: User ID
        email: User email
        name: User name
        roles: User roles
        expires_delta: Token expiration time

    Returns:
        JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode = {
        "sub": user_id,
        "email": email,
        "name": name,
        "roles": roles,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
