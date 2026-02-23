# Quick Start Guide

Get the Research Assistant (backend + Web UI) up and running in a few minutes.

## Step 1: Install Python Dependencies

```bash
# From project root
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

## Step 2: Set Up API Keys

1. Copy the example environment file:
   ```bash
   # Windows
   copy .env.example .env

   # Linux/Mac
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=sk-your-openai-key-here
   TAVILY_API_KEY=tvly-your-tavily-key-here
   ```

   **Get your API keys:**
   - OpenAI: https://platform.openai.com/api-keys
   - Tavily: https://tavily.com/

## Step 3: Verify Setup

```bash
python setup_check.py
```

You should see all checks passing ✅

## Step 4: Run the App

### Option A: Web UI (recommended)

1. **Start the FastAPI backend** (from project root, with venv active):
   ```bash
   uvicorn server.api:app --reload --port 8000
   ```

2. **In a second terminal**, start the React frontend:
   ```bash
   cd front_end
   npm install
   npm run dev
   ```

3. Open **http://localhost:5173** in your browser. Use the search bar to ask a research question; the answer and sources appear below (research can take 1–2 minutes).

The frontend proxies `/api` to `http://localhost:8000`, so both must be running.

### Option B: Command-line only

**Single query:**
```bash
python main.py "What are the latest developments in quantum computing?"
```

**Interactive mode:**
```bash
python main.py
```

Then type queries. Use `report` for metrics and `quit` to exit.

## Example Output (Web UI)

- **Answer**: Markdown report (summary, findings, citations).
- **Sources**: Numbered list of clickable links (title + URL).

Output is also saved to `outputs/research_output_[timestamp].md` when using the API or CLI.

## Expose Web UI on Your Network

To access the app from another device on your LAN:

- Start the backend as above.
- Run the frontend with: `npm run dev -- --host` (or add `host: true` under `server` in `front_end/vite.config.js`).
- Use the URL Vite prints (e.g. `http://192.168.x.x:5173`) on other devices.

## Troubleshooting

### "ModuleNotFoundError: No module named 'autogen'"
```bash
pip install -U "autogen-agentchat" "autogen-ext[openai]"
```

### "Missing required environment variables"
- Ensure `.env` exists and contains valid `OPENAI_API_KEY` and `TAVILY_API_KEY`.

### "Tavily API request failed"
- Check your Tavily API key and internet connection.
- Confirm you have API credits/quota.

### "OpenAI API error"
- Verify your OpenAI API key and account balance.
- Check the model name in `config/agent_configs.yaml`.

### Web UI: "Search failed" or long request timeout
- Ensure the **FastAPI backend** is running on port 8000.
- Research queries can take 1–2 minutes; the Vite proxy is configured for long timeouts.

### npm install peer dependency errors (front_end)
- The project uses `.npmrc` with `legacy-peer-deps=true`. Run `npm install` again from `front_end/`.

## Next Steps

- Customize prompts in `config/prompts.yaml`
- Adjust agent settings in `config/agent_configs.yaml`
- Review evaluation reports in `evaluation_reports/`
- Check logs in `logs/`

## Need Help?

- Full documentation: [README.md](README.md)
- High-level overview: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- Logs: `logs/research_assistant_*.log`
