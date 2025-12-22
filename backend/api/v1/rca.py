"""
RCA API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import uuid
import structlog

from database.session import get_db, AsyncSessionLocal
from database.models import RCASession, Agent, AgentMessage, Hypothesis, RCAReport
from orchestration.langgraph_orchestrator import rca_orchestrator
from core.cache import redis_client
from schemas.rca import (
    RCASessionCreate,
    RCASessionResponse,
    RCAStatusResponse,
    HypothesisResponse,
    AgentMessageResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/rca", tags=["RCA"])


@router.post("/submit", response_model=RCASessionResponse, status_code=202)
async def submit_rca(
    request: RCASessionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit new RCA request.
    
    Creates session and triggers multi-agent workflow in background.
    """
    session_id = str(uuid.uuid4())
    
    # Create session record
    session = RCASession(
        session_id=session_id,
        lot_id=request.lot_id,
        wafer_id=request.wafer_id,
        bin=request.bin,
        priority=request.priority,
        status="queued",
        created_by=request.user_id,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    logger.info(
        "rca_session_created",
        session_id=session_id,
        lot_id=request.lot_id,
        wafer_id=request.wafer_id,
    )
    
    # Trigger workflow in background
    background_tasks.add_task(execute_rca_workflow, session_id, request.dict())
    
    return RCASessionResponse(
        session_id=session_id,
        status="queued",
        message="RCA analysis queued successfully",
    )


@router.get("/status/{session_id}", response_model=RCAStatusResponse)
async def get_rca_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get RCA session status.
    
    Returns current status, progress, and active agents.
    """
    # Query session
    result = await db.execute(select(RCASession).where(RCASession.session_id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # For now, return static agent information (agents are not session-specific)
    # In production, you'd track agent execution state per session
    active_agents = []
    completed_agents = []
    progress = 0
    if session.status == "queued":
        progress = 0
    elif session.status == "running":
        progress = 50
        active_agents = ["DataAnalyst", "StatisticalAnalyst", "SpatialPatternDetector", 
                        "CorrelationHunter", "ConclusionEngine", "ReportGenerator"]
    elif session.status == "completed":
        progress = 100
        completed_agents = ["DataAnalyst", "StatisticalAnalyst", "SpatialPatternDetector", 
                           "CorrelationHunter", "ConclusionEngine", "ReportGenerator"]
    elif session.status == "failed":
        progress = 0
    
    return RCAStatusResponse(
        session_id=session_id,
        status=session.status,
        progress=progress,
        active_agents=active_agents,
        completed_agents=completed_agents,
        started_at=session.started_at,
        completed_at=session.completed_at,
    )


@router.get("/results/{session_id}", response_model=dict)
async def get_rca_results(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get RCA analysis results.
    
    Returns ranked hypotheses, confidence scores, and supporting evidence.
    """
    # Query session
    result = await db.execute(select(RCASession).where(RCASession.session_id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status not in ["completed", "partially_completed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Session not completed (status={session.status})",
        )
    
    # Query hypotheses
    hypotheses_result = await db.execute(
        select(Hypothesis)
        .where(Hypothesis.session_id == session_id)
        .order_by(Hypothesis.rank)
    )
    hypotheses = hypotheses_result.scalars().all()
    
    # Query report
    report_result = await db.execute(
        select(RCAReport).where(RCAReport.session_id == session_id)
    )
    report = report_result.scalar_one_or_none()
    
    return {
        "session_id": session_id,
        "status": session.status,
        "hypotheses": [
            {
                "rank": h.rank,
                "hypothesis": h.hypothesis_text,
                "confidence": h.confidence,
                "evidence": h.evidence,
            }
            for h in hypotheses
        ],
        "wafer_map_path": session.session_metadata.get("wafer_map_path") if session.session_metadata else None,
        "report_path": report.report_path if report else None,
        "metadata": session.session_metadata,
    }


@router.get("/messages/{session_id}", response_model=List[AgentMessageResponse])
async def get_agent_messages(
    session_id: str,
    agent_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get agent communication messages for session.
    
    Optional filtering by agent name.
    """
    query = select(AgentMessage).where(AgentMessage.session_id == session_id)
    
    if agent_name:
        query = query.where(AgentMessage.sender_agent == agent_name)
    
    query = query.order_by(AgentMessage.timestamp)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [
        AgentMessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            sender_agent=msg.sender_agent,
            content=msg.content,
            timestamp=msg.timestamp,
        )
        for msg in messages
    ]


@router.post("/feedback/{session_id}")
async def submit_feedback(
    session_id: str,
    hypothesis_id: str,
    rating: int,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit user feedback on hypothesis.
    
    Used for RAG knowledge base improvement.
    """
    from database.models import UserFeedback
    
    # Validate session exists
    result = await db.execute(select(RCASession).where(RCASession.session_id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create feedback
    feedback = UserFeedback(
        session_id=session_id,
        hypothesis_id=hypothesis_id,
        rating=rating,
        comment=comment,
    )
    db.add(feedback)
    await db.commit()
    
    logger.info(
        "feedback_submitted",
        session_id=session_id,
        hypothesis_id=hypothesis_id,
        rating=rating,
    )
    
    return {"message": "Feedback submitted successfully"}


@router.get("/download/{session_id}/report")
async def download_report(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download PDF report for session.
    
    Returns presigned S3 URL.
    """
    # Query report
    result = await db.execute(
        select(RCAReport).where(RCAReport.session_id == session_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Generate presigned URL (mock)
    from datetime import datetime, timedelta
    presigned_url = f"{report.report_path}?expires={int((datetime.now() + timedelta(hours=1)).timestamp())}"
    
    return {"download_url": presigned_url, "expires_in": 3600}


async def execute_rca_workflow(session_id: str, input_data: dict):
    """
    Background task to execute RCA workflow.
    
    Updates session status as workflow progresses.
    Creates its own DB session to avoid issues with FastAPI request lifecycle.
    """
    # Create new DB session for background task
    async with AsyncSessionLocal() as db:
        try:
            # Update status to running
            result = await db.execute(select(RCASession).where(RCASession.session_id == session_id))
            session = result.scalar_one_or_none()
            session.status = "running"
            await db.commit()
            
            logger.info("rca_workflow_starting", session_id=session_id)
            
            # Execute workflow
            workflow_result = await rca_orchestrator.execute({
                "session_id": session_id,
                **input_data,
            })
            
            # Update session with results
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.session_metadata = {
                "total_agents": 6,
                "completed_agents": 6,
                "wafer_map_path": workflow_result.get("wafer_map_path", ""),
            }
            
            # Save hypotheses
            for h_data in workflow_result.get("root_causes", []):
                hypothesis = Hypothesis(
                    session_id=session_id,
                    rank=h_data["rank"],
                    hypothesis_text=h_data["hypothesis"],
                    confidence=h_data["confidence"],
                    evidence=h_data["evidence"],
                )
                db.add(hypothesis)
            
            # Save report
            if "report_path" in workflow_result:
                report = RCAReport(
                    session_id=session_id,
                    report_path=workflow_result["report_path"],
                    format="pdf",
                )
                db.add(report)
            
            await db.commit()
            
            logger.info(
                "rca_workflow_completed",
                session_id=session_id,
                hypotheses_count=len(workflow_result.get("root_causes", [])),
            )
            
        except Exception as e:
            logger.error(
                "rca_workflow_error",
                session_id=session_id,
                error=str(e),
                exc_info=True,
            )
            
            # Update session to failed
            result = await db.execute(select(RCASession).where(RCASession.session_id == session_id))
            session = result.scalar_one_or_none()
            session.status = "failed"
            session.session_metadata = {"error": str(e)}
            await db.commit()
