"""
Pydantic schemas for RCA API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RCASessionCreate(BaseModel):
    """Request schema for creating RCA session."""
    lot_id: str = Field(..., min_length=1, max_length=255)
    wafer_id: str = Field(..., min_length=1, max_length=255)
    bin: int = Field(..., ge=0)
    priority: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    user_id: str = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "lot_id": "LOT12345",
                "wafer_id": "W01",
                "bin": 5,
                "priority": "high",
                "user_id": "user@company.com",
            }
        }


class RCASessionResponse(BaseModel):
    """Response schema for RCA session creation."""
    session_id: str
    status: str
    message: str


class RCAStatusResponse(BaseModel):
    """Response schema for RCA status."""
    session_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    active_agents: List[str]
    completed_agents: List[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "running",
                "progress": 65,
                "active_agents": ["ConclusionEngine"],
                "completed_agents": ["DataAnalyst", "StatisticalAnalyst", "SpatialAnalyst"],
                "started_at": "2024-01-15T10:30:00Z",
                "completed_at": None,
            }
        }


class HypothesisResponse(BaseModel):
    """Response schema for hypothesis."""
    rank: int
    hypothesis: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Dict[str, Any]]


class AgentMessageResponse(BaseModel):
    """Response schema for agent message."""
    id: str
    session_id: str
    sender_agent: str
    content: Dict[str, Any]
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg-123",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "sender_agent": "DataAnalyst",
                "content": {
                    "finding": "Parsed STDF file: 5000 die, 84% yield",
                    "wafer_map_path": "s3://wafer-maps/LOT12345_W01_all_bins.png",
                },
                "timestamp": "2024-01-15T10:31:00Z",
            }
        }


class RAGSearchRequest(BaseModel):
    """Request schema for RAG search."""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Edge effect pattern on wafer periphery",
                "top_k": 10,
                "similarity_threshold": 0.7,
                "filters": {"bin": 5},
            }
        }


class RAGSearchResult(BaseModel):
    """Response schema for RAG search result."""
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]


class RAGSearchResponse(BaseModel):
    """Response schema for RAG search."""
    query: str
    results: List[RAGSearchResult]
    total_results: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Edge effect pattern on wafer periphery",
                "results": [
                    {
                        "id": "rca-456",
                        "score": 0.92,
                        "text": "Edge effect detected: Package stress causing peripheral die failures...",
                        "metadata": {
                            "session_id": "old-session-123",
                            "lot_id": "LOT98765",
                            "confidence": 0.88,
                            "date": "2024-01-10",
                        },
                    }
                ],
                "total_results": 8,
            }
        }
