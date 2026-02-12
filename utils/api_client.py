"""
Tavily API Client Module

Handles communication with Tavily Search API including error handling,
retry logic with exponential backoff, and response parsing.
"""

import os
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger("research_assistant")


@dataclass
class SearchResult:
    """Structured representation of a search result."""
    title: str
    url: str
    content: str
    score: Optional[float] = None
    published_date: Optional[str] = None


class TavilyAPIClient:
    """
    Client for interacting with Tavily Search API.
    
    Implements retry logic with exponential backoff and comprehensive
    error handling for production use.
    """
    
    BASE_URL = "https://api.tavily.com/search"
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """
        Initialize Tavily API client.
        
        Args:
            api_key: Tavily API key. If None, reads from TAVILY_API_KEY env var
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key not provided. Set TAVILY_API_KEY environment variable."
            )
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = False,
        include_raw_content: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a search query using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_depth: Search depth ("basic" or "advanced")
            include_answer: Whether to include AI-generated answer
            include_raw_content: Whether to include raw content
            
        Returns:
            Dictionary containing search results and metadata
            
        Raises:
            requests.RequestException: If API request fails after retries
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Executing Tavily search (attempt {attempt + 1}/{self.max_retries}): {query}")
                response = self.session.post(
                    self.BASE_URL,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Structure the response
                results = []
                for result in data.get("results", []):
                    search_result = SearchResult(
                        title=result.get("title", ""),
                        url=result.get("url", ""),
                        content=result.get("content", ""),
                        score=result.get("score"),
                        published_date=result.get("published_date")
                    )
                    results.append(search_result)
                
                return {
                    "query": query,
                    "results": results,
                    "answer": data.get("answer", ""),
                    "timestamp": datetime.now().isoformat(),
                    "total_results": len(results),
                    "query_used": query
                }
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error during search: {str(e)}")
                raise
        
        # Should not reach here, but handle edge case
        raise Exception("Search failed after all retry attempts")
    
    def search_with_fallback(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Execute search with graceful fallback on failure.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with results or empty structure if search fails
        """
        try:
            return self.search(query, max_results=max_results)
        except Exception as e:
            logger.error(f"Search failed with fallback: {str(e)}")
            return {
                "query": query,
                "results": [],
                "answer": "",
                "timestamp": datetime.now().isoformat(),
                "total_results": 0,
                "query_used": query,
                "error": str(e)
            }
