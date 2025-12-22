"""
Correlation Hunter Agent - Discovers correlations between test parameters.
"""
from typing import Dict, Any, List, Tuple
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
import structlog
import numpy as np

from core.config import settings

logger = structlog.get_logger(__name__)


class CorrelationHunterAgent:
    """
    Agent specialized in finding correlations between test parameters.
    
    Capabilities:
    - Pearson correlation analysis
    - Spearman rank correlation
    - Feature importance using Random Forest
    - Time-series correlation (lot-to-lot trends)
    - Multi-parameter interaction analysis
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY,
        )
        self.tools = [
            Tool(
                name="pearson_correlation",
                func=self._pearson_correlation,
                description="Calculate Pearson correlation between parametric tests",
            ),
            Tool(
                name="spearman_correlation",
                func=self._spearman_correlation,
                description="Calculate Spearman rank correlation (non-linear relationships)",
            ),
            Tool(
                name="feature_importance",
                func=self._feature_importance,
                description="Calculate feature importance using Random Forest",
            ),
            Tool(
                name="time_series_correlation",
                func=self._time_series_correlation,
                description="Analyze lot-to-lot trends and correlations",
            ),
        ]
    
    def _pearson_correlation(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Pearson correlation between parametric tests.
        
        In production: Use real test data from STDF (IDDQ, Vth, frequency, etc.)
        """
        from scipy.stats import pearsonr
        
        # Mock parametric test data
        np.random.seed(42)
        n_samples = 500
        
        # Simulate correlated tests (e.g., IDDQ and Vth)
        iddq = np.random.lognormal(3, 0.5, n_samples)
        vth = 0.7 + 0.05 * np.log(iddq) + np.random.normal(0, 0.02, n_samples)
        
        # Calculate correlation
        corr_coef, p_value = pearsonr(iddq, vth)
        
        logger.info(
            "pearson_correlation_calculated",
            test1="IDDQ_25C",
            test2="Vth_nom",
            correlation=float(corr_coef),
            p_value=float(p_value),
        )
        
        return {
            "test1": "IDDQ_25C",
            "test2": "Vth_nom",
            "correlation": float(corr_coef),
            "p_value": float(p_value),
            "strength": "strong" if abs(corr_coef) > 0.7 else "moderate" if abs(corr_coef) > 0.4 else "weak",
            "significance": "significant" if p_value < 0.05 else "not significant",
            "description": f"{'Strong' if abs(corr_coef) > 0.7 else 'Moderate'} correlation (r={corr_coef:.2f}, p={p_value:.4f})",
            "confidence": 0.88 if p_value < 0.05 else 0.55,
        }
    
    def _spearman_correlation(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Spearman rank correlation (handles non-linear relationships).
        
        In production: Use for monotonic but non-linear relationships
        """
        from scipy.stats import spearmanr
        
        # Mock data with monotonic relationship
        np.random.seed(42)
        n_samples = 500
        
        # Simulate non-linear relationship
        test1 = np.random.exponential(2, n_samples)
        test2 = np.sqrt(test1) + np.random.normal(0, 0.3, n_samples)
        
        # Calculate Spearman correlation
        corr_coef, p_value = spearmanr(test1, test2)
        
        logger.info(
            "spearman_correlation_calculated",
            test1="FreqMax_125C",
            test2="Vdd_min",
            correlation=float(corr_coef),
            p_value=float(p_value),
        )
        
        return {
            "test1": "FreqMax_125C",
            "test2": "Vdd_min",
            "correlation": float(corr_coef),
            "p_value": float(p_value),
            "strength": "strong" if abs(corr_coef) > 0.7 else "moderate" if abs(corr_coef) > 0.4 else "weak",
            "description": f"Spearman correlation (ρ={corr_coef:.2f}, p={p_value:.4f})",
            "confidence": 0.82 if p_value < 0.05 else 0.50,
        }
    
    def _feature_importance(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate feature importance using Random Forest.
        
        In production: Train RF classifier on pass/fail with parametric tests as features
        """
        from sklearn.ensemble import RandomForestClassifier
        
        # Mock dataset: 500 samples, 5 parametric tests
        np.random.seed(42)
        n_samples = 500
        
        # Generate features (parametric tests)
        iddq = np.random.lognormal(3, 0.5, n_samples)
        vth = np.random.normal(0.7, 0.05, n_samples)
        freq = np.random.normal(1000, 50, n_samples)
        vdd = np.random.normal(1.8, 0.05, n_samples)
        temp_coef = np.random.normal(50, 10, n_samples)
        
        X = np.column_stack([iddq, vth, freq, vdd, temp_coef])
        
        # Generate target (bin pass/fail) - make IDDQ most important
        y = (iddq > np.percentile(iddq, 80)).astype(int)
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        feature_names = ["IDDQ_25C", "Vth_nom", "FreqMax_125C", "Vdd_min", "TempCoef"]
        importances = rf.feature_importances_
        
        # Sort by importance
        sorted_idx = np.argsort(importances)[::-1]
        
        logger.info(
            "feature_importance_calculated",
            top_feature=feature_names[sorted_idx[0]],
            importance=float(importances[sorted_idx[0]]),
        )
        
        return {
            "method": "Random Forest Feature Importance",
            "features": [
                {
                    "name": feature_names[i],
                    "importance": float(importances[i]),
                    "rank": int(np.where(sorted_idx == i)[0][0] + 1),
                }
                for i in range(len(feature_names))
            ],
            "top_feature": feature_names[sorted_idx[0]],
            "top_importance": float(importances[sorted_idx[0]]),
            "description": f"Top predictor: {feature_names[sorted_idx[0]]} (importance={importances[sorted_idx[0]]:.3f})",
            "confidence": 0.85,
        }
    
    def _time_series_correlation(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lot-to-lot trends and correlations.
        
        In production: Use historical lot data to detect trends
        """
        # Mock lot-to-lot bin rate data
        np.random.seed(42)
        n_lots = 30
        
        # Simulate increasing trend in bin rate
        lot_numbers = np.arange(1, n_lots + 1)
        bin_rates = 0.10 + 0.002 * lot_numbers + np.random.normal(0, 0.01, n_lots)
        
        # Calculate trend
        from scipy.stats import linregress
        slope, intercept, r_value, p_value, std_err = linregress(lot_numbers, bin_rates)
        
        trend = "increasing" if slope > 0 else "decreasing"
        
        logger.info(
            "time_series_correlation_analyzed",
            slope=float(slope),
            r_squared=float(r_value**2),
            p_value=float(p_value),
            trend=trend,
        )
        
        return {
            "analysis": "Lot-to-Lot Trend Analysis",
            "slope": float(slope),
            "r_squared": float(r_value**2),
            "p_value": float(p_value),
            "trend": trend,
            "description": f"Bin rate shows {trend} trend (slope={slope:.4f}, R²={r_value**2:.3f})",
            "confidence": 0.90 if p_value < 0.05 else 0.60,
            "recommendation": "Investigate process drift or equipment degradation" if p_value < 0.05 else None,
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute correlation analysis workflow.
        
        Args:
            state: Workflow state containing test data
        
        Returns:
            Updated state with correlations
        """
        logger.info(
            "correlation_hunter_starting",
            session_id=state.get("session_id"),
            lot_id=state.get("lot_id"),
        )
        
        # Run correlation analyses
        correlations = []
        
        # Pearson correlation
        pearson_result = self._pearson_correlation({})
        correlations.append(pearson_result)
        
        # Spearman correlation
        spearman_result = self._spearman_correlation({})
        correlations.append(spearman_result)
        
        # Feature importance
        feature_result = self._feature_importance({})
        correlations.append(feature_result)
        
        # Time series
        time_series_result = self._time_series_correlation({})
        correlations.append(time_series_result)
        
        # Use LLM to synthesize correlation findings
        synthesis_prompt = f"""
        You are a correlation analyst reviewing semiconductor test parameter relationships.
        
        Correlation Analysis Results:
        {correlations}
        
        Lot: {state.get('lot_id')}
        Wafer: {state.get('wafer_id')}
        Bin: {state.get('bin')}
        
        Provide a concise summary of the key correlations discovered and their implications.
        Focus on significant correlations (p < 0.05) and high feature importance.
        Suggest which test parameters are most predictive of failures.
        """
        
        try:
            response = self.llm.invoke(synthesis_prompt)
            synthesis = response.content
        except Exception as e:
            logger.error("llm_synthesis_failed", error=str(e))
            # Fallback to top correlation
            top_corr = max(correlations, key=lambda c: c.get("confidence", 0))
            synthesis = f"{top_corr.get('description', 'Correlation analysis completed')}"
        
        # Update state
        state["correlations"] = correlations
        
        if "messages" not in state:
            state["messages"] = []
        
        state["messages"].append({
            "agent": "CorrelationHunter",
            "finding": synthesis,
            "confidence": max([c.get("confidence", 0.5) for c in correlations]),
            "details": correlations,
        })
        
        logger.info(
            "correlation_hunter_completed",
            session_id=state.get("session_id"),
            correlations_count=len(correlations),
        )
        
        return state


# Singleton instance
correlation_hunter_agent = CorrelationHunterAgent()
