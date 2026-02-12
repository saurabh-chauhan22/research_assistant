# Quick Start Guide

Get the Research Assistant Multi-Agent System up and running in 5 minutes!

## Step 1: Install Python Dependencies

```bash
# Activate virtual environment (if not already activated)
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Install packages
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

Run the setup verification script:
```bash
python setup_check.py
```

You should see all checks passing ✅

## Step 4: Run Your First Query

### Command-Line Mode:
```bash
python main.py "What are the latest developments in quantum computing?"
```

### Interactive Mode:
```bash
python main.py
```

Then type your queries interactively.

## Example Output

The system will:
1. **Research Agent** searches for relevant sources
2. **Analysis Agent** synthesizes findings
3. **Writing Agent** creates formatted report

Output is saved to `outputs/research_output_[timestamp].md`

## Troubleshooting

### "ModuleNotFoundError: No module named 'autogen'"
```bash
pip install -U "autogen-agentchat" "autogen-ext[openai]"
```

### "Missing required environment variables"
- Check that `.env` file exists
- Verify API keys are set correctly (not using placeholder values)

### "Tavily API request failed"
- Verify your Tavily API key is correct
- Check your internet connection
- Ensure you have API credits/quota

### "OpenAI API error"
- Verify your OpenAI API key
- Check your OpenAI account has credits
- Verify the model name in `config/agent_configs.yaml` is correct

## Next Steps

- Customize agent prompts in `config/prompts.yaml`
- Adjust agent settings in `config/agent_configs.yaml`
- Review evaluation reports in `evaluation_reports/`
- Check logs in `logs/` directory

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review logs in `logs/` directory for error details
- Verify configuration files are properly formatted (YAML syntax)
