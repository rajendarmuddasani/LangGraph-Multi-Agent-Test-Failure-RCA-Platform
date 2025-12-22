"""
Data Analyst Agent - Parses STDF files and generates wafer maps.
"""
from typing import Dict, Any, List
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


class STDFParserInput(BaseModel):
    """Input schema for STDF parser tool."""
    lot_id: str = Field(description="Lot identifier (e.g., TC41x_LOT123)")
    wafer_id: str = Field(description="Wafer identifier (e.g., W05)")


class DataAnalystAgent:
    """
    Data Analyst Agent - Specializes in:
    - Parsing STDF binary files
    - Generating wafer maps
    - Extracting test data summaries
    - SQL queries on test data warehouse
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_retries=settings.OPENAI_MAX_RETRIES,
            timeout=settings.OPENAI_TIMEOUT,
        )
        self.tools = self._create_tools()
        self.name = "DataAnalyst"
        self.role = "Parse STDF files and generate wafer maps"
    
    def _create_tools(self) -> List[StructuredTool]:
        """Create agent tools."""
        return [
            StructuredTool.from_function(
                func=self.parse_stdf,
                name="parse_stdf",
                description="Parse STDF file for given lot and wafer, return test data summary",
                args_schema=STDFParserInput,
            ),
            StructuredTool.from_function(
                func=self.generate_wafer_map,
                name="generate_wafer_map",
                description="Generate wafer map PNG image from die coordinates and bins",
            ),
        ]
    
    async def parse_stdf(self, lot_id: str, wafer_id: str) -> Dict[str, Any]:
        """
        Parse STDF file and return test data summary.
        
        In production, this would:
        1. Download STDF file from S3: s3://stdf-files/{lot_id}_{wafer_id}.stdf
        2. Parse with pystdf library
        3. Extract: die count, bin distribution, yield, top failing tests
        4. Store parsed data in Parquet format
        5. Cache results in PostgreSQL (stdf_data_cache table)
        """
        logger.info("parsing_stdf", lot_id=lot_id, wafer_id=wafer_id)
        
        # Mock data for demonstration
        mock_data = {
            "lot_id": lot_id,
            "wafer_id": wafer_id,
            "die_count": 5000,
            "bin_distribution": {
                "bin1": 4200,  # Pass
                "bin5": 600,   # Fail functional
                "bin99": 200,  # Scrap
            },
            "yield": 0.84,
            "top_failing_tests": ["IDDQ_25C", "Vth_nom", "Fmax_100C"],
            "parametric_summary": {
                "IDDQ_25C": {"mean": 105.3, "std": 25.1, "min": 45.2, "max": 185.7},
                "Vth_nom": {"mean": 0.72, "std": 0.05, "min": 0.61, "max": 0.88},
            }
        }
        
        logger.info(
            "stdf_parsed",
            lot_id=lot_id,
            wafer_id=wafer_id,
            die_count=mock_data["die_count"],
            yield_value=mock_data["yield"],
        )
        
        return mock_data
    
    async def generate_wafer_map(self, stdf_data: Dict[str, Any]) -> str:
        """
        Generate wafer map PNG image.
        
        In production, this would:
        1. Read die (x, y, bin) data from parsed STDF
        2. Create 300x300 RGB image using OpenCV/PIL
        3. Color code by bin (bin1=green, bin5=red, bin99=black)
        4. Upload to S3: s3://wafer-maps/{lot_id}_{wafer_id}_bin{bin}.png
        5. Store metadata in PostgreSQL (wafer_maps table)
        6. Return S3 path
        """
        lot_id = stdf_data.get("lot_id")
        wafer_id = stdf_data.get("wafer_id")
        
        logger.info("generating_wafer_map", lot_id=lot_id, wafer_id=wafer_id)
        
        # Mock S3 path
        wafer_map_path = f"s3://wafer-maps/{lot_id}_{wafer_id}_all_bins.png"
        
        logger.info(
            "wafer_map_generated",
            lot_id=lot_id,
            wafer_id=wafer_id,
            path=wafer_map_path,
        )
        
        return wafer_map_path
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Data Analyst agent.
        
        Args:
            state: Agent state containing lot_id, wafer_id, bin
        
        Returns:
            Updated state with STDF data and wafer map path
        """
        logger.info(
            "data_analyst_executing",
            session_id=state.get("session_id"),
            lot_id=state.get("lot_id"),
        )
        
        try:
            # Parse STDF
            stdf_data = await self.parse_stdf(
                lot_id=state["lot_id"],
                wafer_id=state["wafer_id"],
            )
            
            # Generate wafer map
            wafer_map_path = await self.generate_wafer_map(stdf_data)
            
            # Update state
            state["stdf_data"] = stdf_data
            state["wafer_map_path"] = wafer_map_path
            
            # Add message to blackboard
            message = {
                "agent": self.name,
                "timestamp": "2025-12-05T10:00:00Z",
                "finding": f"STDF parsed: {stdf_data['die_count']} die, "
                          f"{stdf_data['yield']*100:.1f}% yield, wafer map generated",
                "confidence": 1.0,
            }
            state["messages"].append(message)
            
            logger.info(
                "data_analyst_completed",
                session_id=state.get("session_id"),
                die_count=stdf_data["die_count"],
                yield_value=stdf_data["yield"],
            )
            
            return state
            
        except Exception as e:
            logger.error(
                "data_analyst_failed",
                session_id=state.get("session_id"),
                error=str(e),
                exc_info=True,
            )
            state["error"] = f"DataAnalyst failed: {str(e)}"
            return state


# Singleton instance
data_analyst_agent = DataAnalystAgent()
