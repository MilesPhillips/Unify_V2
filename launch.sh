#!/usr/bin/env bash
# launch.sh — Start the Unify V2 development stack.
#
# Usage: ./launch.sh
#
# What this script does:
#   1. Creates and activates a Python venv (if not already done)
#   2. Installs core Python dependencies
#   3. Copies .env.example → .env if .env does not exist
#   4. Asks whether to use SQLite or PostgreSQL
#   5. (PostgreSQL) starts Docker Compose and waits for Postgres to be healthy
#   6. Initialises database tables
#   7. Starts Flask on :5000 in the background
#   8. Starts Vite on :5173 in the foreground
#   9. On exit (Ctrl+C), kills Flask

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# ─── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # no colour

info()    { echo -e "${GREEN}[launch]${NC} $*"; }
warn()    { echo -e "${YELLOW}[launch]${NC} $*"; }
error()   { echo -e "${RED}[launch]${NC} $*" >&2; }

# ─── Prerequisites ────────────────────────────────────────────────────────────
require_cmd() {
    command -v "$1" &>/dev/null || { error "Required command not found: $1. $2"; exit 1; }
}
require_cmd python3 "Install Python 3.11+ from https://python.org"
require_cmd node    "Install Node.js 18+ from https://nodejs.org"
require_cmd npm     "Install Node.js 18+ from https://nodejs.org"

# ─── Python venv ──────────────────────────────────────────────────────────────
VENV_DIR="$REPO_ROOT/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating Python virtual environment at .venv ..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv for the rest of this script
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

info "Installing core Python dependencies ..."
pip install -q -r "$REPO_ROOT/requirements-core.txt"

# ─── .env setup ───────────────────────────────────────────────────────────────
if [[ ! -f "$REPO_ROOT/.env" ]]; then
    warn ".env not found — copying from .env.example"
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    warn "Edit .env with your settings, then re-run this script."
    warn "At minimum set SECRET_KEY to a random string."
fi

# Load .env into the current shell so docker-compose picks up credentials
set -a
# shellcheck source=/dev/null
source "$REPO_ROOT/.env"
set +a

# ─── Database selection ───────────────────────────────────────────────────────
echo ""
echo "Which database backend do you want to use?"
echo "  1) SQLite  (zero config, data stored in unify_dev.db)"
echo "  2) PostgreSQL  (via Docker — requires Docker installed and DB_PASS in .env)"
echo ""
read -rp "Enter 1 or 2 [default: 1]: " DB_CHOICE
DB_CHOICE="${DB_CHOICE:-1}"

if [[ "$DB_CHOICE" == "2" ]]; then
    require_cmd docker "Install Docker from https://docs.docker.com/get-docker/"

    if [[ -z "${DB_PASS:-}" ]]; then
        error "DB_PASS is not set in .env. Please set it before using PostgreSQL."
        exit 1
    fi

    info "Installing PostgreSQL driver ..."
    pip install -q -r "$REPO_ROOT/requirements-postgres.txt"

    info "Starting PostgreSQL via Docker Compose ..."
    docker compose up -d postgres

    info "Waiting for PostgreSQL to be healthy ..."
    RETRIES=30
    until docker compose exec -T postgres pg_isready -U "${DB_USER:-postgres}" -d "${DB_NAME:-conversations_db}" &>/dev/null; do
        RETRIES=$((RETRIES - 1))
        if [[ $RETRIES -le 0 ]]; then
            error "PostgreSQL did not become healthy in time. Check: docker compose logs postgres"
            exit 1
        fi
        sleep 2
    done
    info "PostgreSQL is ready."
else
    info "Using SQLite (unify_dev.db)."
    # Unset DATABASE_URL so the app falls back to SQLite
    unset DATABASE_URL DB_NAME DB_USER DB_PASS DB_HOST DB_PORT
fi

# ─── Database tables ──────────────────────────────────────────────────────────
info "Initialising database tables ..."
python "$REPO_ROOT/create_db_tables.py"

# ─── Frontend dependencies ────────────────────────────────────────────────────
FRONTEND_DIR="$REPO_ROOT/frontend"
if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    info "Installing frontend npm dependencies ..."
    npm --prefix "$FRONTEND_DIR" install
fi

# ─── Start Flask ──────────────────────────────────────────────────────────────
info "Starting Flask backend on http://localhost:5000 ..."
FLASK_APP=app.py flask run &
FLASK_PID=$!

# ─── Cleanup on exit ──────────────────────────────────────────────────────────
cleanup() {
    echo ""
    info "Shutting down ..."
    kill "$FLASK_PID" 2>/dev/null || true
    wait "$FLASK_PID" 2>/dev/null || true
    info "Flask stopped."
}
trap cleanup EXIT INT TERM

# Give Flask a moment to start before Vite sends proxy requests
sleep 1

# ─── Start Vite (foreground) ──────────────────────────────────────────────────
info "Starting React frontend on http://localhost:5173 ..."
info "Press Ctrl+C to stop both servers."
echo ""
npm --prefix "$FRONTEND_DIR" run dev
