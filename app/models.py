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


