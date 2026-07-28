from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import DuplicateEntityException, UnauthorizedException
from src.core.security import create_access_token, generate_api_key, get_password_hash, verify_password
from src.models.user import User, APIKey
from src.repositories.user_repository import UserRepository, APIKeyRepository
from src.schemas.auth import TokenResponse, UserLogin, UserRegister


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.user_repo = UserRepository(db_session)
        self.apikey_repo = APIKeyRepository(db_session)

    async def register_user(self, schema: UserRegister) -> User:
        existing_email = await self.user_repo.get_by_email(schema.email)
        if existing_email:
            raise DuplicateEntityException("User", "email", schema.email)

        existing_username = await self.user_repo.get_by_username(schema.username)
        if existing_username:
            raise DuplicateEntityException("User", "username", schema.username)

        user = User(
            email=schema.email,
            username=schema.username,
            hashed_password=get_password_hash(schema.password),
            full_name=schema.full_name,
            role=schema.role
        )
        return await self.user_repo.create(user)

    async def login_user(self, schema: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_by_username_or_email(schema.username_or_email)
        if not user or not verify_password(schema.password, user.hashed_password):
            raise UnauthorizedException("Invalid username/email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive.")

        token = create_access_token(subject=user.id, role=user.role)
        return TokenResponse(
            access_token=token,
            expires_in_seconds=1440 * 60,
            user_id=user.id,
            role=user.role
        )

    async def create_api_key(self, user_id: str, name: str) -> Tuple[APIKey, str]:
        raw_key = generate_api_key(prefix="eai")
        key_hash = get_password_hash(raw_key)

        api_key = APIKey(
            name=name,
            prefix=raw_key[:7],
            key_hash=key_hash,
            user_id=user_id
        )
        saved = await self.apikey_repo.create(api_key)
        return saved, raw_key
