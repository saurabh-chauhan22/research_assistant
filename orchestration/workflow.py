"""
Workflow Orchestration Module

Implements the sequential workflow coordination using AutoGen GroupChat
to manage multi-agent collaboration.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

from autogen.agentchat.groupchat import GroupChat, GroupChatManager

from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.writing_agent import WritingAgent

logger = logging.getLogger("research_assistant")


class ResearchWorkflow:
    """
    Orchestrates the multi-agent research workflow using AutoGen GroupChat.
    
    Manages sequential execution: User Query → Research Agent → 
    Analysis Agent → Writing Agent → Final Output
    """
    
    def __init__(
        self,
        research_agent: ResearchAgent,
        analysis_agent: AnalysisAgent,
        writing_agent: WritingAgent,
        workflow_config: Dict[str, Any]
    ):
        """
        Initialize Research Workflow.
        
        Args:
            research_agent: Initialized Research Agent instance
            analysis_agent: Initialized Analysis Agent instance
            writing_agent: Initialized Writing Agent instance
            workflow_config: Workflow configuration dictionary
        """
        self.research_agent = research_agent
        self.analysis_agent = analysis_agent
        self.writing_agent = writing_agent
        self.config = workflow_config
        
        # Extract agents
        self.agents = [
            research_agent.get_agent(),
            analysis_agent.get_agent(),
            writing_agent.get_agent()
        ]
        
        # Initialize GroupChat
        self.group_chat = None
        self.manager = None
        self._initialize_group_chat()
        
        # Conversation history tracking
        self.conversation_history: List[Dict[str, Any]] = []
        
        logger.info("Research Workflow initialized")
    
    def _initialize_group_chat(self) -> None:
        """Initialize GroupChat and GroupChatManager with configured settings."""
        # Define speaking order: Research → Analysis → Writing
        # Allow Research to speak first, then Analysis, then Writing
        self.group_chat = GroupChat(
            agents=self.agents,
            messages=[],
            max_round=self.config.get("max_rounds", 10),
            speaker_selection_method="round_robin"  # Sequential order
        )
        
        llm_config = {
            # "model": "gpt-4",
            "config_list": [
                {
                    "model": "gpt-4",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                }
            ]
        }
        
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=llm_config,
            human_input_mode=self.config.get("human_input_mode", "NEVER")
        )
        
        logger.info("GroupChat initialized with sequential workflow")
    
    def execute(
        self,
        user_query: str,
        save_history: bool = True
    ) -> Dict[str, Any]:
        """
        Execute the complete research workflow.
        
        Args:
            user_query: User's research query
            save_history: Whether to save conversation history
            
        Returns:
            Dictionary containing final output and metadata
        """
        start_time = datetime.now()
        logger.info(f"Starting research workflow for query: {user_query}")
        
        try:
            # Step 1: Research Agent gathers information
            logger.info("Step 1: Research Agent gathering information")
            research_response = self.research_agent.process_query(user_query)
            research_response = self._ensure_str(research_response)
            self._log_interaction("ResearchAgent", user_query, research_response)
            
            # Step 2: Analysis Agent synthesizes findings
            logger.info("Step 2: Analysis Agent synthesizing findings")
            analysis_response = self.analysis_agent.analyze_research(research_response)
            analysis_response = self._ensure_str(analysis_response)
            self._log_interaction("AnalysisAgent", research_response, analysis_response)
            
            # Step 3: Writing Agent produces final output
            logger.info("Step 3: Writing Agent generating final output")
            
            # Extract sources from research response if possible
            sources = self._extract_sources(research_response)
            
            final_output = self.writing_agent.write_final_output(
                analysis=analysis_response,
                original_query=user_query,
                sources=sources
            )
            final_output = self._ensure_str(final_output)
            self._log_interaction("WritingAgent", analysis_response, final_output)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                "query": user_query,
                "final_output": final_output,
                "research_findings": research_response,
                "analysis": analysis_response,
                "processing_time_seconds": processing_time,
                "timestamp": end_time.isoformat(),
                "sources_count": len(sources) if sources else 0,
                "conversation_history": self.conversation_history if save_history else []
            }
            
            logger.info(f"Workflow completed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in workflow execution: {str(e)}")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                "query": user_query,
                "error": str(e),
                "processing_time_seconds": processing_time,
                "timestamp": end_time.isoformat()
            }
    
    def _log_interaction(
        self,
        agent_name: str,
        input_message: str,
        output_message: str
    ) -> None:
        """
        Log agent interaction for history tracking.
        
        Args:
            agent_name: Name of the agent
            input_message: Input message to the agent
            output_message: Output message from the agent
        """
        input_str = self._ensure_str(input_message)
        output_str = self._ensure_str(output_message)
        interaction = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "input": input_str[:500] + "..." if len(input_str) > 500 else input_str,
            "output": output_str[:500] + "..." if len(output_str) > 500 else output_str,
            "input_length": len(input_str),
            "output_length": len(output_str)
        }
        self.conversation_history.append(interaction)
        logger.debug(f"Logged interaction: {agent_name}")
    
    @staticmethod
    def _ensure_str(value: Any) -> str:
        """Ensure value is a string (agents may return dict from generate_reply)."""
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return value.get("content", str(value))
        return str(value)

    def _extract_sources(self, research_response: str) -> List[Dict[str, str]]:
        """
        Extract source information from research response.
        
        Args:
            research_response: Research agent's response string
            
        Returns:
            List of source dictionaries
        """
        research_response = self._ensure_str(research_response)
        sources = []
        # Simple extraction - look for URL patterns
        import re
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, research_response)
        
        # Try to extract titles and URLs together
        lines = research_response.split('\n')
        current_source = {}
        
        for line in lines:
            if line.strip().startswith('[') and ']' in line:
                # Potential source line
                if 'URL:' in line or 'http' in line:
                    if 'title' in current_source or 'url' in current_source:
                        sources.append(current_source.copy())
                        current_source = {}
                if 'http' in line:
                    url_match = re.search(url_pattern, line)
                    if url_match:
                        current_source['url'] = url_match.group()
            elif 'URL:' in line:
                url_match = re.search(url_pattern, line)
                if url_match:
                    current_source['url'] = url_match.group()
            elif line.strip() and not line.startswith(' ') and ':' not in line[:20]:
                if not current_source.get('title'):
                    current_source['title'] = line.strip()
        
        if current_source:
            sources.append(current_source)
        
        return sources
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
