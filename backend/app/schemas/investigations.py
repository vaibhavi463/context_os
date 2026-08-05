import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, Field


class InvestigationCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: uuid.UUID
    investigation_id: uuid.UUID
    sender_type: str
    content: str
    citations: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    tokens_used: int
    estimated_cost_usd: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class InvestigationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    status: str
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
