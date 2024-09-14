#!/usr/bin/python3

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from flask import Blueprint
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.db import db


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
            if user.is_parent:
                return redirect(url_for('main.parent_dashboard'))
            elif user.is_teacher:
                return redirect(url_for('main.teacher_dashboard'))
            elif user.is_student:
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
        # Create the user
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        
        # Assign role based on form
        if form.role.data == 'parent':
            user.is_parent = True
            user.role = 'parent'
        elif form.role.data == 'teacher':
            user.is_teacher = True
            user.role = 'teacher'
        elif form.role.data == 'student':
            user.is_student = True
            user.role = 'student'
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
