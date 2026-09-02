from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import query_db, execute_db

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the administrator panel.', 'warning')
            return redirect(url_for('auth.login'))

        if session.get('user_role') != 'admin':
            flash('Access denied: Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

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

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        existing_user = query_db(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            one=True
        )

        if existing_user:
            flash(
                'An account with this email address already exists. Please log in.',
                'warning'
            )
            return redirect(url_for('auth.login'))

        password_hash = generate_password_hash(password)

        user_id = execute_db("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'user')
        """, (name, email, password_hash))

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

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

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user.get('role', 'user')

            flash(f"Welcome back, {user['name']}!", 'success')

            if session['user_role'] == 'admin':
                return redirect(url_for('admin.dashboard'))

            return redirect(url_for('dashboard'))

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


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']

    user = query_db(
        "SELECT * FROM users WHERE id = %s",
        (user_id,),
        one=True
    )

    if not user:
        session.clear()
        flash('User account not found.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        new_password = request.form.get('new_password', '')

        if not name:
            flash('Name cannot be empty.', 'danger')
            return render_template('profile.html', user=user)

        execute_db(
            "UPDATE users SET name = %s WHERE id = %s",
            (name, user_id)
        )

        session['user_name'] = name

        if new_password:
            if len(new_password) < 6:
                flash(
                    'New password must be at least 6 characters long.',
                    'danger'
                )
                return redirect(url_for('auth.profile'))

            password_hash = generate_password_hash(new_password)

            execute_db(
                "UPDATE users SET password = %s WHERE id = %s",
                (password_hash, user_id)
            )

            flash(
                'Profile and password updated successfully.',
                'success'
            )
        else:
            flash('Profile details updated successfully.', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=user)
