import uuid
from app.mcp_server.approval_gate import approval_gate


def test_approval_token_signature_and_verification() -> None:
    requester_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    tool_name = "execute_account_remediation"
    tool_args = {"account_id": "ACC-100", "action_type": "RESET_RATE_LIMIT"}

    token = approval_gate.create_approval_token(
        requester_id=requester_id,
        tenant_id=tenant_id,
        tool_name=tool_name,
        tool_args=tool_args
    )
    assert isinstance(token, str)

    # Valid verification
    assert approval_gate.verify_approval_token(token, tool_name, tool_args) is True

    # Invalid tool name
    assert approval_gate.verify_approval_token(token, "wrong_tool", tool_args) is False

    # Forged arguments
    assert approval_gate.verify_approval_token(token, tool_name, {"account_id": "ACC-999"}) is False
