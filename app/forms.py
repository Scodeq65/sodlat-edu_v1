#!/usr/bin/python3
"""
Forms module for handling user input in the SodLat Edu Solution project.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Course
from pytz import utc
from datetime import datetime
from wtforms_sqlalchemy.fields import QuerySelectField


class LoginForm(FlaskForm):
    """Login form."""
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')])
    role = SelectField('Role', choices=[('parent', 'Parent'), ('teacher', 'Teacher'), ('student', 'Student')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Validate that the username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        """Validate that the email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')


class UserForm(FlaskForm):
    """Form for creating or updating users."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('parent', 'Parent'), ('teacher', 'Teacher'), ('student', 'Student')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        """Validate that the username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        """Validate that the email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')


class CourseForm(FlaskForm):
    """Form for creating or updating courses."""
    name = StringField('Course Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AssignmentForm(FlaskForm):
    """Form for creating or updating assignments."""
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    course_id = QuerySelectField('Course', query_factory=lambda: Course.query.all(), get_label='name', allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_due_date(self, due_date):
        """Validate that the due date is not in the past."""
        if due_date.data < datetime.utcnow().replace(tzinfo=utc):
            raise ValidationError('Due date cannot be in the past.')

class LinkParentForm(FlaskForm):
    """Form for linking a student to a parent."""
    student_username = StringField('Student Username', validators=[DataRequired()])
    student_email = StringField('Student Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Link Student')

    def validate_student_username(self, student_username):
        """Validate that the parent username exists."""
        student = User.query.filter_by(username=student_username.data).first()
        if not student:
            raise ValidationError('No matching student found')
        elif student.email != self.student_email.data:
            raise ValidationError('Student email does not match.')
        
    def validate_student_email(self, student_email):
        """Validate that the student email exists."""
        student = User.query.filter_by(email=student_email.data).first()
        if not student:
            raise ValidationError('No matching student found')
        elif student.username != self.student_username.data:
            raise ValidationError('Student username does not match.')


class ProgressForm(FlaskForm):
    """Form for tracking student progress."""
    student_name = StringField('Student Name', validators=[DataRequired()])
    teacher_name = StringField('Teacher Name', validators=[DataRequired()])
    grade = StringField('Grade', validators=[DataRequired()])
    attendance = StringField('Attendance')
    overall_performance = TextAreaField('Overall Performance')
    submit = SubmitField('Submit')

    def validate_student_name(self, student_name):
        """Validate that the student username exists."""
        student = User.query.filter_by(username=student_name.data).first()
        if not student:
            raise ValidationError('No matching student found.')
        
    def validate_teacher_name(self, teacher_name):
        """Validate that the teacher username exists."""
        teacher = User.query.filter_by(username=teacher_name.data).first()
        if not teacher:
            raise ValidationError('No matching teacher found.')