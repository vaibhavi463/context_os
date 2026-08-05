import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field(..., min_length=10)
    file_type: str = Field("text/markdown", max_length=50)
    source_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentChunkResponse(BaseModel):
    id: uuid.UUID
    chunk_index: int
    content: str
    metadata: dict[str, Any]

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    source_url: str | None
    content_hash: str
    file_type: str
    metadata_json: dict[str, Any]
    chunk_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
