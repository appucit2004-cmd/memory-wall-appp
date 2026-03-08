"""
Digital Memory Wall - Flask Backend
A private digital memory diary where people can submit messages about you.
Only admin can view submissions.
"""

import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


def get_db_connection():
    """Create database connection and return it."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with memories table."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            photo TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def admin_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def count_words(text):
    """Count words in text."""
    if not text or not text.strip():
        return 0
    return len(text.split())


# ==================== ROUTES ====================

@app.route('/')
def root():
    """Redirect to loading page when website opens."""
    return redirect(url_for('loading'))


@app.route('/home')
def index():
    """Landing page - no memories visible to visitors."""
    return render_template('index.html')


@app.route('/loading')
def loading():
    """Loading page - animated intro. Redirects to home after animation."""
    return render_template('loading.html')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    """Memory submission page."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        message = request.form.get('message', '').strip()
        photo = request.files.get('photo')

        # Validation
        errors = []
        if not name:
            errors.append('Name is required.')
        if not message:
            errors.append('Message is required.')
        
        word_count = count_words(message)
        if word_count < 2000:
            errors.append(f'Message must contain at least 2000 words. Current: {word_count} words.')
        
        if not photo or photo.filename == '':
            errors.append('Photo is required.')
        elif photo and not allowed_file(photo.filename):
            errors.append('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP')

        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        # Save photo
        filename = secure_filename(photo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        photo.save(photo_path)
        photo_url = f"/static/uploads/{unique_filename}"

        # Save to database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO memories (name, photo, message) VALUES (?, ?, ?)',
            (name, photo_url, message)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Your memory has been submitted successfully!'})

    return render_template('submit.html')


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard - view all memories."""
    search = request.args.get('search', '').strip()
    conn = get_db_connection()
    
    if search:
        memories = conn.execute(
            'SELECT * FROM memories WHERE name LIKE ? OR message LIKE ? ORDER BY created_at DESC',
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        memories = conn.execute(
            'SELECT * FROM memories ORDER BY created_at DESC'
        ).fetchall()
    
    conn.close()
    
    # Convert to list of dicts for template
    memories_list = [dict(m) for m in memories]
    return render_template('dashboard.html', memories=memories_list, search=search)


@app.route('/delete-memory/<int:memory_id>', methods=['POST'])
@admin_required
def delete_memory(memory_id):
    """Delete a memory (admin only)."""
    conn = get_db_connection()
    memory = conn.execute('SELECT * FROM memories WHERE id = ?', (memory_id,)).fetchone()
    
    if memory:
        # Delete photo file if exists
        photo_url = memory['photo']
        if photo_url.startswith('/static/'):
            full_path = os.path.join(os.path.dirname(__file__), photo_url[1:])
        else:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_url)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except OSError:
                pass
        
        conn.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
        conn.commit()
        flash('Memory deleted successfully.', 'success')
    
    conn.close()
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    init_db()
    # For deployment platforms, respect PORT env var
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
