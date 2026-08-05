import pytest
from app.mcp_server.registry import tool_registry
from app.mcp_server.guards.rbac_guard import RBACScopeGuard
import app.mcp_server.tools  # noqa: register tools


def test_tool_registry_contains_6_tools() -> None:
    tools_ops = tool_registry.list_tools("ops_engineer")
    tool_names = [t["name"] for t in tools_ops]
    assert "search_customer_accounts" in tool_names
    assert "get_system_incident_status" in tool_names
    assert "execute_account_remediation" in tool_names


def test_rbac_scope_guard_denies_unprivileged_role() -> None:
    # read_only role attempting write tool execute_account_remediation
    with pytest.raises(Exception):
        RBACScopeGuard.validate_tool_access("execute_account_remediation", "read_only")


def test_rbac_scope_guard_allows_privileged_role() -> None:
    tool = RBACScopeGuard.validate_tool_access("execute_account_remediation", "ops_engineer")
    assert tool.name == "execute_account_remediation"
    assert tool.requires_approval is True
