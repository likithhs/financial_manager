"""
FinAI Backend Foundation - Profile Routes Blueprint
Handles user settings and financial baseline profile configuration (/profile).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_helper import login_required, get_current_user_id
from services.user_service import UserService
from services.validators import ValidationError, validate_password

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = get_current_user_id()
    user = UserService.get_by_id(user_id)

    if not user:
        session.clear()
        flash('User account not found. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', 25)
        occupation = request.form.get('occupation', 'Student / Professional').strip()
        financial_exp = request.form.get('financial_exp', 'Beginner')
        investment_exp = request.form.get('investment_exp', 'None')
        new_password = request.form.get('new_password', '').strip()

        if not name:
            flash('Name cannot be empty.', 'danger')
            return render_template('profile.html', user=user)

        try:
            age = int(age) if age else 25
        except ValueError:
            age = 25

        UserService.update_profile(user_id, name, age, occupation, financial_exp, investment_exp)
        session['user_name'] = name

        if new_password:
            try:
                UserService.update_password(user_id, new_password)
                flash('Profile details and password updated successfully.', 'success')
            except ValidationError as ve:
                flash(ve.message, 'danger')
                return redirect(url_for('profile.profile'))
        else:
            flash('Profile information saved.', 'success')

        return redirect(url_for('profile.profile'))

    return render_template('profile.html', user=user)
