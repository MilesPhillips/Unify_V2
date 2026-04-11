# Unify_V2

Unify — Designated Support App.

Flask REST API backend + React (Vite + TypeScript) frontend.

---

## Quick start

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd Unify_V2

# 2. Copy .env and set your database password
cp .env.example .env
# Edit .env — set DB_PASS (and optionally DB_NAME, DB_USER)

# 3. Run the launch script
./launch.sh
```

The script handles everything:
- Creates a Python virtual environment
- Installs Python dependencies (including the PostgreSQL driver)
- Starts PostgreSQL via Docker Compose and waits for it to be healthy
- Initialises database tables
- Starts Flask on `:5000` and Vite on `:5173`

Open `http://localhost:5173` in your browser. Press **Ctrl+C** to stop both servers.

Alternatively, use `./tmux.sh` to launch inside a tmux session — the app runs in the bottom pane and the top pane is free for other work:

```bash
./tmux.sh
```

If a `unify` tmux session is already running, this attaches to it instead of starting a new one.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (required — PostgreSQL runs in a container)

---

## Environment variables

Copy `.env.example` to `.env` before first run. **`DB_PASS` is required** — the app will not start without it.

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | Flask session signing key |
| `DB_NAME` | `unify` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASS` | — | **Required.** PostgreSQL password (also used by docker-compose) |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DATABASE_URL` | — | Full Postgres URL (overrides DB_* vars if set) |
| `ANTHROPIC_API_KEY` | — | Required for live AI chat responses |
| `ANTHROPIC_MODEL` | `claude-3-5-haiku-20241022` | Model to use |
| `ANTHROPIC_MAX_TOKENS` | `512` | Max tokens per assistant response |
| `LLM_SYSTEM_PROMPT` | — | Custom system prompt for the AI assistant |

---

## ML / audio features

The heavy ML packages (torch, whisper, etc.) are in `requirements-ml.txt` and are **not** installed by the launch script. Install them separately only if you need speech/transcription features:

```bash
source .venv/bin/activate
pip install -r requirements-ml.txt
```

---

## Production build

```bash
cd frontend && npm run build
# Outputs to frontend/dist/

source .venv/bin/activate
FLASK_APP=app.py flask run
# Flask now serves both the API and the built React app at :5000
```

---

## Project structure

```
Unify_V2/
├── launch.sh               # Single launch script — start here
├── tmux.sh                 # Tmux split-pane launcher (optional, requires tmux)
├── app.py                  # Flask API (all routes under /api/*)
├── create_db_tables.py     # DB schema init (called by launch.sh)
├── requirements-core.txt   # Python deps (Flask, psycopg2, Anthropic, etc.)
├── requirements-ml.txt     # ML/audio deps (install separately if needed)
├── requirements.txt        # References requirements-core.txt
├── docker-compose.yml      # PostgreSQL container
├── .env.example            # Environment variable template
├── lib/                    # Python modules (LLM service, etc.)
└── frontend/               # React app (Vite + TypeScript)
    ├── package.json
    ├── vite.config.ts      # Dev proxy: /api/* → localhost:5000
    └── src/
        ├── App.tsx
        ├── lib/api.ts
        ├── contexts/AuthContext.tsx
        ├── hooks/useSpeechRecognition.ts
        ├── components/
        └── pages/
```
