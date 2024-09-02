#!/usr/bin/python3
"""
Main route module for the SodLat Edu Solution project.
"""

from flask import (
    Blueprint, render_template, url_for, flash, redirect, request
)
from flask_login import (
    login_user, current_user, logout_user, login_required
)
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.forms import (
    CourseForm, AssignmentForm, ProgressForm, UserForm, LoginForm, 
    RegistrationForm, LinkParentForm
)
from app.models import User, Course, Assignment, Progress

# Define the blueprint for the main routes
bp = Blueprint('main_bp', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """
    Homepage route.

    Returns:
        The rendered homepage template.
    """
    return render_template('index.html', title='Home')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page route.

    Handles user login and redirects to the appropriate page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username_or_email.data) |
            (User.email == form.username_or_email.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        
        flash('Login Unsuccessful. Please check username/email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration page route.

    Handles user registration and redirects to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('main.login'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')
    
    return render_template('register.html', title='Register', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard route.

    Redirects the user to the appropriate dashboard based on their role.
    """
    try:
        if current_user.role == 'parent':
            return redirect(url_for('main.parent_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('main.teacher_dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('main.student_dashboard'))
        else:
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('main.index'))
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while processing your request.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/parent_dashboard', methods=['GET', 'POST'])
@login_required
def parent_dashboard():
    """
    Parent dashboard route.

    Allows parents to link their children to their accounts and view progress.
    """
    if current_user.role != 'parent':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    form = LinkParentForm()
    if form.validate_on_submit():
        try:
            student = User.query.filter_by(username=form.student_name.data).first()
            if student and student.parent_id is None:
                student.parent_id = current_user.id
                db.session.commit()
                flash(f'Child {student.username} added successfully.', 'success')
            elif student:
                flash(f'Child {student.username} is already linked to another parent.', 'warning')
            else:
                flash('Student not found.', 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while linking the child.', 'danger')

    try:
        children_progress = Progress.query.filter_by(student_id=current_user.id).all()
    except SQLAlchemyError:
        db.session.rollback()
        children_progress = []
        flash('An error occurred while fetching progress data.', 'danger')

    return render_template(
        'parent_dashboard.html', 
        title='Parent Dashboard', 
        form=form, 
        progress=children_progress
    )

@bp.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    """
    Teacher dashboard route.

    Allows teachers to manage user accounts and course-related activities.
    """
    if current_user.role != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    course_form = CourseForm()
    assignment_form = AssignmentForm()
    user_form = UserForm()

    if course_form.validate_on_submit():
        course = Course(name=course_form.name.data, teacher_id=current_user.id)
        try:
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully!', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the course.', 'danger')

    if assignment_form.validate_on_submit():
        assignment = Assignment(
            title=assignment_form.title.data,
            content=assignment_form.content.data,
            due_date=assignment_form.due_date.data,
            course_id=assignment_form.course_id.data.id,
            student_id=current_user.id
        )
        try:
            db.session.add(assignment)
            db.session.commit()
            flash('Assignment created successfully!', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the assignment.', 'danger')

    if user_form.validate_on_submit():
        user = User(
            username=user_form.username.data,
            email=user_form.email.data,
            role=user_form.role.data
        )
        user.set_password(user_form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('User created/updated successfully!', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating/updating the user.', 'danger')

    return render_template(
        'teacher_dashboard.html',
        title='Teacher Dashboard',
        course_form=course_form,
        assignment_form=assignment_form,
        user_form=user_form
    )

@bp.route('/student_dashboard', methods=['GET', 'POST'])
@login_required
def student_dashboard():
    """
    Student dashboard route.

    Allows students to link their parents to their accounts and update progress.
    """
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    form = ProgressForm()
    if form.validate_on_submit():
        try:
            student = User.query.filter_by(username=form.student_name.data).first()
            course = Course.query.filter_by(name=form.teacher_name.data).first()
            if student and course:
                progress = Progress(
                    student_id=student.id,
                    course_id=course.id,
                    grade=form.grade.data,
                    attendance=form.attendance.data,
                    overall_performance=form.overall_performance.data
                )
                db.session.add(progress)
                db.session.commit()
                flash('Progress updated successfully!', 'success')
            else:
                flash('Student or Course not found.', 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while updating progress.', 'danger')

    return render_template(
        'student_dashboard.html', 
        title='Student Dashboard', 
        form=form
    )

@bp.route('/logout')
def logout():
    """
    Logout route.

    Logs out the user and redirects to the homepage.
    """
    logout_user()
    return redirect(url_for('main.index'))


# Custom 403 error handler
@bp.app_errorhandler(403)
def forbidden_error(error):
    """Custom handler for 403 Forbidden errors."""
    return render_template('403.html', title='Forbidden'), 403