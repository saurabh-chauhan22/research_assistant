"""
Writing Agent Module

Implements the Writing Agent responsible for producing formatted,
coherent final output with proper citations and structure.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
import autogen
import logging

logger = logging.getLogger("research_assistant")


class WritingAgent:
    """
    Writing Agent specialized in producing formatted, coherent final output.
    
    Transforms analysis into clear, well-structured prose with proper
    citations, markdown formatting, and executive summaries.
    """
    
    def __init__(self, config: Dict[str, Any], prompt: str):
        """
        Initialize Writing Agent.
        
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
            "temperature": self.config.get("temperature", 0.7),
            "tools": [],
            "config_list": [
                {
                    "model": self.config.get("model", "gpt-4"),
                    "api_key": os.getenv("OPENAI_API_KEY"),
                }
            ]
        }
        
        self.agent = autogen.ConversableAgent(
            name=self.config.get("name", "WritingAgent"),
            system_message=self.prompt,
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
        
        logger.info("Writing Agent initialized successfully")
    
    def write_final_output(
        self,
        analysis: str,
        original_query: str,
        sources: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate final formatted output from analysis.
        
        Args:
            analysis: Analytical summary from Analysis Agent
            original_query: Original user query
            sources: Optional list of source dictionaries with title, url, content
            
        Returns:
            Formatted final output with executive summary, detailed findings, and sources
        """
        try:
            logger.info("Writing Agent generating final output")
            
            writing_query = (
                f"Please transform the following analysis into a well-structured research report.\n"
                f"Original Query: {original_query}\n\n"
                f"Analysis to Format:\n{analysis}\n\n"
                f"Requirements:\n"
                f"1. Create an Executive Summary section highlighting key findings\n"
                f"2. Create a Detailed Findings section with comprehensive analysis\n"
                f"3. Include inline citations [1], [2], etc. throughout the text\n"
                f"4. Create a Sources section with numbered list of all sources\n"
                f"5. Use markdown formatting (headers, lists, emphasis)\n"
                f"6. Maintain objective, factual tone\n"
                f"7. Ensure clarity and professional presentation\n"
            )
            
            if sources:
                writing_query += f"\nAvailable Sources:\n"
                for idx, source in enumerate(sources, 1):
                    writing_query += f"[{idx}] {source.get('title', 'Unknown')} - {source.get('url', 'N/A')}\n"
            
            try:
                response = self.agent.generate_reply(
                    messages=[{"role": "user", "content": writing_query}]
                )
            except (AttributeError, TypeError):
                response = self.agent.generate_reply(
                    messages=[{"role": "user", "content": writing_query}]
                )
            # Ensure string (generate_reply can return dict in some AutoGen versions)
            if isinstance(response, str):
                pass
            elif isinstance(response, dict):
                response = response.get("content", str(response))
            else:
                response = str(response)
            
            logger.info("Writing Agent completed final output")
            return response
            
        except Exception as e:
            logger.error(f"Error in Writing Agent: {str(e)}")
            return f"Error generating final output: {str(e)}"
    
    def get_agent(self):
        """Get the underlying AutoGen agent instance."""
        return self.agent
