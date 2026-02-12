"""
Research Assistant Multi-Agent System - Main Entry Point

Production-grade research assistant using Microsoft AutoGen framework
with three specialized agents: Research, Analysis, and Writing.
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.writing_agent import WritingAgent
from orchestration.workflow import ResearchWorkflow
from evaluation.metrics import EvaluationMetrics
from utils.logging_config import setup_logging
from utils.api_client import TavilyAPIClient

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging(log_level="INFO")


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration YAML file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise


def load_prompts(prompts_path: Path) -> Dict[str, str]:
    """
    Load agent prompts from YAML file.
    
    Args:
        prompts_path: Path to prompts YAML file
        
    Returns:
        Dictionary mapping agent names to prompts
    """
    try:
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
        logger.info(f"Prompts loaded from {prompts_path}")
        return prompts
    except Exception as e:
        logger.error(f"Error loading prompts: {str(e)}")
        raise


def initialize_agents(
    config: Dict[str, Any],
    prompts: Dict[str, str]
) -> tuple[ResearchAgent, AnalysisAgent, WritingAgent]:
    """
    Initialize all three agents with their configurations.
    
    Args:
        config: Configuration dictionary
        prompts: Prompts dictionary
        
    Returns:
        Tuple of (ResearchAgent, AnalysisAgent, WritingAgent)
    """
    logger.info("Initializing agents...")
    
    # Initialize Tavily API client
    try:
        tavily_client = TavilyAPIClient()
    except Exception as e:
        logger.error(f"Failed to initialize Tavily client: {str(e)}")
        raise
    
    # Initialize Research Agent
    research_agent = ResearchAgent(
        config=config["research_agent"],
        prompt=prompts["research_agent_prompt"],
        tavily_client=tavily_client
    )
    
    # Initialize Analysis Agent
    analysis_agent = AnalysisAgent(
        config=config["analysis_agent"],
        prompt=prompts["analysis_agent_prompt"]
    )
    
    # Initialize Writing Agent
    writing_agent = WritingAgent(
        config=config["writing_agent"],
        prompt=prompts["writing_agent_prompt"]
    )
    
    logger.info("All agents initialized successfully")
    return research_agent, analysis_agent, writing_agent


def validate_environment() -> None:
    """
    Validate that required environment variables are set.
    
    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set them in your .env file or environment."
        )


def process_query(
    query: str,
    workflow: ResearchWorkflow,
    metrics: Optional[EvaluationMetrics] = None,
    save_output: bool = True
) -> Dict[str, Any]:
    """
    Process a single research query through the workflow.
    
    Args:
        query: User's research query
        workflow: Initialized ResearchWorkflow instance
        metrics: Optional EvaluationMetrics instance for tracking
        save_output: Whether to save output to file
        
    Returns:
        Result dictionary with final output and metadata
    """
    logger.info(f"Processing query: {query}")
    
    # Execute workflow
    result = workflow.execute(user_query=query, save_history=True)
    
    # Record metrics if provided
    if metrics:
        metrics.record_query(query=query, result=result)
    
    # Save output if requested
    if save_output and "final_output" in result:
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = result["timestamp"].replace(":", "-").split(".")[0]
        output_file = output_dir / f"research_output_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Research Query: {query}\n\n")
            f.write(f"**Generated at:** {result['timestamp']}\n")
            f.write(f"**Processing time:** {result['processing_time_seconds']:.2f} seconds\n")
            f.write(f"**Sources used:** {result['sources_count']}\n\n")
            f.write("---\n\n")
            f.write(result["final_output"])
        
        logger.info(f"Output saved to {output_file}")
        result["output_file"] = str(output_file)
    
    return result


def main():
    """Main entry point for the research assistant system."""
    try:
        # Validate environment
        validate_environment()
        
        # Load configuration
        config_dir = Path(__file__).parent / "config"
        config = load_config(config_dir / "agent_configs.yaml")
        prompts = load_prompts(config_dir / "prompts.yaml")
        
        # Initialize agents
        research_agent, analysis_agent, writing_agent = initialize_agents(
            config, prompts
        )
        
        # Initialize workflow
        workflow = ResearchWorkflow(
            research_agent=research_agent,
            analysis_agent=analysis_agent,
            writing_agent=writing_agent,
            workflow_config=config["workflow"]
        )
        
        # Initialize metrics tracker
        metrics = EvaluationMetrics()
        
        # Process queries
        if len(sys.argv) > 1:
            # Query provided as command-line argument
            query = " ".join(sys.argv[1:])
            result = process_query(query, workflow, metrics, save_output=True)
            
            print("\n" + "="*80)
            print("RESEARCH ASSISTANT - FINAL OUTPUT")
            print("="*80)
            if result.get("error"):
                print(f"Error: {result['error']}")
                print(f"Query: {result.get('query', '')}")
            else:
                print(result.get("final_output", ""))
            print("\n" + "="*80)
            print(f"Processing time: {result.get('processing_time_seconds', 0):.2f} seconds")
            print(f"Sources used: {result.get('sources_count', 0)}")
            if result.get("output_file"):
                print(f"Output saved to: {result['output_file']}")
            print("="*80 + "\n")
            
        else:
            # Interactive mode
            print("\n" + "="*80)
            print("Research Assistant Multi-Agent System")
            print("="*80)
            print("Enter your research query (or 'quit' to exit, 'report' for metrics):\n")
            
            while True:
                query = input("Query: ").strip()
                
                if query.lower() == 'quit':
                    break
                
                if query.lower() == 'report':
                    report = metrics.generate_report()
                    print("\n" + json.dumps(report["summary"], indent=2))
                    continue
                
                if not query:
                    continue
                
                result = process_query(query, workflow, metrics, save_output=True)
                
                print("\n" + "-"*80)
                print("RESULT:")
                print("-"*80)
                if result.get("error"):
                    print(f"Error: {result['error']}")
                else:
                    print(result.get("final_output", ""))
                print("-"*80)
                print(f"\nProcessing time: {result.get('processing_time_seconds', 0):.2f} seconds")
                print(f"Sources used: {result.get('sources_count', 0)}")
                if result.get("output_file"):
                    print(f"Output saved to: {result['output_file']}")
                print("\n")
        
        # Generate final evaluation report
        if metrics.metrics_history:
            report_path = Path("evaluation_reports") / f"report_{metrics.metrics_history[-1]['timestamp'].split('T')[0]}.json"
            report = metrics.generate_report(output_path=report_path)
            logger.info(f"Evaluation report generated: {report_path}")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
