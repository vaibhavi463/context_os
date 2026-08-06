import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Annotated

from app.db.session import get_db
from app.domain.agents.orchestrator import agent_orchestrator
from app.infrastructure.security.dependencies import get_current_user
from app.models.domain_models import Investigation, InvestigationMessage, User
from app.schemas.investigations import (
    InvestigationCreate,
    InvestigationResponse,
    MessageCreate,
    MessageResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Investigation:
    inv = Investigation(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        title=payload.title,
        status="ACTIVE"
    )
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return inv


@router.get("", response_model=list[InvestigationResponse])
async def list_investigations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[Investigation]:
    stmt = (
        select(Investigation)
        .where(Investigation.tenant_id == current_user.tenant_id)
        .order_by(Investigation.created_at.desc())
    )
    invs = (await db.execute(stmt)).scalars().all()
    return list(invs)


@router.get("/{investigation_id}/messages", response_model=list[MessageResponse])
async def get_investigation_messages(
    investigation_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[InvestigationMessage]:
    stmt = (
        select(InvestigationMessage)
        .where(
            InvestigationMessage.investigation_id == investigation_id
        )
        .order_by(InvestigationMessage.created_at.asc())
    )
    msgs = (await db.execute(stmt)).scalars().all()
    return list(msgs)


@router.post("/{investigation_id}/stream")
async def stream_investigation_message(
    investigation_id: str,
    payload: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> StreamingResponse:
    stmt = select(Investigation).where(
        Investigation.id == investigation_id,
        Investigation.tenant_id == current_user.tenant_id
    )
    inv = (await db.execute(stmt)).scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found.")

    # Save user message
    user_msg = InvestigationMessage(
        investigation_id=inv.id,
        sender_type="USER",
        content=payload.content
    )
    db.add(user_msg)
    await db.commit()

    async def event_generator() -> AsyncGenerator[str, None]:
        # Run turn logic
        agent_res = await agent_orchestrator.run_investigation_turn(
            db=db,
            user=current_user,
            investigation=inv,
            user_query=payload.content
        )

        # Stream tokens
        words = agent_res.content.split()
        for word in words:
            data = json.dumps({"token": word + " "})
            yield f"event: token\ndata: {data}\n\n"
            await asyncio.sleep(0.02)

        # Stream citations event if present
        if agent_res.citations:
            data = json.dumps({"citations": agent_res.citations})
            yield f"event: citations\ndata: {data}\n\n"

        # Stream tool calls event if present
        if agent_res.tool_calls:
            data = json.dumps({"tool_calls": agent_res.tool_calls})
            yield f"event: tool_calls\ndata: {data}\n\n"

        # Save agent message
        agent_msg = InvestigationMessage(
            investigation_id=inv.id,
            sender_type="AGENT",
            content=agent_res.content,
            citations=agent_res.citations,
            tool_calls=agent_res.tool_calls,
            tokens_used=180,
            estimated_cost_usd=0.0001
        )
        db.add(agent_msg)
        await db.commit()

        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
