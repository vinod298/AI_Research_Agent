from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.auth import APIKeyCreate, APIKeyResponse, TokenResponse, UserLogin, UserRegister, UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(schema: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new enterprise user."""
    service = AuthService(db)
    user = await service.register_user(schema)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(schema: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT access token."""
    service = AuthService(db)
    return await service.login_user(schema)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    schema: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new API key for the current user."""
    service = AuthService(db)
    apikey, raw_key = await service.create_api_key(current_user.id, schema.name)
    return APIKeyResponse(
        id=apikey.id,
        name=apikey.name,
        prefix=apikey.prefix,
        api_key=raw_key,
        created_at=apikey.created_at
    )
