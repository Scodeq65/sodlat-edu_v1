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
    form = LinkParentForm()
    if form.validate_on_submit():
        try:
            student = User.query.filter_by(username=form.parent_name.data).first()
            if student and student.parent_id is None:
                student.parent_id = current_user.id
                db.session.commit()
                flash('Parent linked successfully.', 'success')
                return redirect(url_for('main.parent_dashboard'))
            else:
                flash('Student not found or already linked.', 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while linking the parent.', 'danger')

    children = User.query.filter_by(parent_id=current_user.id).all()
    return render_template(
        'parent_dashboard.html',
        title='Parent Dashboard',
        form=form,
        children=children
    )


@main.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('teacher')
def teacher_dashboard():
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template(
        'teacher_dashboard.html',
        title='Teacher Dashboard',
        courses=courses
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


@main.route('/create_course', methods=['GET', 'POST'])
@login_required
@roles_required('teacher')
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            name=form.name.data,
            teacher_id=current_user.id
        )
        try:
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully.', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the course.', 'danger')
    return render_template('create_course.html', title='Create Course', form=form)


@main.route('/create_assignment', methods=['GET', 'POST'])
@login_required
@roles_required('teacher')
def create_assignment():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            content=form.content.data,
            due_date=form.due_date.data,
            course_id=form.course_id.data.id,
            student_id=current_user.id
        )
        try:
            db.session.add(assignment)
            db.session.commit()
            flash('Assignment created successfully.', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the assignment.', 'danger')
    return render_template('create_assignment.html', title='Create Assignment', form=form)


@main.route('/create_progress', methods=['GET', 'POST'])
@login_required
@roles_required('teacher')
def create_progress():
    form = ProgressForm()
    if form.validate_on_submit():
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
            try:
                db.session.add(progress)
                db.session.commit()
                flash('Progress recorded successfully.', 'success')
                return redirect(url_for('main.teacher_dashboard'))
            except SQLAlchemyError:
                db.session.rollback()
                flash('An error occurred while recording progress.', 'danger')
        else:
            flash('Student or course not found.', 'danger')
    return render_template('create_progress.html', title='Record Progress', form=form)

@main.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('teacher')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)
        user.role = form.role.data
        try:
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while updating the user.', 'danger')
    return render_template('update_user.html', title='Update User', form=form, user=user)