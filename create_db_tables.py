"""
create_db_tables.py — one-shot script to initialize the app schema.

Usage:
    python create_db_tables.py

Requires DB_PASS (and optionally DB_NAME, DB_USER, DB_HOST, DB_PORT) to be
set in .env or the environment. PostgreSQL must be running.
"""

import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

import psycopg2

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ENV_PATH)

DDL = """
CREATE TABLE IF NOT EXISTS users (
    user_id  SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id SERIAL PRIMARY KEY,
    user1_id        INTEGER REFERENCES users(user_id),
    user2_id        INTEGER REFERENCES users(user_id),
    started_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    message_id      SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(conversation_id),
    sender_id       INTEGER REFERENCES users(user_id),
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
"""


def pg_url() -> str:
    url = os.environ.get('DATABASE_URL')
    if url:
        return url
    db_name = os.environ.get('DB_NAME', '')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_pass = os.environ.get('DB_PASS', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    if not db_pass:
        raise SystemExit('ERROR: DB_PASS is not set. Cannot connect to PostgreSQL.')
    return f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'


def main():
    conn = psycopg2.connect(pg_url())
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()
    cur.close()
    conn.close()
    print('PostgreSQL tables created (or already exist).')


if __name__ == '__main__':
    main()
