import unittest
from app import create_app, db
from app.models import User, Course, Assignment

class ModelTestCase(unittest.TestCase):
    """Tests for the models."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Tear down test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test user creation."""
        user = User(username='testuser', email='test@example.com', role='student')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.check_password('password'))

    def test_course_creation(self):
        """Test course creation."""
        teacher = User(username='teacher', email='teacher@example.com', role='teacher')
        db.session.add(teacher)
        db.session.commit()
        course = Course(name='Math', teacher=teacher)
        db.session.add(course)
        db.session.commit()
        self.assertEqual(course.teacher.username, 'teacher')

    def test_assignment_creation(self):
        """Test assignment creation."""
        student = User(username='student', email='student@example.com', role='student')
        teacher = User(username='teacher', email='teacher@example.com', role='teacher')
        db.session.add(student)
        db.session.add(teacher)
        db.session.commit()
        course = Course(name='Math', teacher=teacher)
        db.session.add(course)
        db.session.commit()
        assignment = Assignment(title='Homework', content='Solve problems', course=course, student=student)
        db.session.add(assignment)
        db.session.commit()
        self.assertEqual(assignment.course.name, 'Math')
        self.assertEqual(assignment.student.username, 'student')