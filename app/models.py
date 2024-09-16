#!/usr/bin/python3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.db import db


# Association table for many-to-many relationship between students and courses
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    role = db.Column(db.String(50), nullable=False)

    
    # Relationships
    parent = db.relationship('User', back_populates='children', remote_side=[id])
    children = db.relationship('User', back_populates='parent', cascade="all, delete", remote_side=[parent_id])
    
    # Courses a student is enrolled in (many-to-many)
    enrolled_courses = db.relationship('Course', secondary=student_courses, backref='students')

    # Courses created by a teacher (one-to-many)
    created_courses = db.relationship('Course', backref='teacher', lazy=True)
    
    # Roles flag
    is_teacher = db.Column(db.Boolean, default=False)
    is_parent = db.Column(db.Boolean, default=False)
    is_student = db.Column(db.Boolean, default=False)
    
    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def validate_parent_id(self, parent_id):
        """Prevents circular parent-child relationships."""
        if parent_id is None:
            return parent_id
        parent = User.query.get(parent_id)
        while parent:
            if parent.id == self.id:
                raise ValueError("Circular parent-child relationship detected.")
            parent = parent.parent
        return parent_id

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    teacher = db.relationship('User', backref='courses', foreign_keys=[teacher_id])
    assignments = db.relationship('Assignment', back_populates='course', cascade="all, delete")

    def __repr__(self):
        return f"Course('{self.title}')"


class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Relationships
    course = db.relationship('Course', back_populates='assignments')
    submissions = db.relationship('AssignmentSubmission', back_populates='assignment', cascade="all, delete")

    def __repr__(self):
        return f"Assignment('{self.title}')"


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submission'
    id = db.Column(db.Integer, primary_key=True)
    submission_file = db.Column(db.String(200), nullable=True)  # File path or URL
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    
    # Relationships
    student = db.relationship('User', backref='assignment_submissions', foreign_keys=[student_id])
    assignment = db.relationship('Assignment', back_populates='submissions')

    def __repr__(self):
        return f"AssignmentSubmission('{self.student_id}', '{self.assignment_id}')"


class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grade = db.Column(db.String(10), nullable=True)
    days_present = db.Column(db.Integer, nullable=True)
    days_absent = db.Column(db.Integer, nullable=True)
    overall_performance = db.Column(db.Text, nullable=True)

    # Relationships
    student = db.relationship('User', backref='progress_reports', foreign_keys=[student_id])
    course = db.relationship('Course', back_populate='progress')
    teacher = db.relationship('User', backref='teacher_progress', foreign_keys=[teacher_id])

    def __repr__(self):
        return f"Progress('{self.student_id}', '{self.course_id}')"