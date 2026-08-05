import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.models.domain_models import PendingApproval, User
from app.mcp_server.registry import MCPTool


class ApprovalGate:
    @staticmethod
    def compute_args_hash(tool_args: dict[str, Any]) -> str:
        serialized = json.dumps(tool_args, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def create_approval_token(
        cls,
        requester_id: uuid.UUID,
        tenant_id: uuid.UUID,
        tool_name: str,
        tool_args: dict[str, Any],
        expires_minutes: int = 15
    ) -> str:
        args_hash = cls.compute_args_hash(tool_args)
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        payload = {
            "sub": str(requester_id),
            "tenant_id": str(tenant_id),
            "tool_name": tool_name,
            "args_hash": args_hash,
            "exp": expire,
            "type": "approval_token"
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @classmethod
    def verify_approval_token(cls, token: str, tool_name: str, tool_args: dict[str, Any]) -> bool:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("type") != "approval_token":
                return False
            if payload.get("tool_name") != tool_name:
                return False
            expected_hash = cls.compute_args_hash(tool_args)
            if payload.get("args_hash") != expected_hash:
                return False
            return True
        except JWTError:
            return False

    @classmethod
    async def create_pending_approval(
        cls,
        db: AsyncSession,
        user: User,
        investigation_id: uuid.UUID,
        tool: MCPTool,
        tool_args: dict[str, Any]
    ) -> PendingApproval:
        token = cls.create_approval_token(
            requester_id=user.id,
            tenant_id=user.tenant_id,
            tool_name=tool.name,
            tool_args=tool_args
        )
        idempotency_key = f"idemp_{uuid.uuid4()}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        pending = PendingApproval(
            tenant_id=user.tenant_id,
            investigation_id=investigation_id,
            requester_id=user.id,
            tool_name=tool.name,
            tool_arguments=tool_args,
            status="PENDING",
            approval_token=token,
            idempotency_key=idempotency_key,
            expires_at=expires_at
        )
        db.add(pending)
        await db.commit()
        await db.refresh(pending)
        return pending


approval_gate = ApprovalGate()
