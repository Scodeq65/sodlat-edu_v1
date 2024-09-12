#!/usr/bin/python3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import validates
from app.db import db
from wtforms.validators import ValidationError


class User(UserMixin, db.Model):
    """Model for users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Role management (is_teacher, is_parent, is_student)
    is_teacher = db.Column(db.Boolean, default=False)
    is_parent = db.Column(db.Boolean, default=False)
    is_student = db.Column(db.Boolean, default=False)

    # Parent-Child relationship with circular relationship validation
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    children = db.relationship('User', backref='parent', remote_side=[id], cascade="all, delete", lazy='dynamic')

    # Attendance tracking
    days_present = db.Column(db.Integer, default=0)
    days_absent = db.Column(db.Integer, default=0)


    # Student-related relationships
    assignments = db.relationship('AssignmentSubmission', backref='student', lazy='dynamic')
    progress_records = db.relationship('Progress', foreign_keys='Progress.student_id', backref='student', lazy='dynamic')

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    @validates('parent_id')
    def validate_parent_id(self, key, parent_id):
        """Validate that there is no circular parent-child relationship."""
        if parent_id == self.id:
            raise ValidationError("A user cannot be their own parent.")
        
        parent = User.query.get(parent_id)
        while parent:
            if parent.id == self.id:
                raise ValidationError("Circular parent-child relationship detected.")
            parent = parent.parent
        return parent_id


class Course(db.Model):
    """Model for courses."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic', cascade="all, delete")


class Assignment(db.Model):
    """Model for assignments."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), index=True, nullable=False)

    # Many-to-many relationship via AssignmentSubmission table
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic', cascade="all, delete")


class AssignmentSubmission(db.Model):
    """Model for assignment submissions."""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), index=True, nullable=False)
    submission_content = db.Column(db.Text, nullable=False)
    submission_file = db.Column(db.String(150))


class Progress(db.Model):
    """Model for tracking student progress."""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), index=True, nullable=False)

    # Nullable fields for incomplete data.
    grade = db.Column(db.String(10), nullable=True)
    days_present = db.Column(db.Integer, nullable=True, default=0)
    days_absent = db.Column(db.Integer, nullable=True, default=0)
    overall_performance = db.Column(db.String(100), nullable=True)

    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)

    student = db.relationship('User', foreign_keys=[student_id], backref='progress_records', lazy='dynamic')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='progress_reports', lazy='dynamic')
