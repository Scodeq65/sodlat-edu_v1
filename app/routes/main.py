#!/usr/bin/python3
"""
Main route module for the SodLat Edu Solution project.
"""

import os
from flask import (
    Blueprint, render_template, url_for, flash, redirect, request
)
from flask_login import (
    current_user, login_required
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from functools import wraps
from app.db import db
from app.forms import (
    CourseForm, AssignmentForm, ProgressForm, UserForm, LinkParentForm, AttendanceForm
)
from app.models import User, Course, Assignment, Progress

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
    children = User.query.filter_by(parent_id=current_user.id, role='student').all()
    progress = {child.id: Progress.query.filter_by(student_id=child.id).all() for child in children}

    return render_template(
        'parent_dashboard.html',
        link_child_form=link_child_form,
        children=children,
        progress=progress
    )


# Teacher Dashboard: Creating assignments, courses, and recording progress
@main.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
@roles_required('teacher')
def teacher_dashboard():
    assignment_form = AssignmentForm()
    course_form = CourseForm()
    progress_form = ProgressForm()
    attendance_form = AttendanceForm()
    user_form = UserForm()

    # Fetch all students and their linked parents
    students = User.query.filter_by(role='student').all()
    parent_child_relationships = {
        student: User.query.get(student.parent_id) for student in students if student.parent_id
    }   

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

    # Handle attendance
    if attendance_form.submit.data and attendance_form.validate_on_submit():
        student = User.query.filter_by(username=attendance_form.student_name.data, role='student').first()
        if student:
            try:
                student.days_present += int(attendance_form.days_present.data)
                student.days_absent += int(attendance_form.days_absent.data)
                db.session.commit()
                flash(f"Attendance updated for {student.username}.", 'success')
            except SQLAlchemyError:
                db.session.rollback()
                flash('An error occurred while updating attendance.', 'danger')
            return redirect(url_for('main.teacher_dashboard'))

    # Handle user updates (either parent or student)
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


# Assignment submission route for students
@main.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
@login_required
@roles_required('student')
def submit_assignment(assignment_id):
    assignment_form = AssignmentSubmissionForm()

    if assignment_form.validate_on_submit():
        submission = AssignmentSubmission(
            student_id=current_user.id,
            assignment_id=assignment_id,
            submission_content=assignment_form.submission.data
        )
        if assignment_form.submission_file.data:
            file_name = save_assignment_file(assignment_form.submission_file.data)
            submission.submission_file = file_name
        
        db.session.add(submission)
        db.session.commit()
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('main.student_dashboard'))

    return redirect(url_for('main.student_dashboard'))