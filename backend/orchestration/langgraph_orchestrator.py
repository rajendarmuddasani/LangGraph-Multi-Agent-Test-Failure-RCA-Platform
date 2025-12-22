"""
LangGraph multi-agent orchestrator for RCA workflow.
"""
from typing import Dict, Any, TypedDict, Annotated, Sequence
from operator import add
from langgraph.graph import StateGraph, END
import structlog

from agents.data_analyst import data_analyst_agent
from agents.statistical_analyst import statistical_analyst_agent
from agents.spatial_pattern_detector import spatial_pattern_detector_agent
from agents.correlation_hunter import correlation_hunter_agent
from agents.synthesizer import conclusion_engine_agent
from agents.report_generator import report_generator_agent
from core.config import settings

logger = structlog.get_logger(__name__)


def keep_first(left, right):
    """Reducer that keeps the first value and ignores subsequent updates."""
    return left if left is not None else right


def keep_non_empty(left, right):
    """Reducer that keeps the first non-empty value."""
    # If left is empty/None, use right
    if not left:
        return right
    # If right is empty/None, keep left
    if not right:
        return left
    # Both have values, keep left (first one wins)
    return left


class AgentState(TypedDict):
    """Shared state across all agents in the workflow."""
    # Input fields - keep first value when multiple agents try to update
    session_id: Annotated[str, keep_first]
    lot_id: Annotated[str, keep_first]
    wafer_id: Annotated[str, keep_first]
    bin: Annotated[int, keep_first]
    priority: Annotated[str, keep_first]
    
    # Data populated by agents - keep first value to support parallel execution
    stdf_data: Annotated[dict, keep_first]
    wafer_map_path: Annotated[str, keep_first]
    statistical_findings: Annotated[list, keep_non_empty]
    spatial_patterns: Annotated[list, keep_non_empty]
    correlations: Annotated[list, keep_non_empty]
    rag_results: Annotated[list, keep_non_empty]
    root_causes: Annotated[list, keep_non_empty]  # Ranked hypotheses - keep non-empty!
    confidence_scores: Annotated[dict, keep_non_empty]
    
    # Agent communication log (blackboard) - messages accumulate
    messages: Annotated[Sequence[dict], add]
    
    # Error handling
    error: Annotated[str | None, keep_first]

class RCAOrchestrator:
    """
    LangGraph-based multi-agent RCA orchestrator.
    
    Workflow:
    START → DataAnalyst → ParallelAnalysis → ConclusionEngine → ReportGenerator → END
    """
    
    def __init__(self):
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph state machine."""
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("data_analyst", self._data_analyst_node)
        workflow.add_node("statistical_analyst", self._statistical_analyst_node)
        workflow.add_node("spatial_analyst", self._spatial_analyst_node)
        workflow.add_node("correlation_hunter", self._correlation_hunter_node)
        workflow.add_node("conclusion_engine", self._conclusion_engine_node)
        workflow.add_node("report_generator", self._report_generator_node)
        
        # Define workflow edges
        workflow.set_entry_point("data_analyst")
        
        # After data analyst, run parallel analysis
        workflow.add_edge("data_analyst", "statistical_analyst")
        workflow.add_edge("data_analyst", "spatial_analyst")
        workflow.add_edge("data_analyst", "correlation_hunter")
        
        # All parallel agents converge to conclusion engine
        workflow.add_edge("statistical_analyst", "conclusion_engine")
        workflow.add_edge("spatial_analyst", "conclusion_engine")
        workflow.add_edge("correlation_hunter", "conclusion_engine")
        
        # Conclusion engine to report generator
        workflow.add_edge("conclusion_engine", "report_generator")
        
        # Report generator to end
        workflow.add_edge("report_generator", END)
        
        return workflow
    
    async def _data_analyst_node(self, state: AgentState) -> AgentState:
        """Data Analyst agent node."""
        logger.info("executing_data_analyst", session_id=state["session_id"])
        return await data_analyst_agent.execute(state)
    
    async def _statistical_analyst_node(self, state: AgentState) -> AgentState:
        """Statistical Analyst agent node."""
        logger.info("executing_statistical_analyst", session_id=state["session_id"])
        return await statistical_analyst_agent.execute(state)
    
    async def _spatial_analyst_node(self, state: AgentState) -> AgentState:
        """Spatial Analyst agent node."""
        logger.info("executing_spatial_analyst", session_id=state["session_id"])
        return await spatial_pattern_detector_agent.execute(state)
    
    async def _correlation_hunter_node(self, state: AgentState) -> AgentState:
        """Correlation Hunter agent node."""
        logger.info("executing_correlation_hunter", session_id=state["session_id"])
        return await correlation_hunter_agent.execute(state)
    
    async def _conclusion_engine_node(self, state: AgentState) -> AgentState:
        """Conclusion engine agent node - aggregates findings and ranks hypotheses."""
        logger.info("executing_conclusion_engine", session_id=state["session_id"])
        return await conclusion_engine_agent.execute(state)
    
    async def _report_generator_node(self, state: AgentState) -> AgentState:
        """Report Generator agent node - creates PDF report."""
        logger.info("executing_report_generator", session_id=state["session_id"])
        return await report_generator_agent.execute(state)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute full RCA workflow.
        
        Args:
            input_data: Input containing lot_id, wafer_id, bin, session_id
        
        Returns:
            Final state with RCA results
        """
        logger.info(
            "rca_workflow_starting",
            session_id=input_data["session_id"],
            lot_id=input_data["lot_id"],
        )
        
        # Initialize state
        initial_state: AgentState = {
            "session_id": input_data["session_id"],
            "lot_id": input_data["lot_id"],
            "wafer_id": input_data.get("wafer_id", ""),
            "bin": input_data.get("bin", 0),
            "priority": input_data.get("priority", "normal"),
            "stdf_data": {},
            "wafer_map_path": "",
            "statistical_findings": [],
            "spatial_patterns": [],
            "correlations": [],
            "rag_results": [],
            "root_causes": [],
            "confidence_scores": {},
            "messages": [],
            "error": None,
        }
        
        try:
            # Execute workflow
            result = await self.app.ainvoke(initial_state)
            
            logger.info(
                "rca_workflow_completed",
                session_id=input_data["session_id"],
                hypotheses_count=len(result.get("root_causes", [])),
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "rca_workflow_failed",
                session_id=input_data["session_id"],
                error=str(e),
                exc_info=True,
            )
            initial_state["error"] = str(e)
            return initial_state


# Singleton orchestrator instance
rca_orchestrator = RCAOrchestrator()
