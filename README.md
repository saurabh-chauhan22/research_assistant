# Research Assistant Multi-Agent System

A production-grade research assistant built with Microsoft AutoGen framework, featuring three specialized AI agents that collaborate to deliver comprehensive, well-structured research reports.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Query Input                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Research Agent                                │
│  • Analyzes query and generates search terms                     │
│  • Executes web searches via Tavily API                         │
│  • Extracts and structures information from sources              │
│  • Returns research findings with citations                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Analysis Agent                                │
│  • Receives raw research data                                    │
│  • Identifies patterns and contradictions                        │
│  • Synthesizes findings across sources                           │
│  • Generates confidence assessments                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Writing Agent                                  │
│  • Transforms analysis into structured prose                     │
│  • Applies markdown formatting                                   │
│  • Includes proper citations and source attributions             │
│  • Generates executive summary                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Final Formatted Output                          │
│  • Executive Summary                                             │
│  • Detailed Findings                                             │
│  • Numbered Source List                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### Multi-Agent Collaboration
- **Research Agent**: Specialized in information gathering with Tavily Search API integration
- **Analysis Agent**: Performs critical synthesis and pattern recognition
- **Writing Agent**: Produces professional, formatted output with citations

### Production-Ready Features
- ✅ Comprehensive error handling with graceful degradation
- ✅ Retry logic with exponential backoff for API calls
- ✅ Structured logging at all interaction points
- ✅ Environment variable management for API keys
- ✅ Conversation history tracking
- ✅ Evaluation metrics and quality assessment
- ✅ Input validation and sanitization

### Evaluation Framework
- Query processing time tracking
- Source count and diversity analysis
- Output quality scoring (relevance, completeness, coherence)
- Comparison with baseline single-agent system
- JSON evaluation reports

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Tavily Search API key ([Get one here](https://tavily.com/))

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd Research_Assistent
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** The system uses `autogen-agentchat` package. If installation fails, try:
   ```bash
   pip install -U "autogen-agentchat" "autogen-ext[openai]"
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac

   # Edit .env and add your API keys
   # OPENAI_API_KEY=your_key_here
   # TAVILY_API_KEY=your_key_here
   ```

5. **Verify setup (optional but recommended):**
   ```bash
   python setup_check.py
   ```

## Usage

### Command-Line Mode

Process a single query:
```bash
python main.py "What are the latest developments in quantum computing?"
```

### Interactive Mode

Run without arguments for interactive mode:
```bash
python main.py
```

Then enter queries interactively:
```
Query: What is the impact of AI on healthcare?
Query: report  # View evaluation metrics
Query: quit    # Exit
```

### Programmatic Usage

```python
from main import initialize_agents, load_config, load_prompts
from orchestration.workflow import ResearchWorkflow
from pathlib import Path

# Load configuration
config = load_config(Path("config/agent_configs.yaml"))
prompts = load_prompts(Path("config/prompts.yaml"))

# Initialize agents
research_agent, analysis_agent, writing_agent = initialize_agents(config, prompts)

# Create workflow
workflow = ResearchWorkflow(
    research_agent=research_agent,
    analysis_agent=analysis_agent,
    writing_agent=writing_agent,
    workflow_config=config["workflow"]
)

# Process query
result = workflow.execute("Your research query here")
print(result["final_output"])
```

## Project Structure

```
research_assistant/
├── agents/                    # Agent implementations
│   ├── __init__.py
│   ├── research_agent.py     # Research Agent
│   ├── analysis_agent.py     # Analysis Agent
│   └── writing_agent.py      # Writing Agent
├── orchestration/             # Workflow management
│   ├── __init__.py
│   └── workflow.py           # GroupChat orchestration
├── evaluation/                # Metrics and assessment
│   ├── __init__.py
│   └── metrics.py            # Evaluation framework
├── config/                    # Configuration files
│   ├── agent_configs.yaml    # Agent settings
│   └── prompts.yaml          # System prompts
├── utils/                     # Shared utilities
│   ├── __init__.py
│   ├── logging_config.py     # Logging setup
│   └── api_client.py         # Tavily API client
├── tests/                     # Test data
│   └── test_queries.json     # Sample queries
├── outputs/                   # Generated outputs (created automatically)
├── logs/                      # Log files (created automatically)
├── evaluation_reports/        # Evaluation reports (created automatically)
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## Configuration

### Agent Configuration (`config/agent_configs.yaml`)

Customize agent behavior:
- Model selection (GPT-4, GPT-3.5-turbo, etc.)
- Temperature settings
- Max tokens
- Max sources per query
- Workflow parameters

### Prompts (`config/prompts.yaml`)

Modify agent system prompts to change behavior:
- Research Agent: Focus on information gathering
- Analysis Agent: Emphasize critical thinking
- Writing Agent: Control output style and format

## Output Format

Each research query produces a structured markdown document:

```markdown
# Executive Summary
[Brief overview of key findings]

# Detailed Findings
[Comprehensive analysis with inline citations [1], [2], etc.]

# Sources
1. [Source Title] - URL
2. [Source Title] - URL
...
```

## Evaluation Metrics

The system tracks:
- **Processing Time**: Total time to process query
- **Source Count**: Number of sources used
- **Output Length**: Character count of final output
- **Quality Scores**:
  - Relevance Score (0-1)
  - Completeness Score (0-1)
  - Coherence Score (0-1)
  - Overall Quality Score (weighted average)

Evaluation reports are saved to `evaluation_reports/` directory as JSON files.

## Error Handling

The system includes comprehensive error handling:
- API failures trigger retry logic with exponential backoff
- Missing API keys show clear error messages
- Invalid queries are handled gracefully
- Partial failures don't crash the system
- All errors are logged with full context

## Logging

Logs are written to:
- Console: INFO level and above
- File: `logs/research_assistant_YYYYMMDD.log` (DEBUG level)

Configure logging level in `utils/logging_config.py` or via environment variable.

## Design Decisions

### Why Multi-Agent Architecture?

1. **Specialization**: Each agent focuses on a specific task, improving quality
2. **Modularity**: Easy to modify or replace individual agents
3. **Scalability**: Can add more agents (e.g., Fact-Checking Agent)
4. **Transparency**: Clear separation of research, analysis, and writing phases

### Why AutoGen?

- Built-in agent coordination with GroupChat
- Function calling support for API integration
- Conversation management and history tracking
- Production-ready framework with error handling

### Why Tavily Search API?

- Optimized for AI research workflows
- Returns structured, relevant results
- Includes AI-generated summaries
- Fast and reliable API

## Performance Benchmarks

Example performance metrics (varies by query complexity):

- **Simple Query** (1-2 sources): ~15-25 seconds
- **Medium Query** (3-5 sources): ~30-45 seconds
- **Complex Query** (5+ sources, deep analysis): ~45-60 seconds

Quality scores typically range:
- Relevance: 0.7-0.9
- Completeness: 0.6-0.8
- Coherence: 0.8-0.95
- Overall: 0.7-0.85

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure `.env` file exists with `OPENAI_API_KEY` and `TAVILY_API_KEY`

2. **"Tavily API request failed"**
   - Check API key validity
   - Verify internet connection
   - Check API rate limits

3. **"OpenAI API error"**
   - Verify API key and account balance
   - Check rate limits
   - Ensure model name is correct in config

4. **Import errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`
   - Check Python version (3.10+)

## Contributing

To extend the system:

1. **Add a new agent**: Create class in `agents/` following existing pattern
2. **Modify workflow**: Update `orchestration/workflow.py`
3. **Add metrics**: Extend `evaluation/metrics.py`
4. **Customize prompts**: Edit `config/prompts.yaml`

## License

This project is provided as-is for research and educational purposes.

## Acknowledgments

- Microsoft AutoGen framework
- Tavily Search API
- OpenAI GPT models

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages for specific guidance
3. Verify configuration files are properly formatted
4. Ensure all dependencies are installed

---

**Built with ❤️ using Microsoft AutoGen**
