#!/usr/bin/python3
"""
Main route module for the SodLat Edu Solution project.
"""

from flask import (
    Blueprint, render_template, url_for, flash, redirect, request
)
from flask_login import (
    current_user, login_required
)
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from app.db import db
from app.forms import (
    CourseForm, AssignmentForm, ProgressForm, UserForm, LinkParentForm
)
from app.models import User, Course, Assignment, Progress

# Define the blueprint for the main routes
main = Blueprint('main', __name__)


# Define the roles_required decorator within main.py
def roles_required(*roles):
    """
    Custom decorator to enforce role-based access control.

    :param roles: List of roles allowed to access the route.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', title='Home')


@main.route('/dashboard')
@login_required
def dashboard():
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


@main.route('/parent_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('parent')
def parent_dashboard():
    link_child_form = LinkParentForm()
    
    if link_child_form.validate_on_submit():
        try:
            child = User.query.filter_by(username=link_child_form.student_username.data).first()
            if child and child.parent_id is None:
                child.parent_id = current_user.id
                db.session.commit()
                flash('Child linked successfully.', 'success')
                return redirect(url_for('main.parent_dashboard'))
            else:
                flash('Child not found or already linked.', 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')

    # Fetch linked children and their progress
    children = User.query.filter_by(parent_id=current_user.id).all()
    progress = {child.id: Progress.query.filter_by(student_id=child.id).all() for child in children}

    return render_template(
        'parent_dashboard.html',
        link_child_form=link_child_form,
        children=children,
        progress=progress
    )


@main.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('teacher')
def teacher_dashboard():
    assignment_form = AssignmentForm()
    course_form = CourseForm()
    progress_form = ProgressForm()
    user_form = UserForm()

    # Handle course creation
    if course_form.submit.data and course_form.validate_on_submit():
        try:
            new_course = Course(name=course_form.name.data, teacher_id=current_user.id)
            db.session.add(new_course)
            db.session.commit()
            flash('Course created successfully.', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the course.', 'danger')

    # Handle assignment creation
    if assignment_form.submit.data and assignment_form.validate_on_submit():
        try:
            # Ensure course_id is valid and correctly assigned
            course_id = assignment_form.course_id.data
            course = Course.query.get(course_id)
            if not course:
                flash('Invalid course selected.', 'danger')
            else:
                new_assignment = Assignment(
                title=assignment_form.title.data,
                content=assignment_form.content.data,
                due_date=assignment_form.due_date.data,
                course_id=course.id,
                student_id=None
            )
            db.session.add(new_assignment)
            db.session.commit()
            flash('Assignment created successfully.', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the assignment.', 'danger')


    # Handle progress creation
    if progress_form.submit.data and progress_form.validate_on_submit():
        student = User.query.filter_by(username=progress_form.student_name.data).first()
        if not student:
            flash('Student not found.', 'danger')
        else:
            try:
                new_progress = Progress(
                    student_id=student.id,
                    course_id=progress_form.course_id.data,
                    grade=progress_form.grade.data,
                    days_present=progress_form.days_present.data,
                    days_absent=progress_form.days_absent.data,
                    overall_performance=progress_form.overall_performance.data
                )
                db.session.add(new_progress)
                db.session.commit()
                flash('Progress recorded successfully.', 'success')
                return redirect(url_for('main.teacher_dashboard'))
            except SQLAlchemyError:
                db.session.rollback()
                flash('An error occurred while recording progress.', 'danger')


    # Handle user updates
    if user_form.submit.data and user_form.validate_on_submit():
        user = User.query.get(user_form.id.data)
        if user:
            user.username = user_form.username.data
            user.email = user_form.email.data
            if user_form.password.data:
                user.set_password(user_form.password.data)
            user.role = user_form.role.data
            try:
                db.session.commit()
                flash('User updated successfully.', 'success')
                return redirect(url_for('main.teacher_dashboard'))
            except SQLAlchemyError:
                db.session.rollback()
                flash('An error occurred while updating the user.', 'danger')
        else:
            flash('User not found.', 'danger')

    # Retrieve courses and users
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    users = User.query.all()

    return render_template(
        'teacher_dashboard.html',
        title='Teacher Dashboard',
        courses=courses,
        assignment_form=assignment_form,
        course_form=course_form,
        progress_form=progress_form,
        user_form=user_form,
        users=users
    )

@main.route('/student_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('student')
def student_dashboard():
    assignments = Assignment.query.filter_by(student_id=current_user.id).all()
    progress = Progress.query.filter_by(student_id=current_user.id).all()
    return render_template(
        'student_dashboard.html',
        title='Student Dashboard',
        assignments=assignments,
        progress=progress
    )
