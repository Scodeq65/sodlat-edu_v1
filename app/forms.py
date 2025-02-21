#!/usr/bin/python3
"""
Forms module for handling user input in the SodLat Edu Solution project.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf.file import FileAllowed, FileField
from app.models import User, Course
from datetime import date
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
    is_teacher = BooleanField('Teacher')
    is_parent = BooleanField('Parent')
    is_student = BooleanField('Student')
    password = PasswordField('Password', validators=[])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        """Validate that the username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != self.user_id:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        """Validate that the email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')


class CourseForm(FlaskForm):
    """Form for creating or updating courses."""
    course = StringField('Course', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AssignmentForm(FlaskForm):
    """Form for creating or updating assignments."""
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d', validators=[DataRequired()], render_kw={"type": "date"})
    course_id = QuerySelectField('Course', query_factory=lambda: Course.query.all(), get_label='course', allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_due_date(self, due_date):
        """Validate that the due date is not in the past."""
        if due_date.data.date() < date.today():
            raise ValidationError('Due date cannot be in the past.')
        

class AssignmentSubmissionForm(FlaskForm):
    """Form for students to submit assignments."""
    submission_content = TextAreaField('Submit your work', validators=[DataRequired()])
    submission_file = FileField('Upload File', validators=[
        FileAllowed(['pdf', 'doc', 'docx'], 'PDF or Word documents only!')
    ])
    submit = SubmitField('Submit')

class LinkParentForm(FlaskForm):
    """Form for linking a student to a parent."""
    student_username = StringField('Student Username', validators=[DataRequired()])
    submit = SubmitField('Link Student')

    def validate_student_username(self, student_username):
        """Validate that the parent username exists."""
        student = User.query.filter_by(username=student_username.data).first()
        if not student:
            raise ValidationError('No matching student found')


class ProgressForm(FlaskForm):
    """Form for tracking student progress."""
    student_name = StringField('Student Name', validators=[DataRequired()])
    course_id = QuerySelectField('Course', query_factory=lambda: Course.query.all(), get_label='course', validators=[DataRequired()])
    grade = StringField('Grade', validators=[DataRequired()])
    days_present = IntegerField('Days Present', validators=[DataRequired()])
    days_absent = IntegerField('Days Absent', validators=[DataRequired()])
    overall_performance = TextAreaField('Overall Performance')
    submit = SubmitField('Submit')

    def validate_student_name(self, student_name):
        """Validate that the student username exists."""
        student = User.query.filter_by(username=student_name.data).first()
        if not student:
            raise ValidationError('No matching student found.')

    def validate_days_present(self, days_present):
        """Ensure attendance values are logical."""
        if self.days_absent.data < 0 or self.days_present.data < 0:
            raise ValidationError('Attendance values must be positive.')
        

class AttendanceForm(FlaskForm):
    #Form for recording student attendance.
    student_name = StringField('Student Name', validators=[DataRequired()])
    course_id = QuerySelectField('Course', query_factory=lambda: Course.query.all(), get_label='course', validators=[DataRequired()])
    days_present = IntegerField('Days Present', validators=[DataRequired()])
    days_absent = IntegerField('Days Absent', validators=[DataRequired()])
    submit = SubmitField('Submit Attendance')

    def validate_student_name(self, student_name):
        #Validate that the student username exists.
        student = User.query.filter_by(username=student_name.data).first()
        if not student:
            raise ValidationError('No matching student found.')
