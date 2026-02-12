"""
Evaluation Metrics Module

Provides metrics tracking and quality assessment for the research assistant system.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger("research_assistant")


class EvaluationMetrics:
    """
    Tracks and calculates evaluation metrics for research queries.
    
    Metrics include:
    - Query processing time
    - Source count and diversity
    - Output length and quality
    - Comparison with baseline
    """
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics_history: List[Dict[str, Any]] = []
    
    def record_query(
        self,
        query: str,
        result: Dict[str, Any],
        baseline_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record metrics for a processed query.
        
        Args:
            query: User query
            result: Result dictionary from workflow execution
            baseline_result: Optional baseline result for comparison
            
        Returns:
            Dictionary containing calculated metrics
        """
        metrics = {
            "query": query,
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
            "processing_time_seconds": result.get("processing_time_seconds", 0),
            "sources_count": result.get("sources_count", 0),
            "output_length": len(result.get("final_output", "")),
            "research_length": len(result.get("research_findings", "")),
            "analysis_length": len(result.get("analysis", "")),
        }
        
        # Calculate quality scores
        quality = QualityAssessment.assess(result)
        metrics.update(quality)
        
        # Compare with baseline if provided
        if baseline_result:
            comparison = self._compare_with_baseline(result, baseline_result)
            metrics["baseline_comparison"] = comparison
        
        self.metrics_history.append(metrics)
        logger.info(f"Recorded metrics for query: {query}")
        
        return metrics
    
    def _compare_with_baseline(
        self,
        multi_agent_result: Dict[str, Any],
        baseline_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare multi-agent result with baseline single-agent result.
        
        Args:
            multi_agent_result: Result from multi-agent system
            baseline_result: Result from baseline system
            
        Returns:
            Comparison metrics
        """
        comparison = {
            "time_improvement": (
                baseline_result.get("processing_time_seconds", 0) -
                multi_agent_result.get("processing_time_seconds", 0)
            ),
            "sources_improvement": (
                multi_agent_result.get("sources_count", 0) -
                baseline_result.get("sources_count", 0)
            ),
            "output_length_diff": (
                len(multi_agent_result.get("final_output", "")) -
                len(baseline_result.get("final_output", ""))
            ),
            "quality_score_diff": (
                multi_agent_result.get("quality_score", 0) -
                baseline_result.get("quality_score", 0)
            )
        }
        
        return comparison
    
    def generate_report(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate evaluation report from all recorded metrics.
        
        Args:
            output_path: Optional path to save report as JSON
            
        Returns:
            Dictionary containing aggregated report
        """
        if not self.metrics_history:
            return {"error": "No metrics recorded"}
        
        total_queries = len(self.metrics_history)
        avg_processing_time = sum(
            m["processing_time_seconds"] for m in self.metrics_history
        ) / total_queries
        avg_sources = sum(
            m["sources_count"] for m in self.metrics_history
        ) / total_queries
        avg_output_length = sum(
            m["output_length"] for m in self.metrics_history
        ) / total_queries
        avg_quality_score = sum(
            m.get("quality_score", 0) for m in self.metrics_history
        ) / total_queries
        
        report = {
            "summary": {
                "total_queries": total_queries,
                "average_processing_time_seconds": avg_processing_time,
                "average_sources_count": avg_sources,
                "average_output_length": avg_output_length,
                "average_quality_score": avg_quality_score,
            },
            "detailed_metrics": self.metrics_history,
            "generated_at": datetime.now().isoformat()
        }
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Evaluation report saved to {output_path}")
        
        return report


class QualityAssessment:
    """
    Provides quality assessment scoring for research outputs.
    
    Assesses relevance, completeness, and coherence.
    """
    
    @staticmethod
    def assess(result: Dict[str, Any]) -> Dict[str, float]:
        """
        Assess quality of research result.
        
        Args:
            result: Result dictionary from workflow execution
            
        Returns:
            Dictionary with quality scores
        """
        final_output = result.get("final_output", "")
        research_findings = result.get("research_findings", "")
        analysis = result.get("analysis", "")
        sources_count = result.get("sources_count", 0)
        
        # Relevance score (based on output length and content quality)
        relevance_score = min(1.0, len(final_output) / 2000) if final_output else 0.0
        
        # Completeness score (based on sources and analysis depth)
        completeness_score = min(1.0, sources_count / 5.0) * 0.5
        completeness_score += min(1.0, len(analysis) / 1500) * 0.5
        
        # Coherence score (based on structure and formatting)
        coherence_indicators = [
            "Executive Summary" in final_output or "Summary" in final_output,
            "Sources" in final_output or "References" in final_output,
            "[" in final_output and "]" in final_output,  # Citations present
            len(final_output.split("\n")) > 10  # Multiple paragraphs
        ]
        coherence_score = sum(coherence_indicators) / len(coherence_indicators)
        
        # Overall quality score (weighted average)
        quality_score = (
            relevance_score * 0.3 +
            completeness_score * 0.4 +
            coherence_score * 0.3
        )
        
        return {
            "relevance_score": round(relevance_score, 3),
            "completeness_score": round(completeness_score, 3),
            "coherence_score": round(coherence_score, 3),
            "quality_score": round(quality_score, 3)
        }
