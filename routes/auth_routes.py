from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import query_db, execute_db
from extensions import limiter

auth_bp = Blueprint('auth', __name__)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validates password strength according to modern security policies (NIST SP 800-63B):
    - Minimum 12 characters
    - Maximum 128 characters (prevents computational resource exhaustion)
    - Supports long passphrases and password managers
    - Disallows purely whitespace or empty passwords
    """
    if not password:
        return False, "Password cannot be blank."
    if len(password) < 12:
        return False, "Password must be at least 12 characters long. We encourage using a memorable passphrase or password manager."
    if len(password) > 128:
        return False, "Password cannot exceed 128 characters."
    if password != password.strip():
        return False, "Password cannot begin or end with whitespace."
    if not password.strip():
        return False, "Password cannot consist exclusively of whitespace characters."
    return True, ""


from services.auth_helper import (
    login_required,
    admin_required,
    is_authenticated,
    is_admin,
    get_current_user_id,
    get_current_user_role,
)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 15 per hour", methods=["POST"])
def register():
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Please fill in all mandatory fields.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        is_valid_pwd, pwd_error = validate_password_strength(password)
        if not is_valid_pwd:
            flash(pwd_error, 'danger')
            return render_template('register.html')

        existing_user = query_db(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            one=True
        )

        if existing_user:
            flash(
                'If an account with this email address already exists, please sign in. Otherwise check your credentials.',
                'warning'
            )
            return redirect(url_for('auth.login'))

        password_hash = generate_password_hash(password)

        user_id = execute_db("""
            INSERT INTO users (name, email, password, password_hash, role)
            VALUES (%s, %s, %s, %s, 'user')
        """, (name, email, password_hash, password_hash))

        if not user_id:
            user_id = execute_db("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, 'user')
            """, (name, email, password_hash))

        if not user_id:
            user_id = execute_db("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, 'user')
            """, (name, email, password_hash))

        if not user_id:
            flash('Failed to create account. Please try again.', 'danger')
            return render_template('register.html')

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per hour", methods=["POST"])
def login():
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login.html')

        user = query_db(
            "SELECT * FROM users WHERE email = %s",
            (email,),
            one=True
        )

        stored_hash = (user.get('password_hash') or user.get('password') or '') if user else ''
        if user and stored_hash and check_password_hash(stored_hash, password):
            # Session fixation protection: clear old session identifier
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user.get('role', 'user')
            session.permanent = True

            flash(f"Welcome back, {user['name']}!", 'success')

            if session['user_role'] == 'admin':
                return redirect(url_for('admin.dashboard'))

            return redirect(url_for('main.home'))

        flash(
            'Invalid email address or password. Please try again.',
            'danger'
        )

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/settings', methods=['GET', 'POST'])
@auth_bp.route('/profile', endpoint='profile', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per hour", methods=["POST"])
def settings():
    user_id = session['user_id']

    user = query_db(
        "SELECT * FROM users WHERE id = %s",
        (user_id,),
        one=True
    )

    if not user:
        session.clear()
        flash('User account not found. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))

    # Compute formatted joined_date
    created = user.get('created_at')
    if hasattr(created, 'strftime'):
        user['joined_date'] = created.strftime('%B %d, %Y')
    elif isinstance(created, str) and len(created) >= 10:
        try:
            from datetime import datetime
            dt = datetime.strptime(created[:10], '%Y-%m-%d')
            user['joined_date'] = dt.strftime('%B %d, %Y')
        except Exception:
            user['joined_date'] = created[:10]
    else:
        user['joined_date'] = 'Member'

    active_tab = request.args.get('tab', 'account')
    if active_tab not in ['account', 'edit', 'security']:
        active_tab = 'account'

    if request.method == 'POST':
        action = request.form.get('action', 'update_profile')

        if action == 'update_security':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not current_password:
                flash('Please enter your current password.', 'danger')
                return redirect(url_for('auth.settings', tab='security'))

            stored_hash = user.get('password_hash') or user.get('password') or ''
            if not (stored_hash and check_password_hash(stored_hash, current_password)):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('auth.settings', tab='security'))

            is_valid_pwd, pwd_error = validate_password_strength(new_password)
            if not is_valid_pwd:
                flash(pwd_error, 'danger')
                return redirect(url_for('auth.settings', tab='security'))

            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'danger')
                return redirect(url_for('auth.settings', tab='security'))

            new_password_hash = generate_password_hash(new_password)
            execute_db(
                "UPDATE users SET password = %s, password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (new_password_hash, new_password_hash, user_id)
            )

            # Invalidate stale session state and re-issue authenticated credentials
            session.clear()
            session['user_id'] = user_id
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user.get('role', 'user')
            session.permanent = True

            flash('Password updated successfully. Your session has been refreshed.', 'success')
            return redirect(url_for('auth.settings', tab='security'))

        else:
            # action == 'update_profile'
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            age_raw = request.form.get('age', '').strip()
            occupation = request.form.get('occupation', '').strip()
            financial_exp = request.form.get('financial_exp', 'Beginner').strip()
            investment_exp = request.form.get('investment_exp', 'None').strip()

            if not name:
                flash('Full Name is required.', 'danger')
                return redirect(url_for('auth.settings', tab='edit'))

            if not email or '@' not in email or '.' not in email:
                flash('Please enter a valid email address.', 'danger')
                return redirect(url_for('auth.settings', tab='edit'))

            existing = query_db(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (email, user_id),
                one=True
            )
            if existing:
                flash('That email address is already in use by another account.', 'danger')
                return redirect(url_for('auth.settings', tab='edit'))

            if phone:
                import re
                if not re.match(r'^\+?[0-9\s\-().]{7,20}$', phone):
                    flash('Invalid phone number format. Please enter digits with optional +, -, or spaces.', 'danger')
                    return redirect(url_for('auth.settings', tab='edit'))

            age_val = None
            if age_raw:
                try:
                    age_val = int(age_raw)
                    if age_val < 18 or age_val > 120:
                        flash('Age must be between 18 and 120.', 'danger')
                        return redirect(url_for('auth.settings', tab='edit'))
                except ValueError:
                    flash('Age must be a valid whole number.', 'danger')
                    return redirect(url_for('auth.settings', tab='edit'))

            if financial_exp not in ['Beginner', 'Intermediate', 'Advanced']:
                financial_exp = 'Beginner'

            if investment_exp not in ['None', 'Fixed Deposits / Gold', 'Mutual Funds / SIP', 'Direct Stocks / Equity']:
                investment_exp = 'None'

            execute_db("""
                UPDATE users
                SET name = %s, email = %s, phone = %s, address = %s, age = %s,
                    occupation = %s, financial_exp = %s, investment_exp = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                name,
                email,
                phone or None,
                address or None,
                age_val,
                occupation or None,
                financial_exp,
                investment_exp,
                user_id
            ))

            # Optional password update if submitted alongside profile
            new_pwd = request.form.get('new_password', '').strip()
            if new_pwd:
                is_valid_pwd, pwd_error = validate_password_strength(new_pwd)
                if not is_valid_pwd:
                    flash(pwd_error, 'danger')
                    return redirect(url_for('auth.settings', tab='edit'))
                new_hash = generate_password_hash(new_pwd)
                execute_db(
                    "UPDATE users SET password = %s, password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (new_hash, new_hash, user_id)
                )

            # Synchronize session state
            session['user_name'] = name
            session['user_email'] = email

            flash('Profile details updated successfully.', 'success')
            return redirect(url_for('auth.settings', tab='account'))

    return render_template('settings.html', user=user, active_tab=active_tab)

