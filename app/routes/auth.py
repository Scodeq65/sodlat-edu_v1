from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.routes import bp
from app.forms import LoginForm, RegistrationForm
from app.models import User, db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username_or_email.data) |
                                 (User.email == form.username_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))