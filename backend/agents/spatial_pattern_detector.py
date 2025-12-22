"""
Spatial Pattern Detector Agent - Analyzes wafer map patterns using computer vision.
"""
from typing import Dict, Any, List, Tuple
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
import structlog
import numpy as np

from core.config import settings

logger = structlog.get_logger(__name__)


class SpatialPatternDetectorAgent:
    """
    Agent specialized in detecting spatial patterns on wafer maps.
    
    Capabilities:
    - Edge effect detection
    - Ring/donut pattern detection
    - Cluster detection
    - Radial/angular pattern detection
    - Random vs systematic failure classification
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY,
        )
        self.tools = [
            Tool(
                name="edge_effect_detection",
                func=self._edge_effect_detection,
                description="Detect if failures are concentrated at wafer edges",
            ),
            Tool(
                name="cluster_detection",
                func=self._cluster_detection,
                description="Detect failure clusters using DBSCAN",
            ),
            Tool(
                name="radial_pattern_detection",
                func=self._radial_pattern_detection,
                description="Detect radial/ring patterns from wafer center",
            ),
            Tool(
                name="pattern_classification",
                func=self._pattern_classification,
                description="Classify overall pattern type (edge, ring, cluster, random)",
            ),
        ]
    
    def _edge_effect_detection(self, wafer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect edge effect using distance from wafer center.
        
        In production: Use real wafer coordinates and calculate radial distance
        """
        # Mock wafer map: 300mm wafer, 20x20 grid
        wafer_radius = 150  # mm
        grid_size = 20
        
        # Generate mock die coordinates
        np.random.seed(42)
        failures = []
        for i in range(100):  # 100 failures
            # Bias failures toward edge
            angle = np.random.uniform(0, 2 * np.pi)
            radius = np.random.uniform(100, 150)  # Edge region
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            failures.append((x, y))
        
        # Calculate distance from center for each failure
        distances = [np.sqrt(x**2 + y**2) for x, y in failures]
        avg_distance = np.mean(distances)
        
        # Edge effect if average distance > 80% of wafer radius
        edge_threshold = 0.8 * wafer_radius
        edge_effect = avg_distance > edge_threshold
        confidence = (avg_distance / wafer_radius) if edge_effect else 0.5
        
        logger.info(
            "edge_effect_detected",
            avg_distance=float(avg_distance),
            wafer_radius=wafer_radius,
            edge_effect=edge_effect,
            confidence=float(confidence),
        )
        
        return {
            "pattern": "edge_effect" if edge_effect else "no_edge_effect",
            "confidence": float(min(confidence, 0.95)),
            "avg_failure_distance": float(avg_distance),
            "wafer_radius": wafer_radius,
            "description": "Failures concentrated at wafer periphery (>80% radius)" if edge_effect else "No edge effect detected",
            "recommendation": "Investigate package stress, thermal gradients, or edge die thinning" if edge_effect else None,
        }
    
    def _cluster_detection(self, wafer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect failure clusters using DBSCAN.
        
        In production: Use sklearn.cluster.DBSCAN on real die coordinates
        """
        from sklearn.cluster import DBSCAN
        
        # Mock failure coordinates
        np.random.seed(42)
        failures = np.random.randn(100, 2) * 30  # 100 failures scattered
        
        # Add a dense cluster
        cluster_center = np.array([[50, 50]])
        cluster_points = cluster_center + np.random.randn(30, 2) * 5
        all_failures = np.vstack([failures, cluster_points])
        
        # DBSCAN clustering
        clustering = DBSCAN(eps=10, min_samples=5).fit(all_failures)
        n_clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
        
        logger.info(
            "cluster_detection_completed",
            n_clusters=n_clusters,
            n_failures=len(all_failures),
        )
        
        return {
            "pattern": "cluster" if n_clusters > 0 else "scattered",
            "n_clusters": n_clusters,
            "confidence": 0.85 if n_clusters > 0 else 0.50,
            "description": f"{n_clusters} distinct failure clusters detected" if n_clusters > 0 else "Failures are scattered (no clear clusters)",
            "recommendation": "Investigate localized defects (particle, scratch, lithography issue)" if n_clusters > 0 else None,
        }
    
    def _radial_pattern_detection(self, wafer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect radial/ring patterns from wafer center.
        
        In production: Use Hough Transform or radial binning
        """
        # Mock wafer with ring pattern at 100mm radius
        np.random.seed(42)
        ring_radius = 100
        failures = []
        
        for i in range(80):
            angle = np.random.uniform(0, 2 * np.pi)
            radius = np.random.normal(ring_radius, 10)  # Ring with 10mm std
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            failures.append((x, y))
        
        # Calculate radial distribution
        distances = [np.sqrt(x**2 + y**2) for x, y in failures]
        std_distance = np.std(distances)
        mean_distance = np.mean(distances)
        
        # Ring pattern if low std and mean > 50mm
        is_ring = std_distance < 15 and mean_distance > 50
        
        logger.info(
            "radial_pattern_analyzed",
            mean_distance=float(mean_distance),
            std_distance=float(std_distance),
            is_ring=is_ring,
        )
        
        return {
            "pattern": "ring" if is_ring else "no_ring",
            "confidence": 0.88 if is_ring else 0.55,
            "ring_radius": float(mean_distance) if is_ring else None,
            "description": f"Ring pattern detected at {mean_distance:.1f}mm radius" if is_ring else "No clear ring pattern",
            "recommendation": "Investigate process uniformity (implant, etch, CMP)" if is_ring else None,
        }
    
    def _pattern_classification(self, wafer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify overall spatial pattern using OpenCV contours.
        
        In production: Use real wafer map image
        """
        import cv2
        
        # Mock wafer map as binary image (300x300 pixels)
        wafer_map = np.zeros((300, 300), dtype=np.uint8)
        
        # Draw edge failures
        cv2.circle(wafer_map, (150, 150), 140, 255, 10)
        
        # Find contours
        contours, _ = cv2.findContours(wafer_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            
            # Classify based on circularity
            if circularity > 0.8:
                pattern_type = "ring"
            elif circularity < 0.5:
                pattern_type = "cluster"
            else:
                pattern_type = "edge_effect"
        else:
            pattern_type = "random"
        
        logger.info(
            "pattern_classified",
            pattern_type=pattern_type,
            circularity=float(circularity) if len(contours) > 0 else 0,
        )
        
        return {
            "pattern": pattern_type,
            "confidence": 0.82,
            "circularity": float(circularity) if len(contours) > 0 else 0,
            "description": f"Primary pattern: {pattern_type}",
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute spatial pattern detection workflow.
        
        Args:
            state: Workflow state containing wafer map path
        
        Returns:
            Updated state with spatial patterns
        """
        logger.info(
            "spatial_pattern_detector_starting",
            session_id=state.get("session_id"),
            wafer_map_path=state.get("wafer_map_path"),
        )
        
        # Run spatial analyses
        patterns = []
        
        # Edge effect detection
        edge_result = self._edge_effect_detection({})
        patterns.append(edge_result)
        
        # Cluster detection
        cluster_result = self._cluster_detection({})
        patterns.append(cluster_result)
        
        # Radial pattern detection
        radial_result = self._radial_pattern_detection({})
        patterns.append(radial_result)
        
        # Overall pattern classification
        classification_result = self._pattern_classification({})
        patterns.append(classification_result)
        
        # Use LLM to synthesize spatial findings
        synthesis_prompt = f"""
        You are a spatial pattern analyst reviewing semiconductor wafer map patterns.
        
        Spatial Pattern Analysis Results:
        {patterns}
        
        Lot: {state.get('lot_id')}
        Wafer: {state.get('wafer_id')}
        Bin: {state.get('bin')}
        
        Provide a concise summary of the spatial patterns detected and their implications.
        Focus on the most confident patterns (>0.8 confidence).
        Suggest potential root causes based on the spatial distribution.
        """
        
        try:
            response = self.llm.invoke(synthesis_prompt)
            synthesis = response.content
        except Exception as e:
            logger.error("llm_synthesis_failed", error=str(e))
            # Use highest confidence pattern as fallback
            top_pattern = max(patterns, key=lambda p: p.get("confidence", 0))
            synthesis = f"{top_pattern['description']} - {top_pattern.get('recommendation', 'Further analysis needed')}"
        
        # Update state
        state["spatial_patterns"] = patterns
        
        if "messages" not in state:
            state["messages"] = []
        
        state["messages"].append({
            "agent": "SpatialPatternDetector",
            "finding": synthesis,
            "confidence": max([p.get("confidence", 0.5) for p in patterns]),
            "details": patterns,
        })
        
        logger.info(
            "spatial_pattern_detector_completed",
            session_id=state.get("session_id"),
            patterns_count=len(patterns),
        )
        
        return state


# Singleton instance
spatial_pattern_detector_agent = SpatialPatternDetectorAgent()
