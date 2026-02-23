"""
create_db_tables.py — one-shot script to initialize the PostgreSQL schema.

Usage:
    DATABASE_URL=postgresql://postgres:password@localhost:5432/conversations_db \
        python create_db_tables.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

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

def main():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL environment variable is not set')

    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()
    cur.close()
    conn.close()
    print('Database tables created (or already exist).')

if __name__ == '__main__':
    main()
