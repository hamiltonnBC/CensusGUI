"""
Login-related routes and functionality.
"""

from flask import request, jsonify, session, redirect, url_for, render_template
from functools import wraps
from ... import db
from . import bp

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'session_token' not in session:
            return redirect(url_for('auth.login'))

        user_id = db.verify_session(
            session_token=session['session_token'],
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )

        if not user_id:
            session.clear()
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        if not db.check_rate_limit(request.remote_addr, 'login'):
            return jsonify({
                'success': False,
                'error': 'Too many login attempts. Please try again later.'
            }), 429

        data = request.json
        user = db.verify_user(
            username=data['username'],
            password=data['password'],
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )

        if user:
            if not user.get('is_active', False):
                return jsonify({
                    'success': False,
                    'error': 'Please verify your email address.'
                })

            session_token = db.create_session(
                user_id=user['user_id'],
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )

            if session_token:
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['session_token'] = session_token
                return jsonify({'success': True})

        return jsonify({'success': False, 'error': 'Invalid credentials'})

    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Handle user logout."""
    if 'session_token' in session:
        db.invalidate_session(session['session_token'])
    session.clear()
    return redirect(url_for('main.index'))