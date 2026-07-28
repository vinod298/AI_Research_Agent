from typing import AsyncGenerator, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.exceptions import ForbiddenException, UnauthorizedException
from src.core.security import decode_access_token, verify_password
from src.models.user import User
from src.repositories.user_repository import APIKeyRepository, UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> User:
    user_repo = UserRepository(db)

    # 1. API Key Auth
    if x_api_key:
        apikey_repo = APIKeyRepository(db)
        # Scan API keys
        keys = await apikey_repo.get_all()
        for k in keys:
            if verify_password(x_api_key, k.key_hash):
                user = await user_repo.get_by_id(k.user_id)
                if user and user.is_active:
                    return user
        raise UnauthorizedException("Invalid API Key.")

    # 2. Bearer JWT Auth
    if token:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Could not validate credentials.")

        user = await user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedException("User not found or inactive.")
        return user

    # 3. Default Guest User Fallback for seamless local testing
    guest_user = await user_repo.get_by_username("default_researcher")
    if not guest_user:
        guest_user = User(
            id="default_user_id",
            email="researcher@enterprise.ai",
            username="default_researcher",
            hashed_password="disabled",
            full_name="Enterprise Researcher",
            role="researcher",
            is_active=True
        )
        db.add(guest_user)
        await db.commit()
        await db.refresh(guest_user)
    return guest_user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin" and not user.is_superuser:
        raise ForbiddenException("Admin privileges required.")
    return user
