import unittest
from flask import url_for
from app import create_app, db
from app.models import User

class RoutesTestCase(unittest.TestCase):
    """Tests for the routes."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """Tear down test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page(self):
        """Test if the index page loads correctly."""
        response = self.client.get(url_for('main.index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to SodLat Edu Solution', response.data)

    def test_login(self):
        """Test the login process."""
        user = User(username='testuser', email='test@example.com', role='student')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        response = self.client.post(url_for('main.login'), data={
            'username_or_email': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, testuser!', response.data)

    def test_registration(self):
        """Test the registration process."""
        response = self.client.post(url_for('main.register'), data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password',
            'confirm_password': 'password',
            'role': 'student'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been registered', response.data)

    def test_logout(self):
        """Test the logout process."""
        user = User(username='testuser', email='test@example.com', role='student')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        self.client.post(url_for('main.login'), data={
            'username_or_email': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        response = self.client.get(url_for('main.logout'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out.', response.data)

    def test_dashboard_access(self):
        """Test access to dashboards based on user roles."""
        parent = User(username='parentuser', email='parent@example.com', role='parent')
        parent.set_password('password')
        db.session.add(parent)
        db.session.commit()

        teacher = User(username='teacheruser', email='teacher@example.com', role='teacher')
        teacher.set_password('password')
        db.session.add(teacher)
        db.session.commit()

        student = User(username='studentuser', email='student@example.com', role='student')
        student.set_password('password')
        db.session.add(student)
        db.session.commit()

        # Test parent dashboard access
        self.client.post(url_for('main.login'), data={
            'username_or_email': 'parentuser',
            'password': 'password'
        }, follow_redirects=True)
        response = self.client.get(url_for('main.parent_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Parent Dashboard', response.data)

        # Test teacher dashboard access
        self.client.post(url_for('main.logout'))
        self.client.post(url_for('main.login'), data={
            'username_or_email': 'teacheruser',
            'password': 'password'
        }, follow_redirects=True)
        response = self.client.get(url_for('main.teacher_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Teacher Dashboard', response.data)

        # Test student dashboard access
        self.client.post(url_for('main.logout'))
        self.client.post(url_for('main.login'), data={
            'username_or_email': 'studentuser',
            'password': 'password'
        }, follow_redirects=True)
        response = self.client.get(url_for('main.student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Dashboard', response.data)