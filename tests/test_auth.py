import unittest
from tests.base import BaseTestCase
from app import app, User


class TestAuthentication(BaseTestCase):
    """Test authentication routes."""
    
    def test_login_page_loads(self):
        """Test login page loads correctly."""
        rv = self.app.get('/login')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Login', rv.data)
    
    def test_register_page_loads(self):
        """Test register page loads correctly."""
        rv = self.app.get('/register')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Register', rv.data)
    
    def test_first_user_becomes_admin(self):
        """Test that first registered user becomes admin."""
        rv = self.app.post('/register', data={
            'username': 'firstuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        
        with app.app_context():
            user = User.query.filter_by(username='firstuser').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.is_admin)
    
    def test_second_user_not_admin(self):
        """Test that second user is not admin."""
        self.create_user("firstuser", is_admin=True)
        
        rv = self.app.post('/register', data={
            'username': 'seconduser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        
        with app.app_context():
            user = User.query.filter_by(username='seconduser').first()
            self.assertIsNotNone(user)
            self.assertFalse(user.is_admin)
    
    def test_login_success(self):
        """Test successful login."""
        self.create_user()
        rv = self.login()
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Links', rv.data)
    
    def test_login_failure(self):
        """Test failed login with wrong credentials."""
        self.create_user()
        rv = self.login(password="wrongpass")
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Invalid username or password', rv.data)
    
    def test_logout(self):
        """Test logout functionality."""
        self.create_user()
        self.login()
        rv = self.logout()
        self.assertEqual(rv.status_code, 200)
    
    def test_duplicate_username_registration(self):
        """Test that duplicate usernames are rejected."""
        self.create_user("duplicate")
        
        rv = self.app.post('/register', data={
            'username': 'duplicate',
            'password': 'newpass'
        })
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Username already exists', rv.data)
    
    def test_index_redirects_unauthenticated(self):
        """Test index redirects to login for unauthenticated users."""
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/login', rv.location)
    
    def test_index_redirects_authenticated(self):
        """Test index redirects to links for authenticated users."""
        self.create_user()
        self.login()
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/links', rv.location)
    
    def test_authenticated_user_cannot_access_login(self):
        """Test that authenticated users are redirected from login page."""
        self.create_user()
        self.login()
        rv = self.app.get('/login')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/links', rv.location)


if __name__ == '__main__':
    unittest.main()