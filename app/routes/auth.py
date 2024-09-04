#!/usr/bin/python3

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from flask import Blueprint
from app.forms import LoginForm, RegistrationForm
from app.models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route.

    Handles user login and redirects to the appropriate dashboard upon successful authentication.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username_or_email.data) |
            (User.email == form.username_or_email.data)
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome, {user.username}!', 'success')

            # Redirect based on user role
            if user.role == 'Parent':
                return redirect(url_for('main.parent_dashboard'))
            elif user.role == 'Teacher':
                return redirect(url_for('main.teacher_dashboard'))
            elif user.role == 'Student':
                return redirect(url_for('main.student_dashboard'))
            else:
                return redirect(url_for('main.index'))

        else:
            flash('Invalid username/email or password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route.

    Handles new user registrations and redirects to the login page upon successful registration.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
    return render_template('register.html', title='Register', form=form)

@auth.route('/logout')
@login_required
def logout():
    """
    Logout route.

    Logs out the current user and redirects to the homepage.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))