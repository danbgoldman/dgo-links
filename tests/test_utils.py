import unittest
from app import is_valid_url


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_is_valid_url_valid_cases(self):
        """Test is_valid_url with valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://sub.example.com/path",
            "http://localhost:8080",
            "https://example.com:443/path?query=value",
            "http://192.168.1.1",
            "https://example.com/path/to/resource.html",
            "http://example.com:3000/api/v1/endpoint"
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_valid_url(url), f"URL should be valid: {url}")
    
    def test_is_valid_url_invalid_cases(self):
        """Test is_valid_url with invalid URLs."""
        invalid_urls = [
            "example.com",                    # Missing scheme
            "javascript:alert('xss')",       # Dangerous scheme
            "",                              # Empty string
            "not_a_url",                     # Plain text
            "://example.com",                # Missing scheme name
            "http://",                       # Missing netloc
            "https://",                      # Missing netloc
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_valid_url(url), f"URL should be invalid: {url}")
    
    def test_is_valid_url_edge_cases(self):
        """Test is_valid_url with edge cases."""
        edge_cases = [
            ("http://localhost", True),       # Localhost without port
            ("https://127.0.0.1", True),     # IP address
            ("http://[::1]", True),          # IPv6
            ("https://example.com.", True),   # Trailing dot
            ("http://sub.sub.example.com", True),  # Multiple subdomains
        ]
        
        for url, expected in edge_cases:
            with self.subTest(url=url):
                result = is_valid_url(url)
                self.assertEqual(result, expected, f"URL {url} should be {'valid' if expected else 'invalid'}")
    
    def test_is_valid_url_exception_handling(self):
        """Test that is_valid_url handles exceptions gracefully."""
        # Test with None (should not crash)
        try:
            result = is_valid_url(None)
            self.assertFalse(result)
        except:
            self.fail("is_valid_url should handle None gracefully")
        
        # Test with non-string input (should not crash)
        try:
            result = is_valid_url(123)
            self.assertFalse(result)
        except:
            self.fail("is_valid_url should handle non-string input gracefully")


if __name__ == '__main__':
    unittest.main()