#!/usr/bin/python3
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.routes import bp
from app.forms import CourseForm, AssignmentForm, ProgressForm, UserForm
from app.models import Course, Assignment, User, Progress
from app import db

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

@bp.route('/parent_dashboard', methods=['GET', 'POST'])
@login_required
def parent_dashboard():
    """Parent dashboard with functionalities."""
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        teacher_name = request.form.get('teacher_name')
        student = User.query.filter_by(username=student_name).first()
        teacher = User.query.filter_by(username=teacher_name).first()

        if student and teacher:
            # Link the student to the parent
            if student.parent_id is None:
                student.parent_id = current_user.id
                db.session.commit()
                flash('Child added successfully.', 'success')
            else:
                flash('Child is already linked to another parent.', 'warning')
        else:
            flash('Invalid student or teacher name.', 'danger')

    # Query to get the children’s progress
    children_progress = Progress.query.filter_by(student_id=current_user.id).all()
    
    return render_template('parent_dashboard.html', title='Parent Dashboard', progress=children_progress)

@bp.route('/teacher_dashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    """Teacher dashboard with functionalities."""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully.', 'success')
            else:
                flash('User not found.', 'danger')

        elif action == 'update':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            if user:
                user.username = request.form.get('username', user.username)
                user.email = request.form.get('email', user.email)
                user.role = request.form.get('role', user.role)
                db.session.commit()
                flash('User updated successfully.', 'success')
            else:
                flash('User not found.', 'danger')

        elif action == 'create':
            new_user = User(
                username=request.form.get('username'),
                email=request.form.get('email'),
                role=request.form.get('role')
            )
            new_user.set_password(request.form.get('password'))
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully.', 'success')

    # Query to get the list of users
    users = User.query.all()
    
    return render_template('teacher_dashboard.html', title='Teacher Dashboard', users=users)

@bp.route('/student_dashboard', methods=['GET', 'POST'])
@login_required
def student_dashboard():
    """Student dashboard with functionalities."""
    if request.method == 'POST':
        parent_name = request.form.get('parent_name')
        parent_email = request.form.get('parent_email')
        
        parent = User.query.filter_by(username=parent_name, email=parent_email).first()
        
        if parent:
            # Link the parent to the student
            if current_user.parent_id is None:
                current_user.parent_id = parent.id
                db.session.commit()
                flash('Parent added successfully.', 'success')
            else:
                flash('Student already has a parent linked.', 'warning')
        else:
            flash('Invalid parent details.', 'danger')
    
    return render_template('student_dashboard.html', title='Student Dashboard')