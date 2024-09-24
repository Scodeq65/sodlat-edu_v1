#!/usr/bin/python3
"""
Main route module for the SodLat Edu Solution project.
"""

import os
from flask import (
    Blueprint, render_template, url_for, flash, redirect, request, current_app
)
from flask_login import (
    current_user, login_required
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from functools import wraps
from app.db import db
from app.forms import (
    CourseForm, AssignmentForm, ProgressForm, UserForm, LinkParentForm, AttendanceForm, AssignmentSubmissionForm
)
from app.models import User, Course, Assignment, Progress, AssignmentSubmission

# Helper function for file uploads
def save_assignment_file(submission_file):
    """Helper function to save the uploaded assignment file."""
    filename = secure_filename(submission_file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    submission_file.save(file_path)
    return filename

# Define the blueprint for the main routes
main = Blueprint('main', __name__)

# Define the roles_required decorator within main.py
def roles_required(*roles):
    """
    Custom decorator to enforce role-based access control.

    :param roles: List of role attributes allowed to access the route (e.g., 'is_teacher').
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not any(getattr(current_user, role, False) for role in roles):
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main.route('/')
@main.route('/Home')
def index():
    return render_template('index.html', title='Home')

@main.route('/dashboard')
@login_required
def dashboard():
    try:
        if current_user.is_parent:
            return redirect(url_for('main.parent_dashboard'))
        elif current_user.is_teacher:
            return redirect(url_for('main.teacher_dashboard'))
        elif current_user.is_student:
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
@roles_required('is_parent')
def parent_dashboard():
    link_child_form = LinkParentForm()

    if link_child_form.validate_on_submit():
        try:
            child = User.query.filter_by(username=link_child_form.student_username.data, role='student').first()
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
    children = User.query.filter_by(parent_id=current_user.id, is_student=True).all()
    progress = {child.id: Progress.query.filter_by(student_id=child.id).all() for child in children}

    return render_template(
        'parent_dashboard.html',
        link_child_form=link_child_form,
        children=children,
        progress=progress
    )

@main.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('is_teacher')
def teacher_dashboard():
    course_form = CourseForm()
    assignment_form = AssignmentForm()
    progress_form = ProgressForm()
    attendance_form = AttendanceForm()
    user_form = UserForm()

    # Handle course creation
    if course_form.validate_on_submit() and 'create_course' in request.form:
        try:
            new_course = Course(course=course_form.course_name.data, description=course_form.description.data, teacher_id=current_user.id)
            db.session.add(new_course)
            db.session.commit()
            flash('Course created successfully.', 'success')
            return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the course.', 'danger')

    # Handle assignment creation
    if assignment_form.validate_on_submit() and 'create_assignment' in request.form:
        try:
            course = assignment_form.course_id.data
            if not course or course.teacher_id != current_user.id:
                flash('Invalid course selected.', 'danger')
            else:
                new_assignment = Assignment(
                    title=assignment_form.title.data,
                    description=assignment_form.description.data,
                    due_date=assignment_form.due_date.data,
                    course_id=course.id
                )
                db.session.add(new_assignment)
                db.session.commit()
                flash('Assignment created successfully.', 'success')
                return redirect(url_for('main.teacher_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the assignment.', 'danger')

    # Handle progress creation
    if progress_form.validate_on_submit() and 'create_progress' in request.form:
        student = User.query.filter_by(username=progress_form.student_name.data, role='student').first()
        course = progress_form.course_id.data
        if not student:
            flash('Student not found.', 'danger')
        else:
            try:
                new_progress = Progress(
                    student_id=student.id,
                    course_id=course.id,
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
    if user_form.validate_on_submit() and 'update_user' in request.form:
        user = User.query.get(user_form.id.data)
        if user:
            user.username = user_form.username.data
            user.email = user_form.email.data
            if user_form.password.data:
                user.set_password(user_form.password.data)
            user.is_parent = user_form.is_parent.data
            user.is_student = user_form.is_student.data
            user.role = 'teacher' if user.is_teacher else 'parent' if user.is_parent else 'student'
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
    users = User.query.filter(User.role.in_(['parent', 'student'])).all()

    return render_template(
        'teacher_dashboard.html',
        title='Teacher Dashboard',
        courses=courses,
        assignment_form=assignment_form,
        course_form=course_form,
        progress_form=progress_form,
        attendance_form=attendance_form,
        user_form=user_form,
        users=users
    )

@main.route('/student_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('is_student')
def student_dashboard():
    # Get all courses the student is enrolled in
    enrolled_courses = current_user.enrolled_courses

    # Fetch assignments for all enrolled courses
    assignments = Assignment.query.filter(Assignment.course_id.in_([course.id for course in enrolled_courses])).all()

    # Fetch progress reports for the student
    progress = Progress.query.filter_by(student_id=current_user.id).all()

    return render_template(
        'student_dashboard.html',
        title='Student Dashboard',
        enrolled_courses=enrolled_courses,
        assignments=assignments,
        progress=progress
    )


@main.route('/submit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@roles_required('is_student')
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    form = AssignmentSubmissionForm()

    if form.validate_on_submit():
        try:
            filename = save_assignment_file(form.submission_file.data) if form.submission_file.data else None
            new_submission = AssignmentSubmission(
                submission_content=form.submission_content.data,
                submission_file=filename,
                student_id=current_user.id,
                assignment_id=assignment.id
            )
            db.session.add(new_submission)
            db.session.commit()
            flash('Assignment submitted successfully.', 'success')
            return redirect(url_for('main.student_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while submitting the assignment.', 'danger')

    # Since this form is part of the student dashboard, I render the student_dashboard template directly
    enrolled_courses = current_user.enrolled_courses
    assignments = Assignment.query.filter(Assignment.course_id.in_([course.id for course in enrolled_courses])).all()
    progress = Progress.query.filter_by(student_id=current_user.id).all()

    return render_template(
        'student_dashboard.html',
        title='Student Dashboard',
        form=form,
        assignment=assignment,
        enrolled_courses=enrolled_courses,
        assignments=assignments,
        progress=progress
    )
