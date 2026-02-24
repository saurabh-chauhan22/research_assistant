"""
FastAPI search endpoint: accepts a query string and returns research assistant results.
"""
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, Query
from redis import Redis


from main import (
    process_query,
    load_config,
    load_prompts,
    initialize_agents,
    validate_environment,
)
from orchestration.workflow import ResearchWorkflow
from utils.cache import QueryCache

logger = logging.getLogger("research_assistant")

router = APIRouter()

_cache_url = os.getenv("REDIS_URL")
cache = QueryCache(Redis.from_url(_cache_url)) if _cache_url else None


_workflow: ResearchWorkflow | None = None


def _get_workflow() -> ResearchWorkflow:
    """Build ResearchWorkflow with config and agents (same as main.py)."""
    project_root = Path(__file__).resolve().parent.parent
    config_dir = project_root / "config"
    config = load_config(config_dir / "agent_configs.yaml")
    prompts = load_prompts(config_dir / "prompts.yaml")
    research_agent, analysis_agent, writing_agent = initialize_agents(
        config, prompts
    )
    return ResearchWorkflow(
        research_agent=research_agent,
        analysis_agent=analysis_agent,
        writing_agent=writing_agent,
        workflow_config=config["workflow"],
    )


def get_workflow() -> ResearchWorkflow:
    """Return cached workflow, initializing once."""
    global _workflow
    if _workflow is None:
        validate_environment()
        _workflow = _get_workflow()
    return _workflow


@router.get("/search", summary="Research search",description="Run the research assistant on the given query and return the result.",response_model=Dict[str, Any])
async def search(query: str = Query(..., min_length=1)):
    """
    Execute a search/research query using the research assistant.
    Accepts a user query string and returns the research result.
    """
    logger.info("Executing search query: %s", query[:80])
    result = None
    try:
        workflow = get_workflow()
        if cache is not None and cache.is_cache_available:
            result = cache.get_cached_result(query)
            logger.info("Getting cached result ")
            if result is not None:
                return result
        result = await asyncio.to_thread(process_query, query, workflow, None, True)
        if cache is not None and cache.is_cache_available:
            cache.set_cached_result(query, result)
        return result
    except Exception as e:
        logger.exception("Error executing search query")
        return {"error": str(e), "query": query}

