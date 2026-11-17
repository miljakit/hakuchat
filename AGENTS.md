# hakuchat - AGENTS.md

## Quick Start

```bash
# Install dependencies
.venv/bin/pip install openai flask python-dotenv

# Set required env var
export OPEN_ROUTER_API_KEY="your-openrouter-api-key"

# Run Flask server
.venv/bin/python app.py
```

## Project Structure

```
hakuchat/
├── app.py              # Flask server + tool use logic
├── tools.py            # web_search tool (curl + DuckDuckGo HTML)
├── weather.py          # Original single-script weather example
├── templates/
│   └── index.html      # Chat UI (vanilla JS)
├── static/
│   └── style.css       # Minimal styling
├── .venv/              # Python 3.14 venv
└── .env                # (gitignored) OPEN_ROUTER_UUS
```

## Architecture

- **LLM**: OpenRouter (`https://openrouter.ai/api/v1`) with model `nvidia/nemotron-3.5-super-vl:free`
- **Client**: OpenAI Python SDK (`openai.OpenAI`)
- **Tool**: `web_search(query)` → `curl -s -L -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=<query>"` → regex parse snippets
- **Chat flow**: Client sends full `messages[]` → Flask calls model with tool → if tool_calls: execute search, call model again → return final reply as JSON
- **History**: Client-side (sent with each request)
- **Errors**: Inline in chat as system/error messages

## Implementation Steps (testable increments)

1. **`tools.py`** – `web_search(query)` with curl + regex. Test: `python -c "from tools import web_search; print(web_search('Python Flask'))"`
2. **`app.py` skeleton** – Flask, `/api/chat` without tools. Test: `curl -X POST -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"hei"}]}' http://localhost:5000/api/chat`
3. **`app.py` tool integration** – Add `WEB_SEARCH_TOOL`, handle tool_calls loop. Test: ask "mikä on uusin Python-versio?" → triggers search
4. **`templates/index.html` + `static/style.css`** – Vanilla JS fetch, message bubbles, inline errors. Test: open `http://localhost:5000`

## Notes

- No pyproject.toml, requirements.txt, or setup.py yet
- No lint, typecheck, or test tooling configured
- Requires `OPEN_ROUTER_API_KEY` environment variable
- DuckDuckGo HTML scraping is rate-limited/unreliable; MVP only