import unittest
from tests.base import BaseTestCase
from app import app, db, User, GoLink
from werkzeug.security import generate_password_hash


class TestModels(BaseTestCase):
    """Test database models."""
    
    def test_user_creation(self):
        """Test user creation and attributes."""
        user = self.create_user()
        with app.app_context():
            saved_user = User.query.filter_by(username="testuser").first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.username, "testuser")
            self.assertFalse(saved_user.is_admin)
    
    def test_admin_user_creation(self):
        """Test admin user creation."""
        user = self.create_user(is_admin=True)
        with app.app_context():
            saved_user = User.query.filter_by(username="testuser").first()
            self.assertTrue(saved_user.is_admin)
    
    def test_golink_creation(self):
        """Test GoLink creation and relationships."""
        with app.app_context():
            user = User(
                username="testuser",
                password_hash=generate_password_hash("testpass"),
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            
            link = GoLink(
                short_path="test",
                target_url="https://example.com",
                user_id=user.id
            )
            db.session.add(link)
            db.session.commit()
            
            saved_link = GoLink.query.filter_by(short_path="test").first()
            self.assertIsNotNone(saved_link)
            self.assertEqual(saved_link.target_url, "https://example.com")
            self.assertEqual(saved_link.user_id, user.id)
            self.assertEqual(saved_link.creator.username, "testuser")
    
    def test_user_link_relationship(self):
        """Test User-GoLink relationship."""
        with app.app_context():
            user = User(
                username="testuser",
                password_hash=generate_password_hash("testpass"),
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            
            link1 = GoLink(short_path="test1", target_url="https://example1.com", user_id=user.id)
            link2 = GoLink(short_path="test2", target_url="https://example2.com", user_id=user.id)
            db.session.add(link1)
            db.session.add(link2)
            db.session.commit()
            
            saved_user = User.query.filter_by(username="testuser").first()
            self.assertEqual(len(saved_user.links), 2)
            link_paths = [link.short_path for link in saved_user.links]
            self.assertIn("test1", link_paths)
            self.assertIn("test2", link_paths)


if __name__ == '__main__':
    unittest.main()