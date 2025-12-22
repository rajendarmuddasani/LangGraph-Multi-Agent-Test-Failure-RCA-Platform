"""
Statistical Analyst Agent - Performs statistical analysis on test data.
"""
from typing import Dict, Any
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


class StatisticalAnalystAgent:
    """
    Agent specialized in statistical analysis of semiconductor test data.
    
    Capabilities:
    - T-tests for comparing bin rates vs baseline
    - ANOVA for multi-group comparisons
    - Control chart analysis (Xbar-R, EWMA)
    - Distribution analysis (normality tests, outlier detection)
    - Parametric test correlation analysis
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY,
        )
        self.tools = [
            Tool(
                name="t_test_analysis",
                func=self._t_test_analysis,
                description="Perform t-test to compare current bin rate against historical baseline",
            ),
            Tool(
                name="anova_analysis",
                func=self._anova_analysis,
                description="Perform ANOVA to compare test results across multiple lots/wafers",
            ),
            Tool(
                name="control_chart_analysis",
                func=self._control_chart_analysis,
                description="Analyze control charts for process stability and trends",
            ),
            Tool(
                name="outlier_detection",
                func=self._outlier_detection,
                description="Detect outliers in parametric test data using Z-score and IQR methods",
            ),
        ]
    
    def _t_test_analysis(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform t-test comparing current bin rate to historical baseline.
        
        In production: Use scipy.stats.ttest_ind
        """
        from scipy import stats
        import numpy as np
        
        # Mock baseline data
        baseline_bin_rates = np.random.normal(0.12, 0.03, 100)  # 12% ± 3% baseline
        current_bin_rate = test_data.get("current_bin_rate", 0.18)
        current_sample = np.array([current_bin_rate] * 30)  # Simulate sample
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(current_sample, baseline_bin_rates)
        
        conclusion = "significantly elevated" if p_value < 0.05 and t_stat > 0 else "within normal range"
        
        logger.info(
            "t_test_completed",
            t_statistic=float(t_stat),
            p_value=float(p_value),
            conclusion=conclusion,
        )
        
        return {
            "test": "t-test",
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "conclusion": f"Bin rate {conclusion} (p={p_value:.4f})",
            "confidence": 0.95 if p_value < 0.05 else 0.60,
            "recommendation": "Investigate root cause" if p_value < 0.05 else "Monitor trends",
        }
    
    def _anova_analysis(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform ANOVA to compare test results across multiple groups.
        
        In production: Use scipy.stats.f_oneway
        """
        from scipy import stats
        import numpy as np
        
        # Mock data for 3 lots
        lot1 = np.random.normal(100, 5, 50)
        lot2 = np.random.normal(105, 6, 50)
        lot3 = np.random.normal(110, 4, 50)
        
        f_stat, p_value = stats.f_oneway(lot1, lot2, lot3)
        
        logger.info(
            "anova_completed",
            f_statistic=float(f_stat),
            p_value=float(p_value),
        )
        
        return {
            "test": "ANOVA",
            "f_statistic": float(f_stat),
            "p_value": float(p_value),
            "conclusion": f"Significant difference between lots (p={p_value:.4f})" if p_value < 0.05 else "No significant difference",
            "confidence": 0.90 if p_value < 0.05 else 0.50,
        }
    
    def _control_chart_analysis(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze control chart for process stability.
        
        In production: Calculate UCL, LCL, detect runs, trends
        """
        import numpy as np
        
        # Mock control chart data
        data = np.random.normal(100, 5, 30)
        mean = np.mean(data)
        std = np.std(data)
        ucl = mean + 3 * std
        lcl = mean - 3 * std
        
        # Detect out-of-control points
        out_of_control = np.sum((data > ucl) | (data < lcl))
        
        logger.info(
            "control_chart_analyzed",
            mean=float(mean),
            ucl=float(ucl),
            lcl=float(lcl),
            out_of_control_points=int(out_of_control),
        )
        
        return {
            "test": "Control Chart (Xbar-R)",
            "mean": float(mean),
            "ucl": float(ucl),
            "lcl": float(lcl),
            "out_of_control_points": int(out_of_control),
            "conclusion": f"{out_of_control} out-of-control points detected" if out_of_control > 0 else "Process in control",
            "confidence": 0.85 if out_of_control > 0 else 0.70,
        }
    
    def _outlier_detection(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect outliers using Z-score and IQR methods.
        
        In production: Apply to parametric test data (IDDQ, Vth, etc.)
        """
        import numpy as np
        
        # Mock parametric test data
        iddq_data = np.random.lognormal(3, 0.5, 500)
        
        # Z-score method
        z_scores = np.abs((iddq_data - np.mean(iddq_data)) / np.std(iddq_data))
        z_outliers = np.sum(z_scores > 3)
        
        # IQR method
        q1 = np.percentile(iddq_data, 25)
        q3 = np.percentile(iddq_data, 75)
        iqr = q3 - q1
        iqr_outliers = np.sum((iddq_data < q1 - 1.5 * iqr) | (iddq_data > q3 + 1.5 * iqr))
        
        logger.info(
            "outlier_detection_completed",
            z_outliers=int(z_outliers),
            iqr_outliers=int(iqr_outliers),
        )
        
        return {
            "test": "Outlier Detection",
            "z_score_outliers": int(z_outliers),
            "iqr_outliers": int(iqr_outliers),
            "total_samples": len(iddq_data),
            "outlier_percentage": float((z_outliers / len(iddq_data)) * 100),
            "conclusion": f"{z_outliers} outliers detected in IDDQ data (Z-score method)",
            "confidence": 0.88 if z_outliers > 10 else 0.65,
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute statistical analysis workflow.
        
        Args:
            state: Workflow state containing STDF data
        
        Returns:
            Updated state with statistical findings
        """
        logger.info(
            "statistical_analyst_starting",
            session_id=state.get("session_id"),
            lot_id=state.get("lot_id"),
        )
        
        # Extract test data from state
        stdf_data = state.get("stdf_data", {})
        current_bin_rate = stdf_data.get("bin_distribution", {}).get("bin5", 600) / stdf_data.get("die_count", 5000)
        
        # Run statistical analyses
        findings = []
        
        # T-test
        t_test_result = self._t_test_analysis({"current_bin_rate": current_bin_rate})
        findings.append(t_test_result)
        
        # ANOVA
        anova_result = self._anova_analysis({})
        findings.append(anova_result)
        
        # Control chart
        control_chart_result = self._control_chart_analysis({})
        findings.append(control_chart_result)
        
        # Outlier detection
        outlier_result = self._outlier_detection({})
        findings.append(outlier_result)
        
        # Use LLM to synthesize findings
        synthesis_prompt = f"""
        You are a statistical analyst reviewing semiconductor test failure data.
        
        Statistical Analysis Results:
        {findings}
        
        Lot: {state.get('lot_id')}
        Wafer: {state.get('wafer_id')}
        Bin: {state.get('bin')}
        
        Provide a concise summary of the key statistical findings and their implications for root cause analysis.
        Focus on the most significant results (p < 0.05).
        """
        
        try:
            response = self.llm.invoke(synthesis_prompt)
            synthesis = response.content
        except Exception as e:
            logger.error("llm_synthesis_failed", error=str(e))
            synthesis = f"Statistical analysis completed: {len(findings)} tests performed"
        
        # Update state
        state["statistical_findings"] = findings
        
        if "messages" not in state:
            state["messages"] = []
        
        state["messages"].append({
            "agent": "StatisticalAnalyst",
            "finding": synthesis,
            "confidence": max([f.get("confidence", 0.5) for f in findings]),
            "details": findings,
        })
        
        logger.info(
            "statistical_analyst_completed",
            session_id=state.get("session_id"),
            findings_count=len(findings),
        )
        
        return state


# Singleton instance
statistical_analyst_agent = StatisticalAnalystAgent()
