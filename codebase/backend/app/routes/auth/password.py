"""
Password reset functionality.
"""

from flask import request, jsonify, render_template
from ... import db
from . import bp
from .validators import validate_password

@bp.route('/reset-password', methods=['GET', 'POST'])
def request_password_reset():
    """Handle password reset requests."""
    if request.method == 'POST':
        if not db.check_rate_limit(request.remote_addr, 'password_reset'):
            return jsonify({
                'success': False,
                'error': 'Too many reset attempts. Please try again later.'
            }), 429

        data = request.json
        email = data.get('email')
        if db.create_password_reset_token(email):
            # Send password reset email (implement this later)
            pass
        return jsonify({
            'success': True,
            'message': 'If an account exists, you will receive reset instructions.'
        })
    return render_template('security/request_reset.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if request.method == 'POST':
        data = request.json
        new_password = data.get('password')

        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg})

        if db.reset_password(token, new_password):
            return jsonify({'success': True, 'message': 'Password updated successfully.'})
        return jsonify({'success': False, 'error': 'Invalid or expired reset token.'})

    return render_template('security/reset_password.html')
