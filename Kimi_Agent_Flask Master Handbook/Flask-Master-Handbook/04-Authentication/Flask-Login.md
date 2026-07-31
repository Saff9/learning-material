---
title: Flask-Login
description: Production-ready user session management for Flask — login, logout, remember me, and user loading
chapter: 04-Authentication
tags:
  - flask-login
  - authentication
  - sessions
  - user-management
  - login-manager
difficulty: Intermediate
prerequisites:
  - [[04-Authentication/Authentication-Overview]]
  - [[03-Database/Flask-SQLAlchemy]]
---

# Flask-Login

> Flask-Login is the de facto standard for user session management in Flask. It provides the `login_user()`, `logout_user()`, and `login_required` utilities that production Flask applications rely on. This chapter covers everything from basic setup to advanced patterns like remember-me functionality and custom user loading.

## Learning Objectives

After completing this chapter, you will be able to:

- Set up Flask-Login with your User model
- Implement login, logout, and remember-me functionality
- Use `login_required` and `fresh_login_required` decorators
- Customize the login manager and user loader
- Implement account activation and password reset workflows
- Handle anonymous users and unauthorized access

## What Is Flask-Login?

Flask-Login is an extension that provides user session management for Flask. It handles:

- Storing and retrieving the active user's ID in the session
- `login_user()` — Log a user in
- `logout_user()` — Log a user out
- `login_required` — Protect routes that require authentication
- `current_user` — Access the authenticated user anywhere
- Remember me functionality
- Session protection against tampering

Flask-Login does NOT:
- Handle user registration
- Restrict views by roles or permissions
- Hash passwords
- Handle form validation

You combine it with Flask-WTF (forms), Werkzeug (password hashing), and your own business logic.

## Installation and Setup

```bash
pip install flask-login
```

### Basic Setup

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Configure login behavior
login_manager.login_view = 'auth.login'        # Route to redirect unauthenticated users
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
```

### The User Model

Your User model must implement the `UserMixin` properties:

```python
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True)  # Note: not named is_active (conflict with mixin)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Override UserMixin property
    @property
    def is_active(self):
        return self.is_active_user
```

`UserMixin` provides default implementations of:
- `is_authenticated` — True if user has valid credentials
- `is_active` — True if account is active
- `is_anonymous` — False for real users
- `get_id()` — Returns the user's ID

### User Loader

Flask-Login needs a function to load a user from the database given their ID:

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

This is called automatically on each request to load the current user.

## Login and Logout

### Login

```python
from flask import request, redirect, url_for, flash, render_template
from flask_login import login_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember_me') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html')
```

The `remember=True` parameter enables the remember-me cookie, which keeps the user logged in across browser sessions.

### Logout

```python
from flask_login import logout_user

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
```

### Protecting Routes

```python
from flask_login import login_required

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
```

Unauthenticated users are redirected to the login view configured in `login_manager.login_view`.

### The `current_user` Proxy

```python
from flask_login import current_user

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return f'Hello, {current_user.username}!'
    return redirect(url_for('login'))
```

`current_user` works like `request` — it is a context-local proxy that points to the authenticated user (or an `AnonymousUserMixin` instance if not logged in).

## Remember Me

When `login_user(user, remember=True)` is called, Flask-Login sets a remember-me cookie with a token that identifies the user. On subsequent visits, if the session has expired but the remember-me cookie is present, the user is automatically logged back in.

### Configuration

```python
from datetime import timedelta

app.config.update(
    REMEMBER_COOKIE_NAME='remember_token',
    REMEMBER_COOKIE_DURATION=timedelta(days=14),
    REMEMBER_COOKIE_SECURE=True,       # HTTPS only
    REMEMBER_COOKIE_HTTPONLY=True,     # No JavaScript access
    REMEMBER_COOKIE_SAMESITE='Lax',
)
```

### Token Storage

Flask-Login stores a token (not the user's ID) in the remember-me cookie. The token is a signed combination of the user ID and a hash of the user's password hash. If the user changes their password, the remember-me token becomes invalid — a security feature.

## Session Protection

Flask-Login provides session protection against session fixation and cookie theft:

```python
login_manager.session_protection = 'strong'  # Default: 'basic'
```

- `'basic'` — Tracks IP address and user agent
- `'strong'` — Invalidates session if IP or user agent changes
- `None` — Disables session protection

## Custom Unauthorized Handler

```python
@login_manager.unauthorized_handler
def unauthorized():
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required'}), 401
    flash('Please log in to access this page.', 'info')
    return redirect(url_for('auth.login', next=request.path))
```

## Account Activation

Implement email-based account activation:

```python
from itsdangerous import URLSafeTimedSerializer

@app.route('/register', methods=['POST'])
def register():
    # ... create user with is_active=False ...
    
    # Send activation email
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    send_email(user.email, 'Confirm Your Account', 'email/confirm', confirm_url=confirm_url)
    
    flash('A confirmation email has been sent.', 'info')
    return redirect(url_for('auth.login'))

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
    except:
        return False
    return email

@app.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    if user.is_active_user:
        flash('Account already confirmed.', 'info')
    else:
        user.is_active_user = True
        db.session.commit()
        flash('Your account has been confirmed!', 'success')
    
    login_user(user)
    return redirect(url_for('main.index'))
```

## Password Reset

```python
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email(user.email, 'Password Reset', 'email/reset', reset_url=reset_url)
        
        # Always show same message to prevent email enumeration
        flash('If an account exists, a reset email has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_request.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token, expiration=86400)  # 24 hours
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    
    if request.method == 'POST':
        password = request.form['password']
        user.set_password(password)
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')
```

## Common Mistakes

**Mistake: Not setting `SECRET_KEY` before using Flask-Login**
Flask-Login uses the secret key to sign remember-me tokens. Without it, remember-me will not work.

**Mistake: Forgetting `user_loader`**
Without the user loader function, Flask-Login cannot load users and `current_user` will always be anonymous.

**Mistake: Not overriding `is_active` correctly**
If your database column is named `is_active`, it may conflict with `UserMixin`. Rename the column or override the property.

**Mistake: Open redirect vulnerability**
Always validate the `next` parameter after login to prevent open redirects.

## Best Practices

- Use `UserMixin` for the basic interface
- Always implement the `user_loader` callback
- Set `login_view` on the LoginManager
- Validate the `next` parameter after login
- Use strong session protection
- Set secure attributes on remember-me cookies
- Send confirmation emails for new registrations
- Use time-limited tokens for password resets
- Show generic messages to prevent user enumeration

## Exercises

1. **Setup**: Set up Flask-Login with a User model. Implement registration, login, and logout.

2. **Remember Me**: Add remember-me functionality with secure cookie settings.

3. **Email Confirmation**: Implement email-based account activation with expiring tokens.

4. **Password Reset**: Implement a complete password reset flow with email tokens.

5. **Session Protection**: Test session protection by changing your user agent and observing behavior.

## Quiz

**Question 1**: What does Flask-Login provide? What does it NOT provide?

**Question 2**: What properties must a User class implement for Flask-Login?

**Question 3**: What is the purpose of the `user_loader` callback?

**Question 4**: How does remember-me functionality work in Flask-Login?

**Question 5**: Why should you validate the `next` parameter after login?

## Interview Questions

1. "How does Flask-Login work? What does it provide?"

2. "Explain the difference between `login_required` and `fresh_login_required`."

3. "How would you implement 'remember me' functionality securely?"

4. "What is session protection in Flask-Login? How does it work?"

5. "How would you implement email confirmation for new registrations?"

## Related Chapters

- [[04-Authentication/Flask-WTF]] — Form handling with CSRF protection
- [[04-Authentication/Flask-Mail]] — Sending confirmation and reset emails
- [[04-Authentication/WTForms]] — Form validation
- [[08-Security/Session-Security]] — Session security deep dive

## Official Documentation References

- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Flask-Login User Mixin](https://flask-login.readthedocs.io/en/latest/#flask_login.UserMixin)
- [Flask-Login LoginManager](https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager)

---

*Previous: [[04-Authentication/Authentication-Overview]] | Next: [[04-Authentication/Flask-WTF]]*