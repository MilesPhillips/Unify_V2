# Unify_V2

Unify — Designated Support App.

Flask REST API backend + React (Vite + TypeScript) frontend.

---

## Development setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, only for PostgreSQL)

### First-time setup

```bash
# 1. Copy environment variables
cp .env.example .env
# For a local toy DB, leave the PostgreSQL variables unset.
# The app will use ./unify_dev.db automatically.

# 2. Install backend dependencies and create database tables
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python create_db_tables.py

# 3. Install frontend dependencies
cd frontend && npm install && cd ..
```

If you want PostgreSQL instead of the local SQLite file, set `DATABASE_URL` or
the `DB_*` variables in `.env`, then run:

```bash
docker-compose up -d
python create_db_tables.py
```

To enable real chat responses, set an Anthropic key in `.env`:

```bash
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-haiku-20241022
```

## Launching the App

### Local SQLite mode

```bash
cd /path/to/Unify_V2
source .venv/bin/activate
python create_db_tables.py
flask --app app run
```

In a second terminal:

```bash
cd /path/to/Unify_V2/frontend
npm run dev
```

Then open `http://localhost:5173`.

### Local SQLite mode with live LLM responses

1. Add `ANTHROPIC_API_KEY` to `.env`.
2. Install the SDK in the project virtualenv:

```bash
cd /path/to/Unify_V2
source .venv/bin/activate
pip install anthropic
flask --app app run
```

Keep the frontend dev server running with `npm run dev` in `frontend/`.

### Running in development

Two processes run side by side:

```bash
# Terminal 1 — Flask API on :5000
flask run

# Terminal 2 — React dev server on :5173 (proxies /api/* to Flask)
cd frontend && npm run dev
```

Open `http://localhost:5173` in your browser.

### Production build

```bash
cd frontend && npm run build
# Outputs to frontend/dist/

flask run
# Flask now serves both the API and the React app at :5000
```

---

## Project structure

```
Unify_V2/
├── app.py                  # Flask API (all routes under /api/*)
├── create_db_tables.py     # One-shot DB schema init
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # PostgreSQL
├── .env.example            # Environment variable template
├── lib/                    # Python modules (DB, LLM, audio, etc.)
└── frontend/               # React app (Vite + TypeScript)
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── index.css
        ├── lib/api.ts
        ├── contexts/AuthContext.tsx
        ├── hooks/useSpeechRecognition.ts
        ├── components/
        │   ├── Navbar.tsx
        │   └── ProtectedRoute.tsx
        └── pages/
            ├── Login.tsx
            ├── Register.tsx
            ├── Chat.tsx
            ├── Profile.tsx
            ├── AICoach.tsx
            ├── Contacts.tsx
            ├── History.tsx
            └── Video.tsx
```

See `Instructions_README.md` for the full phased migration plan.
