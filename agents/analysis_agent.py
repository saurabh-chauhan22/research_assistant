"""
Analysis Agent Module

Implements the Analysis Agent responsible for synthesis and reasoning
on research outputs from the Research Agent.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
import autogen
import logging

logger = logging.getLogger("research_assistant")


class AnalysisAgent:
    """
    Analysis Agent specialized in synthesis and reasoning on research outputs.
    
    Receives raw research data, identifies patterns, contradictions, and
    key insights across sources, and generates analytical summaries with
    confidence assessments.
    """
    
    def __init__(self, config: Dict[str, Any], prompt: str):
        """
        Initialize Analysis Agent.
        
        Args:
            config: Agent configuration dictionary
            prompt: System prompt for the agent
        """
        self.config = config
        self.prompt = prompt
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize the AutoGen ConversableAgent. No tools/functions - chat only."""
        # Do not pass 'functions'; use empty 'tools' so API gets tools=[] and never functions (avoids functions[0].name error)
        llm_config = {
            "temperature": self.config.get("temperature", 0.5),
            "tools": [],
            "config_list": [
                {
                    "model": self.config.get("model", "gpt-4"),
                    "api_key": os.getenv("OPENAI_API_KEY"),
                }
            ]
        }
        
        # Use ConversableAgent only - no function calling for analysis
        self.agent = autogen.ConversableAgent(
            name=self.config.get("name", "AnalysisAgent"),
            system_message=self.prompt,
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
        
        logger.info("Analysis Agent initialized successfully")
    
    def analyze_research(self, research_findings: str) -> str:
        """
        Analyze research findings and generate synthesis.
        
        Args:
            research_findings: Raw research findings from Research Agent
            
        Returns:
            Analytical summary with patterns, insights, and confidence assessments
        """
        try:
            logger.info("Analysis Agent processing research findings")
            
            analysis_query = (
                f"Please analyze the following research findings and provide:\n"
                f"1. Key insights and patterns identified\n"
                f"2. Areas of consensus and disagreement\n"
                f"3. Confidence assessments for major claims (high/medium/low)\n"
                f"4. Critical evaluation of source reliability\n"
                f"5. Synthesis of findings into coherent analytical summary\n\n"
                f"Research Findings:\n{research_findings}"
            )
            
            try:
                response = self.agent.generate_reply(
                    messages=[{"role": "user", "content": analysis_query}]
                )
            except (AttributeError, TypeError):
                response = self.get_agent().generate_reply(
                    messages=[{"role": "user", "content": analysis_query}]
                )
            # Ensure string (generate_reply can return dict in some AutoGen versions)
            if isinstance(response, str):
                pass
            elif isinstance(response, dict):
                response = response.get("content", str(response))
            else:
                response = str(response)
            
            logger.info("Analysis Agent completed analysis")
            return response
            
        except Exception as e:
            logger.error(f"Error in Analysis Agent: {str(e)}")
            return f"Error during analysis: {str(e)}"
    
    def get_agent(self):
        """Get the underlying AutoGen agent instance."""
        return self.agent
