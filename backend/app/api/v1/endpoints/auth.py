import re
from typing import Annotated, Any

from app.core.config import settings
from app.db.session import get_db
from app.infrastructure.security.dependencies import get_current_user
from app.infrastructure.security.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.domain_models import Tenant, User
from app.schemas.auth import TokenResponse, UserRegister, UserResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])


def slugify(text: str) -> str:
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    # Check existing user
    user_stmt = select(User).where(User.email == payload.email)
    existing_user = (await db.execute(user_stmt)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists."
        )

    # Find or create tenant
    tenant_slug = slugify(payload.tenant_name)
    tenant_stmt = select(Tenant).where(Tenant.slug == tenant_slug)
    tenant = (await db.execute(tenant_stmt)).scalar_one_or_none()
    if not tenant:
        tenant = Tenant(name=payload.tenant_name, slug=tenant_slug)
        db.add(tenant)
        await db.flush()

    new_user = User(
        tenant_id=tenant.id,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    stmt = select(User).where(User.email == form_data.username, User.is_active == True)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",  # nosec B105
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    return current_user
