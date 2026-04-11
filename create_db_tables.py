"""
create_db_tables.py — one-shot script to initialize the app schema.

Usage:
    python create_db_tables.py

If no PostgreSQL configuration is present, the script creates a local SQLite
database file at ./unify_dev.db.
"""

import os
import sqlite3

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ENV_PATH)

DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'unify_dev.db')

SQLITE_DDL = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER REFERENCES users(user_id),
    user2_id INTEGER REFERENCES users(user_id),
    started_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER REFERENCES conversations(conversation_id),
    sender_id INTEGER REFERENCES users(user_id),
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

POSTGRES_DDL = """
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


def get_database_config():
    sqlite_path = os.environ.get('SQLITE_PATH', DEFAULT_SQLITE_PATH)
    url = os.environ.get('DATABASE_URL')
    if url:
        if url.startswith('sqlite:///'):
            return {'driver': 'sqlite', 'path': url.removeprefix('sqlite:///')}
        return {'driver': 'postgres', 'url': url}

    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')

    if not all([db_name, db_user, db_pass]):
        return {'driver': 'sqlite', 'path': sqlite_path}

    return {
        'driver': 'postgres',
        'url': f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}',
    }


def main():
    config = get_database_config()
    if config['driver'] == 'sqlite':
        conn = sqlite3.connect(config['path'])
        conn.executescript(SQLITE_DDL)
        conn.commit()
        conn.close()
        print(f"SQLite database ready at {config['path']}.")
        return

    import psycopg2

    conn = psycopg2.connect(config['url'])
    cur = conn.cursor()
    cur.execute(POSTGRES_DDL)
    conn.commit()
    cur.close()
    conn.close()
    print('PostgreSQL tables created (or already exist).')


if __name__ == '__main__':
    main()
