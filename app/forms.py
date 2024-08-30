from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

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
    role = SelectField('Role', choices=[('parent', 'Parent'), ('teacher', 'Teacher'), ('student', 'Student')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered.')

class CourseForm(FlaskForm):
    """Form for creating or updating a course."""
    name = StringField('Course Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AssignmentForm(FlaskForm):
    """Form for creating or updating an assignment."""
    title = StringField('Assignment Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    due_date = StringField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Submit')