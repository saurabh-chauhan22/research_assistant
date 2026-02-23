# Research Assistant Multi-Agent System

A production-grade research assistant with a **multi-agent Python backend** (Microsoft AutoGen) and a **React Web UI**. Three specialized agents collaborate to deliver comprehensive, well-structured research reports. You can use the **Web UI** (FastAPI + React) or the **CLI** (optional).

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              User (Web UI or CLI)                                │
└───────────────────────────┬─────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │  Web: Browser → Vite (5173) → proxy   │
         │       /api → FastAPI (8000)            │
         │  CLI: python main.py "query"          │
         └───────────────────┬───────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Research Agent                                │
│  • Runs web search via Tavily API                               │
│  • Formats sources with title + URL                              │
│  • Returns structured research findings                         │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Analysis Agent                                │
│  • Identifies patterns and contradictions                        │
│  • Synthesizes findings across sources                           │
│  • Generates confidence assessments                              │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Writing Agent                                  │
│  • Transforms analysis into structured prose                     │
│  • Markdown formatting, citations [1]…[n]                        │
│  • Executive summary + Sources section                           │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Output (API / CLI / File)                        │
│  • final_output (markdown)                                       │
│  • sources[] { title, url }                                      │
│  • outputs/research_output_*.md                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### Multi-Agent Backend
- **Research Agent**: Tavily Search API, structured sources (title + URL)
- **Analysis Agent**: Synthesis and pattern recognition
- **Writing Agent**: Markdown report with citations and a Sources list

### Web UI (React + Vite)
- Search bar to submit research questions
- Loading state while the backend runs (long requests supported)
- Markdown-rendered answer (headings, lists, links)
- **Sources** section: numbered, clickable links (title + URL)
- Bootstrap/Bootswatch Lux theme
- Dev server proxies `/api` to FastAPI with long timeouts for research

### FastAPI Backend
- **GET /api/search?query=...** — runs the full workflow
- Returns: `final_output`, `sources` (array of `{ title, url }`), `sources_count`, `processing_time_seconds`, `error` (if any)
- CORS enabled for the frontend
- Optional OpenAPI docs at `/docs`

### CLI (Optional)
- Single query: `python main.py "Your query"`
- Interactive: `python main.py` (then `report`, `quit`)

### Production-Ready
- Error handling and graceful degradation
- Retry with exponential backoff (Tavily)
- Logging (console + file)
- Environment-based API keys
- Evaluation metrics and quality assessment

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for the Web UI)
- **OpenAI API key** — [Get one](https://platform.openai.com/api-keys)
- **Tavily Search API key** — [Get one](https://tavily.com/)

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd research_assistant
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate # Linux/Mac
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   If you see AutoGen import errors:
   ```bash
   pip install -U "autogen-agentchat" "autogen-ext[openai]"
   ```

4. **Environment variables:**
   ```bash
   copy .env.example .env   # Windows
   cp .env.example .env     # Linux/Mac
   ```
   Edit `.env` and set:
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY`

5. **Verify setup (optional):**
   ```bash
   python setup_check.py
   ```

6. **Frontend (for Web UI):**
   ```bash
   cd front_end
   npm install
   cd ..
   ```

## Usage

### Web UI

1. **Start the API server** (from project root, venv active):
   ```bash
   uvicorn server.api:app --reload --port 8000
   ```

2. **Start the frontend** (second terminal):
   ```bash
   cd front_end
   npm run dev
   ```

3. Open **http://localhost:5173**. Enter a research question in the search bar; the answer and sources appear below. Research may take 1–2 minutes.

### API (e.g. for integration)

- **Endpoint:** `GET /api/search?query=Your+research+question`
- **Response (success):** JSON with `final_output`, `sources` (list of `{ "title", "url" }`), `sources_count`, `processing_time_seconds`, `timestamp`, etc.
- **Response (error):** `{ "error": "...", "query": "..." }`

Example with curl (backend on port 8000):
```bash
curl "http://localhost:8000/api/search?query=What%20is%20quantum%20computing"
```

### Command-Line

**Single query:**
```bash
python main.py "What are the latest developments in quantum computing?"
```

**Interactive:**
```bash
python main.py
# Then: Query: ... | report | quit
```

### Programmatic

```python
from main import load_config, load_prompts, initialize_agents, process_query
from pathlib import Path

config_dir = Path("config")
config = load_config(config_dir / "agent_configs.yaml")
prompts = load_prompts(config_dir / "prompts.yaml")
research_agent, analysis_agent, writing_agent = initialize_agents(config, prompts)

from orchestration.workflow import ResearchWorkflow
workflow = ResearchWorkflow(
    research_agent=research_agent,
    analysis_agent=analysis_agent,
    writing_agent=writing_agent,
    workflow_config=config["workflow"]
)

result = workflow.execute("Your research query here")
print(result["final_output"])
# result["sources"] → list of { "title", "url" }
```

## Project Structure

```
research_assistant/
├── agents/                    # Agent implementations
│   ├── research_agent.py     # Research Agent (Tavily)
│   ├── analysis_agent.py     # Analysis Agent
│   └── writing_agent.py      # Writing Agent
├── orchestration/
│   └── workflow.py           # Research → Analysis → Writing
├── evaluation/                # Metrics
│   └── metrics.py            # Quality scoring, reports
├── server/                    # FastAPI backend
│   ├── api.py                # App, CORS, routes
│   └── search_api.py         # GET /api/search
├── front_end/                 # React Web UI
│   ├── src/
│   │   ├── application/      # Chat (search, answer, sources)
│   │   └── services/         # API client
│   └── vite.config.js        # Proxy /api → backend
├── config/
│   ├── agent_configs.yaml    # Agent settings
│   └── prompts.yaml          # System prompts
├── utils/
│   ├── logging_config.py     # Logging
│   └── api_client.py         # Tavily client
├── tests/
│   └── test_queries.json
├── outputs/                   # Generated reports (auto-created)
├── logs/                      # Log files (auto-created)
├── evaluation_reports/        # JSON reports (auto-created)
├── main.py                    # CLI entry point
├── requirements.txt
├── .env.example
├── README.md                  # This file
├── QUICKSTART.md              # Short setup guide
└── PROJECT_SUMMARY.md         # Overview and structure
```

## Configuration

- **Agent behavior:** `config/agent_configs.yaml` (model, temperature, max sources, etc.)
- **Prompts:** `config/prompts.yaml`
- **Secrets:** `.env` (API keys)

## Output Format

Reports are markdown with:

- Executive summary
- Detailed findings with inline citations [1], [2], …
- **Sources**: numbered list with title and URL

The API and Web UI also return a structured `sources` array for links.

## Evaluation Metrics

- Processing time, source count, output length
- Quality scores (relevance, completeness, coherence)
- Reports in `evaluation_reports/report_[date].json`
- In interactive CLI: type `report` for a summary

## Error Handling

- API failures → retry with exponential backoff
- Missing keys → clear errors at startup
- Invalid or long-running queries → handled; errors returned in API response and logged

## Logging

- Console: INFO and above
- File: `logs/research_assistant_YYYYMMDD.log` (DEBUG)

## Expose Web UI on Your Network

Run the frontend with:

```bash
cd front_end && npm run dev -- --host
```

Use the network URL Vite prints (e.g. `http://192.168.x.x:5173`) from other devices. Keep the backend running on the same machine.

## Troubleshooting

| Issue | Action |
|-------|--------|
| Missing env vars | Ensure `.env` has `OPENAI_API_KEY` and `TAVILY_API_KEY` |
| Tavily API failed | Check key, network, and quota |
| OpenAI error | Check key, balance, and model in config |
| Web UI "Search failed" | Start backend: `uvicorn server.api:app --reload --port 8000` |
| Long request timeout | Vite proxy is set for long runs; ensure backend is up |
| npm peer deps | Project uses `legacy-peer-deps` in `front_end/.npmrc`; run `npm install` again |

## Documentation

- **README.md** (this file) — full documentation
- **QUICKSTART.md** — minimal steps to run Web UI and CLI
- **PROJECT_SUMMARY.md** — structure and feature overview

---

**Built with Microsoft AutoGen, FastAPI, and React**
