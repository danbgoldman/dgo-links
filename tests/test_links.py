import unittest
from tests.base import BaseTestCase
from app import app, db, GoLink


class TestLinkManagement(BaseTestCase):
    """Test link creation, editing, and deletion."""
    
    def test_create_link_requires_login(self):
        """Test that creating links requires authentication."""
        rv = self.app.get('/create')
        self.assertEqual(rv.status_code, 302)  # Redirect to login
    
    def test_create_link_page_loads(self):
        """Test create link page loads for authenticated user."""
        self.create_user()
        self.login()
        rv = self.app.get('/create')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Create', rv.data)
    
    def test_create_link_success(self):
        """Test successful link creation."""
        self.create_user()
        self.login()
        
        rv = self.app.post('/create', data={
            'short_path': 'test',
            'target_url': 'https://example.com'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Link created successfully', rv.data)
        
        with app.app_context():
            link = GoLink.query.filter_by(short_path='test').first()
            self.assertIsNotNone(link)
            self.assertEqual(link.target_url, 'https://example.com')
    
    def test_create_link_invalid_url(self):
        """Test link creation with invalid URL."""
        self.create_user()
        self.login()
        
        rv = self.app.post('/create', data={
            'short_path': 'test',
            'target_url': 'invalid_url'
        })
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Please enter a valid URL', rv.data)
    
    def test_create_link_duplicate_path(self):
        """Test link creation with duplicate short path."""
        user = self.create_user()
        self.login()
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=user.id)
            db.session.add(link)
            db.session.commit()
        
        rv = self.app.post('/create', data={
            'short_path': 'test',
            'target_url': 'https://another.com'
        })
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'This short path is already taken', rv.data)
    
    def test_create_link_missing_fields(self):
        """Test link creation with missing required fields."""
        self.create_user()
        self.login()
        
        rv = self.app.post('/create', data={
            'short_path': '',
            'target_url': 'https://example.com'
        })
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Both short path and target URL are required', rv.data)
    
    def test_redirect_to_target_url(self):
        """Test that short links redirect to target URLs."""
        user = self.create_user()
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=user.id)
            db.session.add(link)
            db.session.commit()
        
        rv = self.app.get('/test')
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 'https://example.com')
    
    def test_redirect_nonexistent_link_to_create(self):
        """Test that nonexistent links redirect to create page."""
        rv = self.app.get('/nonexistent')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/create', rv.location)
        self.assertIn('shortlink=nonexistent', rv.location)
    
    def test_edit_own_link(self):
        """Test editing own link."""
        user = self.create_user()
        self.login()
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=user.id)
            db.session.add(link)
            db.session.commit()
        
        rv = self.app.post('/edit/test', data={
            'target_url': 'https://updated.com'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Link updated successfully', rv.data)
        
        with app.app_context():
            updated_link = GoLink.query.filter_by(short_path='test').first()
            self.assertEqual(updated_link.target_url, 'https://updated.com')
    
    def test_cannot_edit_others_link(self):
        """Test that users cannot edit others' links."""
        owner = self.create_user("owner")
        other_user = self.create_user("other")
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=owner.id)
            db.session.add(link)
            db.session.commit()
        
        self.login("other", "testpass")
        rv = self.app.post('/edit/test', data={
            'target_url': 'https://malicious.com'
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'You can only edit your own links', rv.data)
    
    def test_edit_nonexistent_link(self):
        """Test editing nonexistent link."""
        self.create_user()
        self.login()
        
        rv = self.app.get('/edit/nonexistent', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Link not found', rv.data)
    
    def test_delete_own_link(self):
        """Test deleting own link."""
        user = self.create_user()
        self.login()
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=user.id)
            db.session.add(link)
            db.session.commit()
        
        rv = self.app.post('/links/test/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Link deleted successfully', rv.data)
        
        with app.app_context():
            deleted_link = GoLink.query.filter_by(short_path='test').first()
            self.assertIsNone(deleted_link)
    
    def test_cannot_delete_others_link(self):
        """Test that users cannot delete others' links."""
        owner = self.create_user("owner")
        other_user = self.create_user("other")
        
        with app.app_context():
            link = GoLink(short_path='test', target_url='https://example.com', user_id=owner.id)
            db.session.add(link)
            db.session.commit()
        
        self.login("other", "testpass")
        rv = self.app.post('/links/test/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'You can only delete your own links', rv.data)
    
    def test_delete_nonexistent_link(self):
        """Test deleting nonexistent link."""
        self.create_user()
        self.login()
        
        rv = self.app.post('/links/nonexistent/delete', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Link not found', rv.data)
    
    def test_links_page_requires_auth(self):
        """Test links page requires authentication."""
        rv = self.app.get('/links')
        self.assertEqual(rv.status_code, 302)
        self.assertIn('/login', rv.location)
    
    def test_links_page_loads_for_authenticated(self):
        """Test links page loads for authenticated users."""
        self.create_user()
        self.login()
        rv = self.app.get('/links')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Links', rv.data)
    
    def test_links_pagination(self):
        """Test links pagination."""
        user = self.create_user()
        self.login()
        
        # Create more than 10 links to test pagination
        with app.app_context():
            for i in range(15):
                link = GoLink(short_path=f'test{i}', target_url=f'https://example{i}.com', user_id=user.id)
                db.session.add(link)
            db.session.commit()
        
        rv = self.app.get('/links')
        self.assertEqual(rv.status_code, 200)
        # Should show pagination controls when more than 10 items
        self.assertIn(b'Next', rv.data)


if __name__ == '__main__':
    unittest.main()