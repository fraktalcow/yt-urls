import os
import json
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from database import DiceDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.urandom(24)

# Initialize database
db = DiceDB()

# Admin authentication
auth = HTTPBasicAuth()
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # In production, use strong passwords and store securely

# Setup admin user
users = {
    ADMIN_USERNAME: generate_password_hash(ADMIN_PASSWORD)
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Serve the main application page."""
    return app.send_static_file('index.html')

@app.route('/videos.json')
def get_videos():
    """Return videos data as JSON."""
    try:
        videos = db.get('videos')
        if not videos:
            # Fallback to file if not in database
            if os.path.exists('videos.json'):
                with open('videos.json', 'r', encoding='utf-8') as f:
                    videos = json.load(f)
                # Store in database for future requests
                db.set('videos', videos)
            else:
                videos = {}
        return jsonify(videos)
    except Exception as e:
        logger.error(f"Error retrieving videos: {e}")
        return jsonify({"error": "Failed to retrieve videos data"}), 500

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard home page."""
    return render_template('admin/dashboard.html', title="Admin Dashboard")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users.get(username), password):
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html', title="Admin Login")

@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/videos')
@admin_required
def admin_videos():
    """Admin videos management page."""
    videos = db.get('videos', {})
    return render_template('admin/videos.html', title="Manage Videos", videos=videos)

@app.route('/admin/db')
@admin_required
def admin_db():
    """Admin database management page."""
    keys = db.list_keys()
    return render_template('admin/db.html', title="Database Management", keys=keys)

@app.route('/admin/db/view/<key>')
@admin_required
def admin_db_view(key):
    """View database entry."""
    value = db.get(key)
    return render_template('admin/db_view.html', title=f"View '{key}'", key=key, value=value)

@app.route('/admin/db/delete/<key>', methods=['POST'])
@admin_required
def admin_db_delete(key):
    """Delete database entry."""
    if db.delete(key):
        flash(f"Key '{key}' deleted successfully", 'success')
    else:
        flash(f"Failed to delete key '{key}'", 'error')
    return redirect(url_for('admin_db'))

@app.route('/admin/db/backup', methods=['POST'])
@admin_required
def admin_db_backup():
    """Create database backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_db_{timestamp}.pkl"
    
    if db.backup(backup_file):
        flash(f"Database backed up to {backup_file}", 'success')
    else:
        flash("Failed to create database backup", 'error')
    
    return redirect(url_for('admin_db'))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates/admin', exist_ok=True)
    
    # Create admin templates
    with open('templates/admin/base.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Admin</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/admin">Admin Portal</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/admin/videos">Videos</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/admin/db">Database</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/">View Site</a>
                    </li>
                </ul>
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/admin/logout">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category if category != 'error' else 'danger' }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <h1 class="mb-4">{{ title }}</h1>
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')
    
    with open('templates/admin/login.html', 'w') as f:
        f.write('''{% extends "admin/base.html" %}
{% block content %}
<div class="row">
    <div class="col-md-6 offset-md-3">
        <div class="card">
            <div class="card-body">
                <form method="post">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Login</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
    
    with open('templates/admin/dashboard.html', 'w') as f:
        f.write('''{% extends "admin/base.html" %}
{% block content %}
<div class="row">
    <div class="col-md-4">
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Videos Management</h5>
                <p class="card-text">View and manage YouTube video data</p>
                <a href="/admin/videos" class="btn btn-primary">Manage Videos</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Database Management</h5>
                <p class="card-text">Manage DiceDB database entries</p>
                <a href="/admin/db" class="btn btn-primary">Manage Database</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">View Site</h5>
                <p class="card-text">View the public-facing website</p>
                <a href="/" class="btn btn-primary">Go to Site</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
    
    with open('templates/admin/videos.html', 'w') as f:
        f.write('''{% extends "admin/base.html" %}
{% block content %}
<div class="mb-4">
    <a href="/admin" class="btn btn-secondary">← Back to Dashboard</a>
</div>

{% if videos %}
    {% for category, video_list in videos.items() %}
        <div class="card mb-4">
            <div class="card-header">
                <h2>{{ category }}</h2>
            </div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Channel</th>
                            <th>Published At</th>
                            <th>URL</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for video in video_list %}
                            <tr>
                                <td>{{ video.title }}</td>
                                <td>{{ video.channel }}</td>
                                <td>{{ video.publishedAt }}</td>
                                <td><a href="{{ video.url }}" target="_blank">View</a></td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    {% endfor %}
{% else %}
    <div class="alert alert-info">No videos data found.</div>
{% endif %}
{% endblock %}''')
    
    with open('templates/admin/db.html', 'w') as f:
        f.write('''{% extends "admin/base.html" %}
{% block content %}
<div class="mb-4">
    <a href="/admin" class="btn btn-secondary">← Back to Dashboard</a>
    <form method="post" action="/admin/db/backup" class="d-inline ms-2">
        <button type="submit" class="btn btn-success">Create Backup</button>
    </form>
</div>

{% if keys %}
    <div class="card">
        <div class="card-body">
            <h2>Database Keys</h2>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Key</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for key in keys %}
                        <tr>
                            <td>{{ key }}</td>
                            <td>
                                <a href="/admin/db/view/{{ key }}" class="btn btn-sm btn-info">View</a>
                                <form method="post" action="/admin/db/delete/{{ key }}" class="d-inline ms-2" onsubmit="return confirm('Are you sure?')">
                                    <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                                </form>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
{% else %}
    <div class="alert alert-info">No database keys found.</div>
{% endif %}
{% endblock %}''')
    
    with open('templates/admin/db_view.html', 'w') as f:
        f.write('''{% extends "admin/base.html" %}
{% block content %}
<div class="mb-4">
    <a href="/admin/db" class="btn btn-secondary">← Back to Database</a>
</div>

<div class="card">
    <div class="card-header">
        <h2>Key: {{ key }}</h2>
    </div>
    <div class="card-body">
        <h3>Value:</h3>
        <pre class="bg-light p-3 rounded">{{ value|pprint }}</pre>
    </div>
</div>
{% endblock %}''')
    
    # Start the server
    app.run(host='0.0.0.0', port=8000, debug=True) 