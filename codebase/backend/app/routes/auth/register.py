"""
Registration-related routes and functionality.
"""

from flask import request, jsonify, render_template, current_app
from ... import db
from . import bp
from .validators import validate_password, validate_email_address, validate_username
from ...services.email import send_verification_email

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        if not db.check_rate_limit(request.remote_addr, 'register'):
            return jsonify({
                'success': False,
                'error': 'Too many registration attempts. Please try again later.'
            }), 429

        try:
            data = request.json
            if not all([data.get('username'), data.get('email'), data.get('password')]):
                return jsonify({'success': False, 'error': 'Missing required fields'})

            # Validate input
            is_valid, email, error = validate_email_address(data['email'])
            if not is_valid:
                return jsonify({'success': False, 'error': error})

            is_valid, error = validate_password(data['password'])
            if not is_valid:
                return jsonify({'success': False, 'error': error})

            is_valid, error = validate_username(data['username'])
            if not is_valid:
                return jsonify({'success': False, 'error': error})

            # Create user
            user_id = db.create_user(
                username=data['username'],
                email=email,
                password=data['password']
            )

            if user_id:
                try:
                    # Get the user details including activation token
                    user = db.get_user(user_id)
                    if not user:
                        current_app.logger.error(f"Failed to retrieve user after creation: {user_id}")
                        return jsonify({
                            'success': False,
                            'error': 'User creation failed. Please try again.'
                        })

                    # Send verification email
                    if send_verification_email(email, user['activation_token']):
                        return jsonify({
                            'success': True,
                            'message': 'Registration successful. Please check your email to activate your account.'
                        })
                    else:
                        current_app.logger.error(f"Failed to send verification email for user: {user_id}")
                        return jsonify({
                            'success': False,
                            'error': 'Registration successful but failed to send verification email. Please contact support.'
                        })
                except Exception as e:
                    current_app.logger.error(f"Error in email verification process: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'Registration successful but email verification failed. Please contact support.'
                    })
            else:
                return jsonify({'success': False, 'error': 'Registration failed'})

        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    return render_template('register.html')

@bp.route('/activate/<token>', methods=['GET'])
def activate_account(token):
    """Handle account activation."""
    try:
        if db.activate_user(token):
            return render_template('activation_success.html')
        return render_template('activation_failed.html')
    except Exception as e:
        current_app.logger.error(f"Account activation error: {str(e)}")
        return render_template('activation_failed.html', error=str(e))