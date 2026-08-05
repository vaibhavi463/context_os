from typing import Any
from pydantic import BaseModel, Field

from app.mcp_server.approval_gate import approval_gate
from app.mcp_server.registry import MCPTool, tool_registry


# 1. execute_account_remediation
class ExecuteAccountRemediationInput(BaseModel):
    account_id: str = Field(..., description="Target Account ID")
    action_type: str = Field(..., pattern="^(RESET_RATE_LIMIT|CLEAR_LOCKOUT|FLUSH_CACHE)$")
    approval_token: str | None = Field(None, description="Cryptographically signed HITL approval token")


async def execute_account_remediation_executor(args: dict[str, Any]) -> dict[str, Any]:
    parsed = ExecuteAccountRemediationInput(**args)
    if not parsed.approval_token:
        return {
            "status": "PENDING_APPROVAL",
            "message": "Write operation 'execute_account_remediation' requires human operator approval."
        }

    is_valid = approval_gate.verify_approval_token(
        token=parsed.approval_token,
        tool_name="execute_account_remediation",
        tool_args={"account_id": parsed.account_id, "action_type": parsed.action_type}
    )
    if not is_valid:
        return {
            "status": "REJECTED",
            "error": "Invalid, forged, or expired approval token."
        }

    return {
        "status": "SUCCESS",
        "action": parsed.action_type,
        "account_id": parsed.account_id,
        "message": f"Successfully performed {parsed.action_type} on account {parsed.account_id}."
    }


# 2. update_ticket_status
class UpdateTicketStatusInput(BaseModel):
    ticket_id: str = Field(..., description="Support Ticket ID (e.g. TICKET-9921)")
    new_status: str = Field(..., pattern="^(ESCALATED|RESOLVED|IN_PROGRESS)$")
    reason: str = Field(..., min_length=5, description="Reason for updating status")
    approval_token: str | None = Field(None, description="Cryptographically signed HITL approval token")


async def update_ticket_status_executor(args: dict[str, Any]) -> dict[str, Any]:
    parsed = UpdateTicketStatusInput(**args)
    if not parsed.approval_token:
        return {
            "status": "PENDING_APPROVAL",
            "message": "Write operation 'update_ticket_status' requires human operator approval."
        }

    is_valid = approval_gate.verify_approval_token(
        token=parsed.approval_token,
        tool_name="update_ticket_status",
        tool_args={"ticket_id": parsed.ticket_id, "new_status": parsed.new_status, "reason": parsed.reason}
    )
    if not is_valid:
        return {
            "status": "REJECTED",
            "error": "Invalid, forged, or expired approval token."
        }

    return {
        "status": "SUCCESS",
        "ticket_id": parsed.ticket_id,
        "new_status": parsed.new_status,
        "message": f"Ticket {parsed.ticket_id} updated to {parsed.new_status}."
    }


def register_write_tools() -> None:
    tool_registry.register(
        MCPTool(
            name="execute_account_remediation",
            description="Perform state-changing remediation on a customer account (reset rate limit, clear lockout).",
            required_scope="ops:write",
            requires_approval=True,
            input_schema=ExecuteAccountRemediationInput,
            executor=execute_account_remediation_executor
        )
    )

    tool_registry.register(
        MCPTool(
            name="update_ticket_status",
            description="Escalate, resolve, or update support ticket status.",
            required_scope="support:write",
            requires_approval=True,
            input_schema=UpdateTicketStatusInput,
            executor=update_ticket_status_executor
        )
    )
