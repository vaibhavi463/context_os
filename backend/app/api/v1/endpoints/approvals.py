from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.infrastructure.security.dependencies import get_current_user, RequireRole
from app.models.domain_models import PendingApproval, AuditLog, User
from app.schemas.approvals import ApprovalDecisionRequest, PendingApprovalResponse

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("/pending", response_model=list[PendingApprovalResponse])
async def list_pending_approvals(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[PendingApproval]:
    stmt = (
        select(PendingApproval)
        .where(
            PendingApproval.tenant_id == current_user.tenant_id,
            PendingApproval.status == "PENDING"
        )
        .order_by(PendingApproval.created_at.desc())
    )
    approvals = (await db.execute(stmt)).scalars().all()
    return list(approvals)


@router.post("/{approval_id}/decide", response_model=PendingApprovalResponse)
async def decide_approval(
    approval_id: str,
    payload: ApprovalDecisionRequest,
    current_user: Annotated[User, Depends(RequireRole(["ops_engineer", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PendingApproval:
    stmt = select(PendingApproval).where(
        PendingApproval.id == approval_id,
        PendingApproval.tenant_id == current_user.tenant_id
    )
    approval = (await db.execute(stmt)).scalar_one_or_none()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending approval request not found."
        )

    if approval.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval request is already in status '{approval.status}'."
        )

    if datetime.now(timezone.utc) > approval.expires_at:
        approval.status = "EXPIRED"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval request has expired."
        )

    new_status = "APPROVED" if payload.decision == "APPROVE" else "REJECTED"
    approval.status = new_status
    approval.approver_id = current_user.id
    approval.decided_at = datetime.now(timezone.utc)

    # Record Audit Log
    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        action=f"HITL_APPROVAL_{new_status}",
        resource_type="pending_approvals",
        resource_id=str(approval.id),
        correlation_id=approval.idempotency_key,
        payload={"tool_name": approval.tool_name, "decision": new_status}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(approval)
    return approval
