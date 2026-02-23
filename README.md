# Unify_V2

Unify — Designated Support App.

Flask REST API backend + React (Vite + TypeScript) frontend.

---

## Development setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL)

### First-time setup

```bash
# 1. Copy environment variables
cp .env.example .env
# Edit .env with your actual values

# 2. Start PostgreSQL
docker-compose up -d

# 3. Create database tables
pip install -r requirements.txt
python create_db_tables.py

# 4. Install frontend dependencies
cd frontend && npm install && cd ..
```

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
