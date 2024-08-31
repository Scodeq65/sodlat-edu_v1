from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Course, Assignment
from datetime import datetime
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class LoginForm(FlaskForm):
    """Login form."""
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('parent', 'Parent'), ('teacher', 'Teacher'), ('student', 'Student')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')

class UserForm(FlaskForm):
    """Form for creating or updating users."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('parent', 'Parent'), ('teacher', 'Teacher'), ('student', 'Student')], validators=[DataRequired()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
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
        if due_date.data < datetime.utcnow():
            raise ValidationError('Due date cannot be in the past.')

class LinkParentForm(FlaskForm):
    """Form for linking a student to a parent."""
    parent_name = StringField('Parent Username', validators=[DataRequired()])
    parent_email = StringField('Parent Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Link Parent')

    def validate_parent_name(self, parent_name):
        parent = User.query.filter_by(username=parent_name.data).first()
        if not parent:
            raise ValidationError('No matching parent found.')

    def validate_parent_email(self, parent_email):
        parent = User.query.filter_by(email=parent_email.data).first()
        if not parent:
            raise ValidationError('No matching parent found.')

class ProgressForm(FlaskForm):
    """Form for tracking student progress."""
    student_name = StringField('Student Name', validators=[DataRequired()])
    teacher_name = StringField('Teacher Name', validators=[DataRequired()])
    grade = IntegerField('Grade', validators=[DataRequired()])
    attendance = IntegerField('Attendance')
    overall_performance = TextAreaField('Overall Performance')
    submit = SubmitField('Submit')

    def validate_student_name(self, student_name):
        student = User.query.filter_by(username=student_name.data).first()
        if not student:
            raise ValidationError('No matching student found.')