"""
Profile and settings management routes.
"""

from flask import render_template, flash, redirect, url_for, request, jsonify, session
from ... import db
from . import bp
from .login import login_required

@bp.route('/account/profile_settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    """Handle profile and settings page."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            success = db.update_user_settings(
                user_id=session['user_id'],
                settings=data
            )
            if success:
                flash('Settings updated successfully', 'success')
                return jsonify({'status': 'success'})
            flash('Error updating settings', 'error')
            return jsonify({'status': 'error'}), 400
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return jsonify({'status': 'error'}), 500

    # GET request - display profile page
    user_data = db.get_user(session['user_id'])
    return render_template('account/profile_settings.html', user=user_data)

@bp.route('/account/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Handle profile information updates."""
    try:
        data = request.form
        success = db.update_user_profile(
            user_id=session['user_id'],
            username=data.get('username'),
            email=data.get('email')
        )
        if success:
            flash('Profile updated successfully', 'success')
        else:
            flash('Error updating profile', 'error')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('auth.profile_settings'))

@bp.route('/account/update_settings', methods=['POST'])
@login_required
def update_settings():
    """Handle settings updates."""
    try:
        data = request.form
        success = db.update_user_settings(
            user_id=session['user_id'],
            notify_search_complete=data.get('notify_search_complete') == 'on',
            notify_account_activity=data.get('notify_account_activity') == 'on',
            default_view=data.get('default_view'),
            api_key=data.get('api_key')
        )
        if success:
            flash('Settings updated successfully', 'success')
        else:
            flash('Error updating settings', 'error')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('auth.profile_settings'))

@bp.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    """Handle account deletion."""
    try:
        confirmation = request.form.get('confirm_delete')
        if confirmation != 'DELETE':
            flash('Please type DELETE to confirm account deletion', 'error')
            return redirect(url_for('auth.profile_settings'))

        success = db.delete_user(session['user_id'])
        if success:
            session.clear()
            flash('Account deleted successfully', 'success')
            return redirect(url_for('auth.login'))
        flash('Error deleting account', 'error')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('auth.profile_settings'))


@bp.route('/account/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change requests."""
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            # Verify current password
            user_data = db.verify_user(
                username=session.get('username'),
                password=current_password,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )

            if not user_data:
                flash('Current password is incorrect', 'error')
                return redirect(url_for('auth.change_password'))

            # Verify new passwords match
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('auth.change_password'))

            # Update password
            success = db.update_password(session['user_id'], new_password)
            if success:
                flash('Password updated successfully', 'success')
                return redirect(url_for('auth.profile_settings'))
            else:
                flash('Error updating password', 'error')

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

        return redirect(url_for('auth.change_password'))

    # GET request - show password change form
    return render_template('account/change_password.html')