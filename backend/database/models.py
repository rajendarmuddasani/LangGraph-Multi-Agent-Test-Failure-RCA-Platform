"""
Database models for RCA platform.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.base import Base


class RCASession(Base):
    """RCA session model."""
    
    __tablename__ = "rca_sessions"
    
    session_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    lot_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    wafer_id: Mapped[Optional[str]] = mapped_column(String(20))
    bin: Mapped[Optional[int]] = mapped_column(Integer)
    product_family: Mapped[Optional[str]] = mapped_column(String(50))
    package_type: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="queued",
        index=True
    )  # queued, running, completed, failed
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="normal"
    )  # low, normal, high, critical
    
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    total_duration_sec: Mapped[Optional[int]] = mapped_column(Integer)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    session_metadata: Mapped[Optional[Dict]] = mapped_column(JSONB)
    
    # Relationships
    agent_messages: Mapped[List["AgentMessage"]] = relationship(
        "AgentMessage",
        back_populates="rca_session",
        cascade="all, delete-orphan"
    )
    hypotheses: Mapped[List["Hypothesis"]] = relationship(
        "Hypothesis",
        back_populates="rca_session",
        cascade="all, delete-orphan"
    )
    tool_executions: Mapped[List["ToolExecution"]] = relationship(
        "ToolExecution",
        back_populates="rca_session",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_status_created", "status", "created_at"),
        Index("idx_lot_wafer", "lot_id", "wafer_id"),
    )


class Agent(Base):
    """Agent model."""
    
    __tablename__ = "agents"
    
    agent_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(200))
    tools: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    llm_model: Mapped[Optional[str]] = mapped_column(String(50))
    llm_temperature: Mapped[float] = mapped_column(Float, default=0.0)
    prompt_template: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent_messages: Mapped[List["AgentMessage"]] = relationship(
        "AgentMessage",
        foreign_keys="AgentMessage.sender_agent_id",
        back_populates="sender_agent"
    )


class AgentMessage(Base):
    """Agent message model (blackboard)."""
    
    __tablename__ = "agent_messages"
    
    message_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("rca_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender_agent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("agents.agent_id"),
        index=True
    )
    receiver_agent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("agents.agent_id")
    )
    message_type: Mapped[str] = mapped_column(String(50))  # finding, hypothesis, question, answer
    content: Mapped[Dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    rca_session: Mapped["RCASession"] = relationship("RCASession", back_populates="agent_messages")
    sender_agent: Mapped[Optional["Agent"]] = relationship(
        "Agent",
        foreign_keys=[sender_agent_id],
        back_populates="agent_messages"
    )
    
    __table_args__ = (
        Index("idx_session_timestamp", "session_id", "timestamp"),
    )


class ToolExecution(Base):
    """Tool execution model."""
    
    __tablename__ = "tool_executions"
    
    execution_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("rca_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    agent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("agents.agent_id")
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    inputs: Mapped[Optional[Dict]] = mapped_column(JSONB)
    outputs: Mapped[Optional[Dict]] = mapped_column(JSONB)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    rca_session: Mapped["RCASession"] = relationship("RCASession", back_populates="tool_executions")
    
    __table_args__ = (
        Index("idx_session_tool", "session_id", "tool_name"),
    )


class Hypothesis(Base):
    """Hypothesis model."""
    
    __tablename__ = "hypotheses"
    
    hypothesis_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("rca_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    hypothesis_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[Optional[Dict]] = mapped_column(JSONB)
    refuting_evidence: Mapped[Optional[Dict]] = mapped_column(JSONB)
    rank: Mapped[Optional[int]] = mapped_column(Integer)
    created_by_agent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("agents.agent_id")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rca_session: Mapped["RCASession"] = relationship("RCASession", back_populates="hypotheses")
    
    __table_args__ = (
        Index("idx_session_rank", "session_id", "rank"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="check_confidence_range"),
    )


class UserFeedback(Base):
    """User feedback model."""
    
    __tablename__ = "user_feedback"
    
    feedback_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("rca_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    correctness: Mapped[Optional[str]] = mapped_column(String(20))  # correct, incorrect, partial
    comments: Mapped[Optional[str]] = mapped_column(Text)
    confirmed_root_cause: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )


class RCAReport(Base):
    """RCA report model."""
    
    __tablename__ = "rca_reports"
    
    report_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("rca_sessions.session_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    report_metadata: Mapped[Optional[Dict]] = mapped_column(JSONB)


class STDFDataCache(Base):
    """STDF data cache model."""
    
    __tablename__ = "stdf_data_cache"
    
    cache_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[str] = mapped_column(String(50), nullable=False)
    wafer_id: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    parquet_path: Mapped[Optional[str]] = mapped_column(String(500))
    die_count: Mapped[Optional[int]] = mapped_column(Integer)
    bin_distribution: Mapped[Optional[Dict]] = mapped_column(JSONB)
    yield_value: Mapped[Optional[float]] = mapped_column(Float)
    parsed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_lot_wafer_unique", "lot_id", "wafer_id", unique=True),
    )


class WaferMap(Base):
    """Wafer map model."""
    
    __tablename__ = "wafer_maps"
    
    map_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    wafer_id: Mapped[str] = mapped_column(String(20), nullable=False)
    bin: Mapped[Optional[int]] = mapped_column(Integer)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    pattern_type: Mapped[Optional[str]] = mapped_column(String(50))
    pattern_confidence: Mapped[Optional[float]] = mapped_column(Float)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_lot_wafer_map", "lot_id", "wafer_id"),
    )
