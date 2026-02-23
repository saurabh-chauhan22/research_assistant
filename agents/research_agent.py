"""
Research Agent Module

Implements the Research Agent responsible for information gathering
and source retrieval using Tavily Search API.
"""

import os
from typing import Dict, List, Any, Optional
import logging
import autogen
from utils.api_client import TavilyAPIClient



logger = logging.getLogger("research_assistant")


class ResearchAgent:
    """
    Research Agent specialized in information gathering and source retrieval.
    
    Uses Tavily Search API to find relevant sources and extract structured
    information with proper citations.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        prompt: str,
        tavily_client: Optional[TavilyAPIClient] = None
    ):
        """
        Initialize Research Agent.
        
        Args:
            config: Agent configuration dictionary
            prompt: System prompt for the agent
            tavily_client: Optional Tavily API client instance
        """
        self.config = config
        self.prompt = prompt
        self.tavily_client = tavily_client or TavilyAPIClient()
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """Initialize the AutoGen ConversableAgent with function calling."""
        # Define search function for the agent
        def search_research(query: str) -> str:
            """
            Execute a research search query using Tavily API.
            
            Args:
                query: The research query to search for
                
            Returns:
                Formatted string with search results and sources
            """
            try:
                logger.info(f"Research Agent executing search: {query}")
                max_results = self.config.get("max_sources", 5)
                search_results = self.tavily_client.search(
                    query=query,
                    max_results=max_results
                )
                
                # Format results for the agent
                formatted_results = self._format_search_results(search_results)
                logger.info(f"Research Agent found {len(search_results['results'])} sources")
                return formatted_results
                
            except Exception as e:
                logger.error(f"Search failed in Research Agent: {str(e)}")
                return f"Error: Unable to complete search. {str(e)}"
        
        llm_config = {
            "temperature": self.config.get("temperature", 0.3),
            "config_list": [
                {
                    "model": self.config.get("model", "gpt-4"),
                    "api_key": os.getenv("OPENAI_API_KEY"),
                }
            ]
        }
        
        try:
            self.agent = autogen.AssistantAgent(
                name=self.config.get("name", "ResearchAgent"),
                system_message=self.prompt,
                llm_config=llm_config,
            )
        except AttributeError:
            # Fallback for older versions
            self.agent = autogen.ConversableAgent(
                name=self.config.get("name", "ResearchAgent"),
                system_message=self.prompt,
                llm_config=llm_config,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
            )
        
        # Register the function for execution
        try:
            self.agent.register_for_llm(name="search_research", description="Execute a web search to gather research information and sources.")(search_research)
            self.agent.register_for_execution(name="search_research")(search_research)
        except AttributeError:
            # Fallback: use function_map for older versions
            if hasattr(self.agent, 'function_map'):
                self.agent.function_map = {"search_research": search_research}
        
        logger.info("Research Agent initialized successfully")
    
    def _format_search_results(self, search_results: Dict[str, Any]) -> str:
        """
        Format search results into a structured string for agent consumption.
        
        Args:
            search_results: Dictionary containing search results from Tavily API
            
        Returns:
            Formatted string with research findings
        """
        if not search_results.get("results"):
            return "No relevant sources found for this query."
        
        formatted = f"Research Findings for: {search_results['query']}\n"
        formatted += f"Search executed at: {search_results['timestamp']}\n"
        formatted += f"Total sources found: {search_results['total_results']}\n\n"
        
        formatted += "SOURCES:\n"
        for idx, result in enumerate(search_results["results"], 1):
            formatted += f"\n[{idx}] {result.title}\n"
            formatted += f"URL: {result.url}\n"
            formatted += f"Content: {result.content[:500]}...\n"
            if result.score:
                formatted += f"Relevance Score: {result.score:.3f}\n"
        
        if search_results.get("answer"):
            formatted += f"\n\nAI-Generated Summary:\n{search_results['answer']}\n"
        
        formatted += "\n---\n"
        formatted += "Please analyze these sources and provide structured research findings."
        
        return formatted
    
    def process_query(self, query: str) -> str:
        """
        Process a research query and return findings.
        Runs Tavily search directly so we always have real data for downstream agents.
        """
        try:
            logger.info(f"Research Agent processing query: {query}")
            max_results = self.config.get("max_sources", 5)

            # 1) Run Tavily search directly (tool is never invoked in single generate_reply)
            try:
                logger.info(f"Research Agent executing search: {query}")
                search_results = self.tavily_client.search(
                    query=query,
                    max_results=max_results
                )
                formatted = self._format_search_results(search_results)
                num_sources = len(search_results.get("results") or [])
                logger.info(f"Research Agent found {num_sources} sources")
            except Exception as e:
                logger.error(f"Search failed in Research Agent: {str(e)}")
                formatted = f"Error: Unable to complete search. {str(e)}"

            # 2) Optionally ask LLM to structure/summarize (single turn, no tool call)
            if formatted and not formatted.strip().startswith("Error:"):
                try:
                    llm_message = (
                        f"Raw search results for query: \"{query}\". "
                        "Provide a concise structured summary with key facts and source attributions [1], [2]. Keep URLs.\n\n"
                        f"{formatted}"
                    )
                    response = self.agent.generate_reply(
                        messages=[{"role": "user", "content": llm_message}]
                    )
                    if isinstance(response, str) and response.strip():
                        return response
                    if isinstance(response, dict):
                        content = response.get("content") or response.get("text")
                        if content and isinstance(content, str) and content.strip():
                            return content
                except Exception as e:
                    logger.warning(f"LLM structuring failed, using raw results: {e}")
            return formatted
        except Exception as e:
            logger.error(f"Error in Research Agent query processing: {str(e)}")
            return f"Error processing research query: {str(e)}"
    
    def get_agent(self):
        """Get the underlying AutoGen agent instance."""
        return self.agent
