import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(APPROVE|REJECT)$")


class PendingApprovalResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    investigation_id: uuid.UUID
    requester_id: uuid.UUID
    approver_id: uuid.UUID | None
    tool_name: str
    tool_arguments: dict[str, Any]
    status: str
    approval_token: str
    expires_at: datetime
    decided_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
