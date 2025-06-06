import unittest
from tests.base import BaseTestCase
from app import app, db, User, GoLink


class TestAdminFunctionality(BaseTestCase):
    """Test admin-specific functionality."""
    
    def test_admin_can_view_users(self):
        """Test that admin can access user management."""
        self.create_user(is_admin=True)
        self.login()
        
        rv = self.app.get('/users')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Users', rv.data)
    
    def test_non_admin_cannot_view_users(self):
        """Test that non-admin cannot access user management."""
        self.create_user(is_admin=False)
        self.login()
        
        rv = self.app.get('/users', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Admin access required', rv.data)
    
    def test_admin_can_create_user(self):
        """Test that admin can create users."""
        self.create_user(is_admin=True)
        self.login()
        
        rv = self.app.post('/users', data={
            'username': 'newuser',
            'password': 'newpass'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'User created successfully', rv.data)
        
        with app.app_context():
            new_user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(new_user)
            self.assertFalse(new_user.is_admin)
    
    def test_admin_can_create_admin_user(self):
        """Test that admin can create other admin users."""
        self.create_user(is_admin=True)
        self.login()
        
        rv = self.app.post('/users', data={
            'username': 'newadmin',
            'password': 'adminpass',
            'is_admin': 'on'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'User created successfully', rv.data)
        
        with app.app_context():
            new_admin = User.query.filter_by(username='newadmin').first()
            self.assertIsNotNone(new_admin)
            self.assertTrue(new_admin.is_admin)
    
    def test_admin_cannot_create_duplicate_user(self):
        """Test that admin cannot create users with duplicate usernames."""
        self.create_user("existing", is_admin=True)
        self.login("existing", "testpass")
        
        rv = self.app.post('/users', data={
            'username': 'existing',
            'password': 'newpass'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Username already exists', rv.data)
    
    def test_non_admin_cannot_create_user(self):
        """Test that non-admin cannot create users."""
        self.create_user(is_admin=False)
        self.login()
        
        rv = self.app.post('/users', data={
            'username': 'newuser',
            'password': 'newpass'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Admin access required', rv.data)
    
    def test_admin_can_edit_any_link(self):
        """Test that admin can edit any user's link."""
        admin = self.create_user("admin", is_admin=True)
        owner = self.create_user("owner")
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=owner.id)
            db.session.add(link)
            db.session.commit()
        
        self.login("admin", "testpass")
        rv = self.app.post('/edit/test', data={
            'target_url': 'https://admin-updated.com'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Link updated successfully', rv.data)
        
        with app.app_context():
            updated_link = GoLink.query.filter_by(short_path='test').first()
            self.assertEqual(updated_link.target_url, 'https://admin-updated.com')
    
    def test_admin_can_delete_any_link(self):
        """Test that admin can delete any user's link."""
        admin = self.create_user("admin", is_admin=True)
        owner = self.create_user("owner")
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=owner.id)
            db.session.add(link)
            db.session.commit()
        
        self.login("admin", "testpass")
        rv = self.app.post('/links/test/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Link deleted successfully', rv.data)
        
        with app.app_context():
            deleted_link = GoLink.query.filter_by(short_path='test').first()
            self.assertIsNone(deleted_link)
    
    def test_admin_can_toggle_user_admin_status(self):
        """Test that admin can promote/demote users."""
        admin = self.create_user("admin", is_admin=True)
        regular_user = self.create_user("regular")
        
        self.login("admin", "testpass")
        rv = self.app.post(f'/users/{regular_user.id}/toggle-admin', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'promoted to admin', rv.data)
        
        with app.app_context():
            updated_user = User.query.get(regular_user.id)
            self.assertTrue(updated_user.is_admin)
        
        # Test demotion
        rv = self.app.post(f'/users/{regular_user.id}/toggle-admin', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'demoted from admin', rv.data)
        
        with app.app_context():
            updated_user = User.query.get(regular_user.id)
            self.assertFalse(updated_user.is_admin)
    
    def test_admin_can_delete_user(self):
        """Test that admin can delete other users."""
        admin = self.create_user("admin", is_admin=True)
        target_user = self.create_user("target")
        
        self.login("admin", "testpass")
        rv = self.app.post(f'/users/{target_user.id}/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'User deleted successfully', rv.data)
        
        with app.app_context():
            deleted_user = User.query.get(target_user.id)
            self.assertIsNone(deleted_user)
    
    def test_admin_cannot_delete_self(self):
        """Test that admin cannot delete their own account."""
        admin = self.create_user("admin", is_admin=True)
        self.login("admin", "testpass")
        
        rv = self.app.post(f'/users/{admin.id}/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'You cannot delete your own account', rv.data)
        
        with app.app_context():
            existing_admin = User.query.get(admin.id)
            self.assertIsNotNone(existing_admin)
    
    def test_admin_cannot_modify_own_admin_status(self):
        """Test that admin cannot modify their own admin status."""
        admin = self.create_user("admin", is_admin=True)
        self.login("admin", "testpass")
        
        rv = self.app.post(f'/users/{admin.id}/toggle-admin', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'You cannot modify your own admin status', rv.data)
        
        with app.app_context():
            unchanged_admin = User.query.get(admin.id)
            self.assertTrue(unchanged_admin.is_admin)
    
    def test_non_admin_cannot_access_admin_routes(self):
        """Test that non-admin users cannot access admin routes."""
        regular_user = self.create_user("regular", is_admin=False)
        target_user = self.create_user("target")
        
        self.login("regular", "testpass")
        
        # Test all admin routes
        admin_routes = [
            f'/users/{target_user.id}/delete',
            f'/users/{target_user.id}/toggle-admin'
        ]
        
        for route in admin_routes:
            with self.subTest(route=route):
                rv = self.app.post(route, follow_redirects=True)
                self.assertEqual(rv.status_code, 200)
                self.assertIn(b'Admin access required', rv.data)
    
    def test_users_pagination(self):
        """Test users page pagination."""
        admin = self.create_user("admin", is_admin=True)
        
        # Create more than 10 users to test pagination
        with app.app_context():
            for i in range(15):
                user = User(
                    username=f'user{i}',
                    password_hash='dummy_hash',
                    is_admin=False
                )
                db.session.add(user)
            db.session.commit()
        
        self.login("admin", "testpass")
        rv = self.app.get('/users')
        self.assertEqual(rv.status_code, 200)
        # Should show pagination controls when more than 10 items
        self.assertIn(b'Next', rv.data)


if __name__ == '__main__':
    unittest.main()