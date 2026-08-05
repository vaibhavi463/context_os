from typing import Any
from pydantic import BaseModel, Field
import httpx

from app.core.config import settings
from app.mcp_server.registry import MCPTool, tool_registry


# 1. search_customer_accounts
class SearchCustomerAccountsInput(BaseModel):
    account_id: str = Field(..., description="Customer Account ID or Organization Slug")


async def search_customer_accounts_executor(args: dict[str, Any]) -> dict[str, Any]:
    parsed = SearchCustomerAccountsInput(**args)
    # Simulated database lookup
    return {
        "account_id": parsed.account_id,
        "company_name": f"Enterprise Org {parsed.account_id}",
        "subscription_tier": "ENTERPRISE_PREMIUM",
        "status": "ACTIVE",
        "rate_limit_exceeded": True,
        "current_rpm": 4500,
        "allowed_rpm": 3000,
        "account_owner": "owner@enterprise.io"
    }


# 2. get_system_incident_status
class GetSystemIncidentStatusInput(BaseModel):
    service_name: str | None = Field(None, description="Optional service name filter (e.g. database, api, worker)")


async def get_system_incident_status_executor(args: dict[str, Any]) -> dict[str, Any]:
    parsed = GetSystemIncidentStatusInput(**args)
    incidents = [
        {
            "incident_id": "INC-8892",
            "service": "database",
            "severity": "HIGH",
            "status": "DEGRADED_PERFORMANCE",
            "message": "High CPU utilization on DB Primary Pool due to unindexed vector search query spikes.",
            "started_at": "2026-08-05T22:15:00Z"
        },
        {
            "incident_id": "INC-8893",
            "service": "api",
            "severity": "MEDIUM",
            "status": "RATE_LIMITED",
            "message": "Rate limit bucket overflow for Tenant org_enterprise_01.",
            "started_at": "2026-08-05T22:40:00Z"
        }
    ]
    if parsed.service_name:
        incidents = [i for i in incidents if i["service"] == parsed.service_name]

    return {"active_incidents": incidents, "count": len(incidents)}


# 3. lookup_github_issues
class LookupGithubIssuesInput(BaseModel):
    query: str = Field(..., description="Search keyword or error signature (e.g. 'connection pool exhausted')")
    repo: str = Field("vaibhavi463/context_os", description="GitHub Repository in owner/repo format")


async def lookup_github_issues_executor(args: dict[str, Any]) -> dict[str, Any]:
    parsed = LookupGithubIssuesInput(**args)
    if settings.GITHUB_TOKEN:
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {settings.GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
                url = f"https://api.github.com/search/issues?q=repo:{parsed.repo}+{parsed.query}"
                resp = await client.get(url, headers=headers, timeout=5.0)
                if resp.status_code == 200:
                    data = resp.json()
                    items = [
                        {
                            "number": item["number"],
                            "title": item["title"],
                            "state": item["state"],
                            "html_url": item["html_url"],
                            "created_at": item["created_at"]
                        }
                        for item in data.get("items", [])[:5]
                    ]
                    return {"repository": parsed.repo, "issues": items}
        except Exception:
            pass

    # Mock fallback
    return {
        "repository": parsed.repo,
        "issues": [
            {
                "number": 42,
                "title": f"Fix connection pool leak under high concurrency: {parsed.query}",
                "state": "open",
                "html_url": f"https://github.com/{parsed.repo}/issues/42",
                "created_at": "2026-08-04T10:00:00Z"
            }
        ]
    }


# 4. get_audit_history
class GetAuditHistoryInput(BaseModel):
    resource_id: str = Field(..., description="Target Resource ID or Correlation ID")


async def get_audit_history_executor(args: dict[str, Any]) -> dict[str, Any]:
    parsed = GetAuditHistoryInput(**args)
    return {
        "resource_id": parsed.resource_id,
        "history": [
            {
                "action": "RATE_LIMIT_OVERRIDE",
                "actor": "admin@contextos.io",
                "timestamp": "2026-08-05T21:00:00Z",
                "status": "APPROVED"
            }
        ]
    }


def register_read_tools() -> None:
    tool_registry.register(
        MCPTool(
            name="search_customer_accounts",
            description="Lookup customer account subscription, tier, and rate limit status.",
            required_scope="ops:read",
            requires_approval=False,
            input_schema=SearchCustomerAccountsInput,
            executor=search_customer_accounts_executor
        )
    )

    tool_registry.register(
        MCPTool(
            name="get_system_incident_status",
            description="Retrieve active system incidents and service degradation reports.",
            required_scope="ops:read",
            requires_approval=False,
            input_schema=GetSystemIncidentStatusInput,
            executor=get_system_incident_status_executor
        )
    )

    tool_registry.register(
        MCPTool(
            name="lookup_github_issues",
            description="Search GitHub repository issues for error codes and bug reports.",
            required_scope="ops:read",
            requires_approval=False,
            input_schema=LookupGithubIssuesInput,
            executor=lookup_github_issues_executor
        )
    )

    tool_registry.register(
        MCPTool(
            name="get_audit_history",
            description="Retrieve past security and operational audit logs for a resource.",
            required_scope="admin:read",
            requires_approval=False,
            input_schema=GetAuditHistoryInput,
            executor=get_audit_history_executor
        )
    )
