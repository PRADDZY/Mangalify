# web/app.py

import os
import asyncio
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

# Import database manager
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_manager import db_manager

app = Flask(__name__)
app.secret_key = os.getenv("WEB_SECRET_KEY", "change-this-secret-key-in-production")
CORS(app)

# Authentication configuration
WEB_ADMIN_PASSWORD = os.getenv("WEB_ADMIN_PASSWORD", "admin")

# Helper to run async functions in Flask routes
def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
@login_required
def index():
    """Dashboard home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == WEB_ADMIN_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/analytics')
@login_required
@async_route
async def analytics():
    """Analytics page"""
    total_birthdays = await db_manager.get_total_birthdays()
    total_wishes = await db_manager.get_total_manual_wishes()
    birthdays_by_month = await db_manager.get_birthdays_by_month()
    upcoming_birthdays = await db_manager.get_upcoming_birthdays(30)
    
    return render_template('analytics.html',
                         total_birthdays=total_birthdays,
                         total_wishes=total_wishes,
                         birthdays_by_month=birthdays_by_month,
                         upcoming_birthdays=upcoming_birthdays)

@app.route('/birthdays')
@login_required
@async_route
async def birthdays():
    """Manage birthdays page"""
    all_birthdays = await db_manager.get_all_birthdays()
    return render_template('birthdays.html', birthdays=all_birthdays)

@app.route('/wishes')
@login_required
@async_route
async def wishes():
    """Manage wishes page"""
    all_wishes = await db_manager.get_all_manual_wishes()
    return render_template('wishes.html', wishes=all_wishes)

# API Routes
@app.route('/api/stats')
@login_required
@async_route
async def api_stats():
    """API endpoint for dashboard statistics"""
    total_birthdays = await db_manager.get_total_birthdays()
    total_wishes = await db_manager.get_total_manual_wishes()
    birthdays_by_month = await db_manager.get_birthdays_by_month()
    upcoming_birthdays = await db_manager.get_upcoming_birthdays(7)
    
    return jsonify({
        'total_birthdays': total_birthdays,
        'total_wishes': total_wishes,
        'birthdays_by_month': birthdays_by_month,
        'upcoming_birthdays': upcoming_birthdays
    })

@app.route('/api/birthdays')
@login_required
@async_route
async def api_birthdays():
    """API endpoint for all birthdays"""
    birthdays = await db_manager.get_all_birthdays()
    return jsonify(birthdays)

@app.route('/api/birthdays/<int:user_id>', methods=['DELETE'])
@login_required
@async_route
async def api_delete_birthday(user_id):
    """API endpoint to delete a birthday"""
    success = await db_manager.delete_birthday(user_id)
    return jsonify({'success': success})

@app.route('/api/wishes')
@login_required
@async_route
async def api_wishes():
    """API endpoint for all wishes"""
    wishes = await db_manager.get_all_manual_wishes()
    # Convert ObjectId to string for JSON serialization
    for wish in wishes:
        wish['_id'] = str(wish['_id'])
    return jsonify(wishes)

@app.route('/api/wishes/<wish_id>', methods=['DELETE'])
@login_required
@async_route
async def api_delete_wish(wish_id):
    """API endpoint to delete a wish"""
    success = await db_manager.delete_manual_wish(wish_id)
    return jsonify({'success': success})

if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', 5000))
    host = os.getenv('WEB_HOST', '0.0.0.0')
    debug = os.getenv('WEB_DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
