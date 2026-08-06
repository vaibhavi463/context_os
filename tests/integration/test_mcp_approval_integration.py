import pytest
from app.mcp_server.registry import tool_registry


def test_mcp_tool_catalog_and_rbac_scoping():
    # Test read tool discovery for ops_engineer role
    ops_tools = tool_registry.list_tools("ops_engineer")
    tool_names = [t["name"] for t in ops_tools]

    assert "search_customer_accounts" in tool_names
    assert "get_system_incident_status" in tool_names
    assert "lookup_github_issues" in tool_names
    assert "execute_account_remediation" in tool_names

    # Test read_only role restriction
    read_only_tools = tool_registry.list_tools("read_only")
    read_only_names = [t["name"] for t in read_only_tools]
    assert "execute_account_remediation" not in read_only_names
    assert "get_audit_history" not in read_only_names
