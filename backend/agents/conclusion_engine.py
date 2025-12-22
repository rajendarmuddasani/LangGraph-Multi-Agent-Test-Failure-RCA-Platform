"""
Conclusion Engine Agent - Aggregates findings and ranks hypotheses using LLM.
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


class ConclusionEngineAgent:
    """
    Agent specialized in synthesizing multi-agent findings into ranked hypotheses.
    
    Capabilities:
    - Aggregate findings from all specialist agents
    - Use LLM to synthesize evidence and generate hypotheses
    - Query RAG knowledge base for similar historical cases
    - Rank hypotheses by confidence score
    - Provide supporting evidence for each hypothesis
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.2,  # Slightly higher for creative synthesis
            api_key=settings.OPENAI_API_KEY,
        )
        
        # Synthesis prompt template
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert semiconductor failure analysis engineer with 20+ years of experience.
Your role is to synthesize findings from multiple specialist agents and generate ranked root cause hypotheses.

Guidelines:
- Combine evidence from statistical, spatial, and correlation analyses
- Generate 3-5 distinct hypotheses ranked by confidence
- Provide specific evidence supporting each hypothesis
- Include confidence score (0-1) based on evidence strength
- Suggest next steps for validation
- Be specific to the failure mode and test data"""),
            ("user", """{analysis_context}

Based on the above multi-agent analysis, generate ranked root cause hypotheses for this test failure."""),
        ])
    
    def _query_rag_knowledge_base(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query RAG knowledge base for similar historical cases.
        
        In production: Use Qdrant vector search
        """
        # Mock RAG results
        similar_cases = [
            {
                "session_id": "rca-2024-03-15-001",
                "lot_id": "LOT98765",
                "hypothesis": "Package stress causing peripheral die failures due to CTE mismatch",
                "confidence": 0.88,
                "similarity_score": 0.92,
                "outcome": "Validated - Changed package material",
            },
            {
                "session_id": "rca-2024-02-20-003",
                "lot_id": "LOT87654",
                "hypothesis": "Solder voids under edge die causing electrical opens",
                "confidence": 0.82,
                "similarity_score": 0.87,
                "outcome": "Validated - Improved reflow profile",
            },
            {
                "session_id": "rca-2024-01-10-007",
                "lot_id": "LOT76543",
                "hypothesis": "Wafer thinning process causing edge cracking",
                "confidence": 0.75,
                "similarity_score": 0.81,
                "outcome": "Partially validated - Adjusted grinding parameters",
            },
        ]
        
        logger.info(
            "rag_query_completed",
            results_count=len(similar_cases),
            top_similarity=similar_cases[0]["similarity_score"],
        )
        
        return similar_cases
    
    def _generate_hypotheses_with_llm(
        self,
        statistical_findings: List[Dict],
        spatial_patterns: List[Dict],
        correlations: List[Dict],
        rag_results: List[Dict],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to generate ranked hypotheses from aggregated evidence.
        """
        # Build analysis context
        analysis_context = f"""
LOT: {context.get('lot_id')}
WAFER: {context.get('wafer_id')}
BIN: {context.get('bin')}
PRIORITY: {context.get('priority')}

=== STATISTICAL ANALYSIS FINDINGS ===
{self._format_findings(statistical_findings)}

=== SPATIAL PATTERN ANALYSIS ===
{self._format_findings(spatial_patterns)}

=== CORRELATION ANALYSIS ===
{self._format_findings(correlations)}

=== SIMILAR HISTORICAL CASES (RAG) ===
{self._format_rag_results(rag_results)}

=== TEST DATA SUMMARY ===
Die Count: {context.get('stdf_data', {}).get('die_count', 'N/A')}
Yield: {context.get('stdf_data', {}).get('yield', 'N/A')}
Bin Distribution: {context.get('stdf_data', {}).get('bin_distribution', {})}
"""
        
        try:
            # Invoke LLM with synthesis prompt
            chain = self.synthesis_prompt | self.llm
            response = chain.invoke({"analysis_context": analysis_context})
            
            # Parse LLM response into structured hypotheses
            # In production: Use structured output or JSON mode
            hypotheses = self._parse_llm_hypotheses(response.content, context)
            
            logger.info(
                "llm_hypotheses_generated",
                count=len(hypotheses),
                top_confidence=hypotheses[0]["confidence"] if hypotheses else 0,
            )
            
        except Exception as e:
            logger.error("llm_hypothesis_generation_failed", error=str(e), exc_info=True)
            # Fallback: Generate rule-based hypotheses
            hypotheses = self._generate_fallback_hypotheses(
                statistical_findings,
                spatial_patterns,
                correlations,
                context,
            )
        
        return hypotheses
    
    def _format_findings(self, findings: List[Dict]) -> str:
        """Format findings for LLM context."""
        if not findings:
            return "No findings available"
        
        formatted = []
        for f in findings:
            conf = f.get("confidence", 0)
            desc = f.get("description", f.get("conclusion", "N/A"))
            formatted.append(f"- {desc} (confidence: {conf:.2f})")
        
        return "\n".join(formatted)
    
    def _format_rag_results(self, rag_results: List[Dict]) -> str:
        """Format RAG results for LLM context."""
        if not rag_results:
            return "No similar historical cases found"
        
        formatted = []
        for r in rag_results:
            formatted.append(
                f"- {r['hypothesis']} (similarity: {r['similarity_score']:.2f}, "
                f"confidence: {r['confidence']:.2f}, outcome: {r['outcome']})"
            )
        
        return "\n".join(formatted)
    
    def _parse_llm_hypotheses(self, llm_response: str, context: Dict) -> List[Dict[str, Any]]:
        """
        Parse LLM response into structured hypotheses.
        
        In production: Use structured output or JSON parsing
        """
        # Mock parsing - in production, use JSON mode or regex
        hypotheses = [
            {
                "rank": 1,
                "hypothesis": "Package stress (thermal/mechanical) causing peripheral die failures",
                "confidence": 0.87,
                "evidence": [
                    {"type": "spatial", "detail": "Edge effect pattern detected (92% confidence)"},
                    {"type": "statistical", "detail": "Bin rate significantly elevated (p<0.001)"},
                    {"type": "correlation", "detail": "IDDQ/Vth correlation suggests junction stress"},
                    {"type": "rag", "detail": "Similar case: LOT98765 validated package stress (88% confidence)"},
                ],
                "next_steps": [
                    "Perform cross-section analysis on edge die",
                    "Thermal cycling stress test on suspect packages",
                    "Review package material specifications",
                ],
            },
            {
                "rank": 2,
                "hypothesis": "Solder void under peripheral die causing electrical opens",
                "confidence": 0.78,
                "evidence": [
                    {"type": "spatial", "detail": "Failures concentrated at wafer edges"},
                    {"type": "correlation", "detail": "IDDQ elevated indicating current leakage"},
                    {"type": "rag", "detail": "Historical case LOT87654 had solder void issue"},
                ],
                "next_steps": [
                    "X-ray inspection of solder joints",
                    "Review reflow profile temperature uniformity",
                    "Check solder paste volume on edge die",
                ],
            },
            {
                "rank": 3,
                "hypothesis": "Wafer edge thinning process causing mechanical stress",
                "confidence": 0.72,
                "evidence": [
                    {"type": "spatial", "detail": "Edge die failures concentrated"},
                    {"type": "statistical", "detail": "Control chart shows recent process shift"},
                    {"type": "rag", "detail": "LOT76543 had wafer thinning issue (75% confidence)"},
                ],
                "next_steps": [
                    "Review wafer grinding parameters",
                    "Measure edge die thickness variation",
                    "Check backgrind tape adhesion",
                ],
            },
        ]
        
        return hypotheses
    
    def _generate_fallback_hypotheses(
        self,
        statistical_findings: List[Dict],
        spatial_patterns: List[Dict],
        correlations: List[Dict],
        context: Dict,
    ) -> List[Dict[str, Any]]:
        """
        Generate rule-based hypotheses when LLM fails.
        """
        # Simple rule-based hypothesis generation
        hypotheses = []
        rank = 1
        
        # Check for edge effect
        edge_patterns = [p for p in spatial_patterns if p.get("pattern") == "edge_effect"]
        if edge_patterns and edge_patterns[0].get("confidence", 0) > 0.7:
            hypotheses.append({
                "rank": rank,
                "hypothesis": "Edge effect detected - possible package stress or thermal gradient",
                "confidence": edge_patterns[0]["confidence"],
                "evidence": [{"type": "spatial", "detail": edge_patterns[0]["description"]}],
                "next_steps": ["Perform cross-section analysis", "Review thermal profile"],
            })
            rank += 1
        
        # Check for significant statistical deviation
        sig_stats = [s for s in statistical_findings if s.get("p_value", 1) < 0.05]
        if sig_stats:
            hypotheses.append({
                "rank": rank,
                "hypothesis": "Statistical deviation detected - process shift likely",
                "confidence": 0.75,
                "evidence": [{"type": "statistical", "detail": sig_stats[0]["conclusion"]}],
                "next_steps": ["Review process parameters", "Check equipment calibration"],
            })
            rank += 1
        
        # Default hypothesis if no strong patterns
        if not hypotheses:
            hypotheses.append({
                "rank": 1,
                "hypothesis": "Random failures - requires further investigation",
                "confidence": 0.50,
                "evidence": [{"type": "general", "detail": "No strong patterns detected"}],
                "next_steps": ["Collect more data", "Review historical trends"],
            })
        
        return hypotheses
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute synthesis workflow.
        
        Args:
            state: Workflow state with all agent findings
        
        Returns:
            Updated state with ranked hypotheses
        """
        logger.info(
            "synthesizer_starting",
            session_id=state.get("session_id"),
            lot_id=state.get("lot_id"),
        )
        
        # Extract findings from state
        statistical_findings = state.get("statistical_findings", [])
        spatial_patterns = state.get("spatial_patterns", [])
        correlations = state.get("correlations", [])
        
        # Query RAG knowledge base
        rag_results = self._query_rag_knowledge_base({
            "lot_id": state.get("lot_id"),
            "bin": state.get("bin"),
            "spatial_patterns": spatial_patterns,
        })
        state["rag_results"] = rag_results
        
        # Generate hypotheses using LLM
        hypotheses = self._generate_hypotheses_with_llm(
            statistical_findings,
            spatial_patterns,
            correlations,
            rag_results,
            state,
        )
        
        # Update state with ranked hypotheses
        state["root_causes"] = hypotheses
        
        # Add synthesis message
        if "messages" not in state:
            state["messages"] = []
        
        top_hypothesis = hypotheses[0] if hypotheses else None
        state["messages"].append({
            "agent": "ConclusionEngine",
            "finding": f"Top hypothesis: {top_hypothesis['hypothesis']}" if top_hypothesis else "Analysis complete",
            "confidence": top_hypothesis["confidence"] if top_hypothesis else 0.5,
            "details": hypotheses,
        })
        
        logger.info(
            "synthesizer_completed",
            session_id=state.get("session_id"),
            hypotheses_count=len(hypotheses),
            top_confidence=top_hypothesis["confidence"] if top_hypothesis else 0,
        )
        
        return state


# Singleton instance
conclusion_engine_agent = ConclusionEngineAgent()
