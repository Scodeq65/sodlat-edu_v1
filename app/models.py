#!/usr/bin/python3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.db import db

class User(UserMixin, db.Model):
    """Model for users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), nullable=False)

    # Parent-Child relationship
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    children = db.relationship('User', backref='parent', remote_side=[id])

    # Attendance tracking
    days_present = db.Column(db.Integer, default=0)
    days_absent = db.Column(db.Integer, default=0)

    # Teacher-related relationships
    courses = db.relationship('Course', backref='teacher', lazy=True)
    progress_reports = db.relationship('Progress', foreign_keys='Progress.teacher_id', backref='instructor', lazy=True)

    # Student-related relationships
    assignments = db.relationship('Assignment', backref='student', lazy=True)
    progress_records = db.relationship('Progress', foreign_keys='Progress.student_id', backref='student_progress', lazy=True)
    assignment_submissions = db.relationship('AssignmentSubmission', backref='student', lazy=True)

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    """Model for courses."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignments = db.relationship('Assignment', backref='course', lazy=True)


class Assignment(db.Model):
    """Model for assignments."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy=True)


class AssignmentSubmission(db.Model):
    """Model for assignment submissions."""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    submission_content = db.Column(db.Text, nullable=False)
    submission_file = db.Column(db.String(150))


class Progress(db.Model):
    """Model for tracking student progress."""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    days_present = db.Column(db.Integer, nullable=False, default=0)
    days_absent = db.Column(db.Integer, nullable=False, default=0)
    overall_performance = db.Column(db.String(100), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    student = db.relationship('User', foreign_keys=[student_id], backref='student_progress_records')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='teacher_progress_reports')
