# Launch Instructions

This project is not a frontend-only React app. It has two parts:

- `frontend/`: React + Vite + TypeScript
- repo root: Flask API backend in `app.py`

During development, the React app runs on port `5173` and proxies `/api/*` requests to the Flask backend on port `5000`.

## What caused the first "Internal Server Error"

The frontend was able to start, but the backend was not fully set up yet.

The current backend requirements are:

- a `.env` file in the repo root
- Python dependencies installed
- a running PostgreSQL database
- database tables created

If PostgreSQL is missing or `DATABASE_URL` points to a non-working database, routes like `/api/register` and `/api/login` will fail.

## Current known project layout

- `app.py`: Flask API
- `create_db_tables.py`: creates the PostgreSQL tables
- `frontend/package.json`: frontend scripts and dependencies
- `frontend/vite.config.ts`: dev proxy from `/api` to `http://localhost:5000`
- `.env.example`: environment template

## First-time setup

### 1. Frontend dependencies

From the repository root:

```bash
cd frontend
npm install
```

Start the frontend:

```bash
npm run dev
```

## 2. Backend virtual environment

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Backend Python dependencies

Minimal dependencies needed to start the current Flask API:

```bash
pip install Flask==2.3.3 Flask-Bcrypt==1.0.1 Werkzeug==2.3.7 psycopg2-binary python-dotenv
```

If you want the full dependency set from the repository:

```bash
pip install -r requirements.txt
```

Note: `requirements.txt` also includes heavier ML/audio packages. Those are not required just to boot the current auth/chat API.

## 4. Environment variables

Create the env file:

```bash
cp .env.example .env
```

Then edit `.env` and make sure `DATABASE_URL` points to a real PostgreSQL instance.

Example from the template:

```env
SECRET_KEY=change-me-to-a-long-random-string
DB_NAME=conversations_db
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/conversations_db
CLAUD_API_TOKEN=
```

## 5. Start PostgreSQL

This repo includes `docker-compose.yml` for Postgres:

```bash
docker compose up -d
```

If your machine uses the older command:

```bash
docker-compose up -d
```

If Docker is not installed, you need some other running PostgreSQL instance and then must update `.env` accordingly.

## 6. Create database tables

Once PostgreSQL is running and `.env` is correct:

```bash
source .venv/bin/activate
python create_db_tables.py
```

Expected result:

```text
Database tables created (or already exist).
```

## 7. Start the backend

From the repository root:

```bash
source .venv/bin/activate
FLASK_APP=app.py flask run
```

That should start the Flask API on:

```text
http://localhost:5000
```

## 8. Start the frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

That should start the React app on:

```text
http://localhost:5173
```

## Development model

Run both processes at the same time:

- Terminal 1: Flask backend on `:5000`
- Terminal 2: Vite frontend on `:5173`

The browser talks to Vite, and Vite forwards `/api/*` requests to Flask.

## Production-style local run

Build the frontend:

```bash
cd frontend
npm run build
```

Then run Flask from the repository root:

```bash
source .venv/bin/activate
FLASK_APP=app.py flask run
```

In this mode, Flask serves both the API and the built React app.

## Troubleshooting

### Frontend builds but API calls fail

Check:

- Flask is running on port `5000`
- PostgreSQL is running
- `.env` exists
- `DATABASE_URL` is valid
- database tables were created with `python create_db_tables.py`

### `Internal Server Error` on login or register

Most likely cause:

- Flask reached a database-backed route but could not connect to PostgreSQL

Verify by checking:

- your database is actually running
- the username/password/host/port in `.env`
- the `DATABASE_URL` string

### `ModuleNotFoundError: No module named 'flask'`

Activate the backend venv first:

```bash
source .venv/bin/activate
```

Then install dependencies:

```bash
pip install Flask==2.3.3 Flask-Bcrypt==1.0.1 Werkzeug==2.3.7 psycopg2-binary python-dotenv
```

### `docker: command not found`

Docker is not installed on your machine. Either:

- install Docker and use `docker compose up -d`
- or connect the app to another PostgreSQL instance and update `.env`

### Frontend says proxy/API failed

Check `frontend/vite.config.ts`. It proxies `/api` to:

```text
http://localhost:5000
```

If Flask is not running there, API requests from the frontend will fail.

## Minimal command checklist

Backend terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install Flask==2.3.3 Flask-Bcrypt==1.0.1 Werkzeug==2.3.7 psycopg2-binary python-dotenv
cp .env.example .env
# edit .env
docker compose up -d
python create_db_tables.py
FLASK_APP=app.py flask run
```

Frontend terminal:

```bash
cd frontend
npm install
npm run dev
```
