"""
app.py — Unify Flask API

Pure JSON API backend. No render_template() calls.
React (frontend/) is the only UI layer.

Development:
    flask run                        # API on :5000
    cd frontend && npm run dev       # React on :5173 (proxies /api/* to :5000)

Production:
    cd frontend && npm run build     # outputs to frontend/dist/
    flask run                        # serves API + React build
"""

import os
from functools import wraps

import psycopg2
from flask import Flask, jsonify, request, session, send_from_directory, g
from flask_bcrypt import Bcrypt
from lib.llm_service import LLMConfigurationError, LLMService

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ENV_PATH)

# ─── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')

bcrypt = Bcrypt(app)

# ─── Database ─────────────────────────────────────────────────────────────────

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


def _pg_url() -> str:
    url = os.environ.get('DATABASE_URL')
    if url:
        return url
    db_name = os.environ.get('DB_NAME', '')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_pass = os.environ.get('DB_PASS', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    if not db_pass:
        raise RuntimeError('DB_PASS is not set. Cannot connect to PostgreSQL.')
    return f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'


def get_db():
    if 'db' not in g:
        conn = psycopg2.connect(_pg_url())
        cur = conn.cursor()
        cur.execute(DDL)
        conn.commit()
        cur.close()
        g.db = conn
    return g.db


def fetchone_value(cur):
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_conversation(user_id: int) -> int:
    db = get_db()
    cur = db.cursor()
    cur.execute(
        '''
        SELECT conversation_id
        FROM conversations
        WHERE user1_id = %s AND user2_id = %s
        ORDER BY conversation_id ASC
        LIMIT 1
        ''',
        (user_id, user_id),
    )
    row = cur.fetchone()
    conversation_id = row[0] if row else None

    if conversation_id is None:
        cur.execute(
            '''
            INSERT INTO conversations (user1_id, user2_id)
            VALUES (%s, %s)
            RETURNING conversation_id
            ''',
            (user_id, user_id),
        )
        conversation_id = cur.fetchone()[0]
        db.commit()

    cur.close()

    if conversation_id is None:
        raise RuntimeError('Failed to create a conversation for the current user.')

    return conversation_id


def load_recent_messages(conversation_id: int, limit: int = 12) -> list[dict[str, str]]:
    db = get_db()
    cur = db.cursor()
    cur.execute(
        '''
        SELECT sender_id, content
        FROM messages
        WHERE conversation_id = %s
        ORDER BY message_id DESC
        LIMIT %s
        ''',
        (conversation_id, limit),
    )
    rows = cur.fetchall()
    cur.close()

    history: list[dict[str, str]] = []
    for row in reversed(rows):
        sender_id = row[0]
        content = row[1]
        role = 'assistant' if sender_id is None else 'user'
        history.append({'role': role, 'content': content})
    return history


def save_message(conversation_id: int, sender_id: int | None, content: str) -> None:
    db = get_db()
    cur = db.cursor()
    cur.execute(
        '''
        INSERT INTO messages (conversation_id, sender_id, content)
        VALUES (%s, %s, %s)
        ''',
        (conversation_id, sender_id, content),
    )
    db.commit()
    cur.close()


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ─── Auth helpers ─────────────────────────────────────────────────────────────

def login_required(f):
    """Decorator that returns 401 JSON if the user is not logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# ─── Auth routes ─────────────────────────────────────────────────────────────

@app.post('/api/register')
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    db = get_db()
    cur = db.cursor()

    cur.execute('SELECT user_id FROM users WHERE username = %s', (username,))
    if cur.fetchone():
        cur.close()
        return jsonify({'error': 'Username already taken'}), 409

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    cur.execute(
        'INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id',
        (username, hashed),
    )
    user_id = cur.fetchone()[0]
    db.commit()
    cur.close()

    return jsonify({'user_id': user_id, 'username': username}), 201


@app.post('/api/login')
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute(
        'SELECT user_id, password FROM users WHERE username = %s',
        (username,),
    )
    row = cur.fetchone()
    cur.close()

    if not row or not bcrypt.check_password_hash(row[1], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user_id'] = row[0]
    session['username'] = username
    return jsonify({'user_id': row[0], 'username': username})


@app.post('/api/logout')
def logout():
    session.clear()
    return jsonify({'ok': True})


@app.get('/api/me')
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'user_id': session['user_id'], 'username': session['username']})

# ─── Chat routes ──────────────────────────────────────────────────────────────

@app.post('/api/chat')
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    user_id = session['user_id']
    conversation_id = get_or_create_conversation(user_id)
    history = load_recent_messages(conversation_id)

    try:
        response = LLMService().chat(history=history, message=message)
    except LLMConfigurationError as exc:
        return jsonify({'error': str(exc)}), 503
    except Exception:
        app.logger.exception('LLM request failed')
        return jsonify({'error': 'The assistant is temporarily unavailable.'}), 502

    save_message(conversation_id, user_id, message)
    save_message(conversation_id, None, response)

    return jsonify({'response': response})


@app.post('/api/transcribe')
@login_required
def transcribe():
    data = request.get_json(silent=True) or {}
    transcript = (data.get('transcript') or '').strip()

    if not transcript:
        return jsonify({'error': 'Transcript is required'}), 400

    # TODO: store transcript, trigger further processing if needed
    return jsonify({'ok': True, 'transcript': transcript})

# ─── Upload / inbox routes ────────────────────────────────────────────────────

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post('/api/upload')
@login_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    f = request.files['file']
    if not f.filename:
        return jsonify({'error': 'Empty filename'}), 400

    from werkzeug.utils import secure_filename
    filename = secure_filename(f.filename)
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({'filename': filename}), 201


@app.get('/api/inbox/<username>')
@login_required
def inbox(username: str):
    # TODO: fetch inbox videos for this user from the DB
    return jsonify({'username': username, 'videos': []})

# ─── Serve React SPA (production) ────────────────────────────────────────────

DIST_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path: str):
    """
    In production (after `npm run build`), Flask serves the React SPA.
    Any path that maps to a real file in dist/ is served directly;
    everything else falls back to index.html so React Router can handle it.
    """
    if path and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')

# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
