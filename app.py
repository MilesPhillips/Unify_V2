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

from flask import Flask, jsonify, request, session, send_from_directory
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

# ─── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')

bcrypt = Bcrypt(app)

# ─── Database ─────────────────────────────────────────────────────────────────

import psycopg2
from flask import g

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(os.environ['DATABASE_URL'])
    return g.db

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
        return jsonify({'error': 'Username already taken'}), 409

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    cur.execute(
        'INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id',
        (username, hashed),
    )
    row = cur.fetchone()
    user_id = row[0] if row else None
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
    cur.execute('SELECT user_id, password FROM users WHERE username = %s', (username,))
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

    # TODO: wire up LLMService from lib/llm_service.py
    # from lib.llm_service import LLMService
    # response = LLMService.instance().chat(session['user_id'], message)

    # Placeholder response until LLM is wired in.
    response = f"(LLM not yet connected) You said: {message}"

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
