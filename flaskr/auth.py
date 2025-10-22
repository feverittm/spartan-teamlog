"""
Authentication module for Spartan Teamlog.
Provides simple username/password authentication with session management.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import check_password_hash

# Simple hardcoded credentials (in production, use a database)
ADMIN_CREDENTIALS = {
    'admin': 'pbkdf2:sha256:600000$YRGDxPjoDys8ekXn$1b25b68e4291c1b51d8e7af9fe9cb36cc14ca9fbd644ceebf4f9e71313b17d98',  # password: admin123
    'coach': 'pbkdf2:sha256:600000$swaeMnr3FukD5ogm$404792d935cd6ce1c8ea83e89333431fb611b5c60563dff00e45d7df95d97e4a'   # password: coach456
}

auth = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    """Decorator to require login for a view."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('You must be logged in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth.before_app_request
def load_logged_in_user():
    """Load user info into g.user before each request."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = user_id


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif username not in ADMIN_CREDENTIALS:
            error = 'Invalid username or password.'
        elif not check_password_hash(ADMIN_CREDENTIALS[username], password):
            error = 'Invalid username or password.'

        if error is None:
            session.clear()
            session['user_id'] = username
            flash(f'Welcome back, {username.title()}!', 'success')
            
            # Redirect to the page they were trying to access, or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))

        flash(error, 'error')

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    """Handle user logout."""
    username = session.get('user_id', 'User')
    session.clear()
    flash(f'Goodbye, {username.title()}!', 'info')
    return redirect(url_for('main.index'))


# Helper function to generate password hashes (for development use)
def generate_password_hash(password):
    """Generate a password hash for the given password."""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)


# For testing/development - uncomment to generate new hashes
# if __name__ == '__main__':
#     print("admin123:", generate_password_hash('admin123'))
#     print("coach456:", generate_password_hash('coach456'))