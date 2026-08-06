import pytest
from app.infrastructure.security.security import create_access_token, decode_token, get_password_hash, verify_password


@pytest.mark.asyncio
async def test_auth_token_generation_and_decoding():
    user_data = {"sub": "user_id_101", "role": "ops_engineer", "tenant_id": "tenant_enterprise_01"}
    token = create_access_token(user_data)
    assert token is not None

    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_id_101"
    assert decoded["role"] == "ops_engineer"
    assert decoded["tenant_id"] == "tenant_enterprise_01"


def test_password_hashing_and_verification():
    raw_pass = "P@ssw0rdSecure!2026"
    hashed = get_password_hash(raw_pass)
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPass", hashed) is False
