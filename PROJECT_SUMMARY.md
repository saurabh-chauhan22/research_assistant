# Research Assistant Multi-Agent System - Project Summary

A production-grade Research Assistant with a **multi-agent backend** (Microsoft AutoGen) and a **React Web UI** that talks to a FastAPI server.

## 📁 Project Structure

```
research_assistant/
├── agents/                    # Three specialized agents
│   ├── research_agent.py     # Tavily API integration, source formatting
│   ├── analysis_agent.py     # Synthesis and pattern recognition
│   └── writing_agent.py      # Markdown output, citations, sources
├── orchestration/
│   └── workflow.py           # Sequential Research → Analysis → Writing
├── evaluation/                # Metrics and assessment
│   └── metrics.py            # Quality scoring and reporting
├── server/                    # FastAPI backend
│   ├── api.py                # App, CORS, router mount
│   └── search_api.py         # GET /api/search?query=...
├── front_end/                 # React Web UI
│   ├── src/
│   │   ├── application/      # Chat UI (search bar, answer, sources)
│   │   └── services/         # API client (search)
│   ├── vite.config.js        # Proxy /api → backend, long timeouts
│   └── package.json
├── config/
│   ├── agent_configs.yaml    # Agent settings
│   └── prompts.yaml          # System prompts
├── utils/
│   ├── logging_config.py     # Logging setup
│   └── api_client.py         # Tavily client with retry logic
├── tests/
│   └── test_queries.json     # Sample queries
├── main.py                    # CLI entry point (optional)
├── setup_check.py             # Setup verification
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
└── PROJECT_SUMMARY.md         # This file
```

## 🎯 Key Features

### ✅ Multi-Agent Backend
- **Research Agent**: Tavily Search API, structured sources with title + URL
- **Analysis Agent**: Pattern recognition, synthesis, confidence
- **Writing Agent**: Markdown report, citations [1]…[n], Sources section

### ✅ FastAPI Backend
- **GET /api/search?query=...** — runs the workflow, returns `final_output`, `sources` (title + URL), `sources_count`, timing, errors
- CORS enabled for the frontend
- Long-running requests supported (research can take minutes)

### ✅ React Web UI
- **Search bar** — enter a question, submit to backend
- **Loading state** — spinner and message while the backend runs
- **Answer** — markdown-rendered report (headings, lists, links)
- **Sources** — numbered list of clickable links (title + URL)
- Bootstrap/Bootswatch (Lux) theme; Vite dev server with proxy to API

### ✅ CLI (Optional)
- **Single query**: `python main.py "Your query"`
- **Interactive**: `python main.py` then type queries, `report` for metrics, `quit` to exit

### ✅ Production Features
- Error handling and graceful degradation
- Retry logic with exponential backoff (Tavily)
- Logging (console + file)
- Environment variables for API keys
- Conversation history in workflow
- Input validation

### ✅ Evaluation Framework
- Processing time, source count, output length
- Quality scores (relevance, completeness, coherence)
- JSON evaluation reports in `evaluation_reports/`
- Baseline comparison (optional)

## 🔧 Technical Stack

- **Backend**: Python 3.10+, FastAPI, Microsoft AutoGen
- **APIs**: OpenAI GPT-4, Tavily Search
- **Frontend**: React 18, Vite, Bootstrap/Bootswatch Lux, react-markdown, remark-gfm
- **Config**: YAML (agents, prompts), `.env` for keys

## 📊 Workflow

```
User Query (CLI or Web UI)
    ↓
Research Agent (Tavily Search → formatted sources)
    ↓
Analysis Agent (Synthesis & reasoning)
    ↓
Writing Agent (Markdown report + citations)
    ↓
Result: final_output + sources[] (title, url) → UI or CLI output
```

## 🚀 Getting Started

1. **Python env and deps**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Environment**
   - Copy `.env.example` to `.env`
   - Set `OPENAI_API_KEY` and `TAVILY_API_KEY`

3. **Verify**
   ```bash
   python setup_check.py
   ```

4. **Run**
   - **Web UI**: Start API (`uvicorn server.api:app --reload --port 8000`), then frontend (`cd front_end && npm install && npm run dev`). Open http://localhost:5173.
   - **CLI**: `python main.py "Your research query"`

## 📝 Configuration

- **Agent settings**: `config/agent_configs.yaml`
- **Prompts**: `config/prompts.yaml`
- **Environment**: `.env`

## 📈 Output

- **Reports**: `outputs/research_output_[timestamp].md`
- **Evaluation**: `evaluation_reports/report_[date].json`
- **Logs**: `logs/research_assistant_[date].log`

## 🔄 Optional Enhancements

- Caching for repeated queries
- Streaming responses
- Additional data sources
- Fact-checking agent
- Conversation memory / user feedback

---

**Status**: Production-ready (backend + Web UI + CLI)  
**Last Updated**: 2026-02-23
