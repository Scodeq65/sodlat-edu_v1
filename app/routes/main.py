from flask import render_template, redirect, url_for, flash
from app.routes import bp
from flask_login import login_required, current_user
from app.forms import CourseForm, AssignmentForm
from app.models import Course, Assignment, db

@bp.route('/')
@bp.route('/index')
def index():
    """Homepage route."""
    return render_template('index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route."""
    if current_user.role == 'parent':
        return redirect(url_for('main.parent_dashboard'))
    elif current_user.role == 'teacher':
        return redirect(url_for('main.teacher_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('main.student_dashboard'))
    else:
        flash('Unauthorized access.')
        return redirect(url_for('main.index'))

@bp.route('/parent_dashboard')
@login_required
def parent_dashboard():
    """Parent dashboard."""
    # Code to handle parent-specific tasks
    return render_template('parent_dashboard.html', title='Parent Dashboard')

@bp.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    """Teacher dashboard."""
    # Code to handle teacher-specific tasks
    return render_template('teacher_dashboard.html', title='Teacher Dashboard')

@bp.route('/student_dashboard')
@login_required
def student_dashboard():
    """Student dashboard."""
    # Code to handle student-specific tasks
    return render_template('student_dashboard.html', title='Student Dashboard')