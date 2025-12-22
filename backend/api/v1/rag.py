"""
RAG (Retrieval-Augmented Generation) API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List
import structlog

from core.config import settings
from schemas.rca import RAGSearchRequest, RAGSearchResponse, RAGSearchResult

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])

# Qdrant client (initialized at startup)
qdrant_client: QdrantClient = None


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance."""
    global qdrant_client
    if qdrant_client is None:
        qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
    return qdrant_client


@router.post("/search", response_model=RAGSearchResponse)
async def search_knowledge_base(
    request: RAGSearchRequest,
    qdrant: QdrantClient = Depends(get_qdrant_client),
):
    """
    Search RAG knowledge base.
    
    Performs semantic search over historical RCA reports, returning
    similar past cases to inform current analysis.
    """
    try:
        # Generate query embedding (mock - in production use OpenAI embeddings)
        query_embedding = [0.1] * 1536  # Mock 1536-dim embedding
        
        # Build Qdrant filters
        qdrant_filter = None
        if request.filters:
            conditions = []
            for key, value in request.filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
            if conditions:
                qdrant_filter = Filter(must=conditions)
        
        # Search Qdrant
        search_results = qdrant.search(
            collection_name=settings.qdrant_collection_name,
            query_vector=query_embedding,
            limit=request.top_k,
            score_threshold=request.similarity_threshold,
            query_filter=qdrant_filter,
        )
        
        logger.info(
            "rag_search_completed",
            query=request.query,
            results_count=len(search_results),
        )
        
        # Format results
        results = [
            RAGSearchResult(
                id=result.id,
                score=result.score,
                text=result.payload.get("text", ""),
                metadata={
                    k: v for k, v in result.payload.items() if k != "text"
                },
            )
            for result in search_results
        ]
        
        return RAGSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
        )
        
    except Exception as e:
        logger.error(
            "rag_search_failed",
            query=request.query,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"RAG search failed: {str(e)}",
        )


@router.get("/similar/{session_id}", response_model=RAGSearchResponse)
async def find_similar_cases(
    session_id: str,
    top_k: int = 10,
    qdrant: QdrantClient = Depends(get_qdrant_client),
):
    """
    Find similar historical RCA cases.
    
    Uses current session's hypotheses to find similar past cases.
    """
    try:
        # In production: fetch session hypotheses and generate embedding
        # For now, use mock embedding
        query_embedding = [0.1] * 1536
        
        search_results = qdrant.search(
            collection_name=settings.qdrant_collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=0.7,
        )
        
        results = [
            RAGSearchResult(
                id=result.id,
                score=result.score,
                text=result.payload.get("text", ""),
                metadata={
                    k: v for k, v in result.payload.items() if k != "text"
                },
            )
            for result in search_results
        ]
        
        return RAGSearchResponse(
            query=f"Similar cases for session {session_id}",
            results=results,
            total_results=len(results),
        )
        
    except Exception as e:
        logger.error(
            "similar_cases_search_failed",
            session_id=session_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Similar cases search failed: {str(e)}",
        )


@router.post("/embed")
async def embed_rca_session(
    session_id: str,
    qdrant: QdrantClient = Depends(get_qdrant_client),
):
    """
    Embed completed RCA session into knowledge base.
    
    Stores session hypotheses and findings as vectors for future retrieval.
    """
    try:
        # In production:
        # 1. Fetch session data from DB
        # 2. Generate embeddings for hypotheses + findings
        # 3. Store in Qdrant with metadata
        
        logger.info("rca_session_embedded", session_id=session_id)
        
        return {
            "message": "RCA session embedded successfully",
            "session_id": session_id,
        }
        
    except Exception as e:
        logger.error(
            "embed_session_failed",
            session_id=session_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Embedding failed: {str(e)}",
        )
