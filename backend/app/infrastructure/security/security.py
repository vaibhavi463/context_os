from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: str | dict[str, Any] | Any,
    tenant_id: str | None = None,
    role: str | None = None,
    expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if isinstance(subject, dict):
        sub_val = str(subject.get("sub", subject.get("id", "")))
        t_id = str(subject.get("tenant_id", tenant_id or "default"))
        r_val = str(subject.get("role", role or "ops_engineer"))
    else:
        sub_val = str(subject)
        t_id = str(tenant_id or "default")
        r_val = str(role or "ops_engineer")

    to_encode = {
        "exp": expire,
        "sub": sub_val,
        "tenant_id": t_id,
        "role": r_val,
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
