"""
Research Assistant Multi-Agent System - Agents Module

This module contains the three specialized agents:
- ResearchAgent: Information gathering and source retrieval
- AnalysisAgent: Synthesis and reasoning on research outputs
- WritingAgent: Formatted, coherent final output generation
"""

from .research_agent import ResearchAgent
from .analysis_agent import AnalysisAgent
from .writing_agent import WritingAgent

__all__ = ['ResearchAgent', 'AnalysisAgent', 'WritingAgent']
