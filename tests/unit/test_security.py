import uuid
from app.infrastructure.security.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token
)


def test_password_hashing() -> None:
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_encoding_and_decoding() -> None:
    user_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    role = "ops_engineer"

    token = create_access_token(subject=user_id, tenant_id=tenant_id, role=role)
    assert isinstance(token, str)

    payload = decode_token(token)
    assert payload is not None
    assert payload.get("sub") == user_id
    assert payload.get("tenant_id") == tenant_id
    assert payload.get("role") == role
    assert payload.get("type") == "access"
