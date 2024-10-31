import unittest
from unittest.mock import patch
from backend.htmlextractor import get_html_text, HTMLTextExtractor


class TestHTMLTextExtractor(unittest.TestCase):
    """Tests the get_html_text function."""

    def test_extract_text_simple_html(self):
        """Tests the get_html_text function with simple HTML."""
        html = "<html><body>Hello, World!</body></html>"
        self.assertEqual(get_html_text(html), "Hello, World!")

    def test_extract_text_with_nested_tags(self):
        """Tests the get_html_text function with nested HTML tags."""
        html = "<html><body><p>This is <b>bold</b> text.</p></body></html>"
        self.assertEqual(get_html_text(html), "This is bold text.")

    def test_extract_text_with_multiple_body_tags(self):
        """Tests the get_html_text function with multiple body tags."""
        html = "<html><body>First body.</body><body>Second body.</body></html>"
        self.assertEqual(get_html_text(html), "First body.Second body.")

    def test_extract_text_no_body_tag(self):
        """Tests the get_html_text function with no body tag."""
        html = "<html><div>No body tag here.</div></html>"
        self.assertEqual(get_html_text(html), "No body tag here.")

    def test_extract_text_empty_html(self):
        """Tests the get_html_text function with empty HTML."""
        html = ""
        self.assertEqual(get_html_text(html), "")

    def test_get_text_whitespace(self):
        """Tests the get_html_text function with whitespace."""
        html = "<html><body>   Multiple    spaces </body></html>"
        self.assertEqual(get_html_text(html), "Multiple    spaces")

    @patch.object(HTMLTextExtractor, 'feed')
    def test_mock_feed_method(self, mock_feed):
        """Tests the mock feed method"""
        html = "<html><body>Test text</body></html>"
        get_html_text(html)
        mock_feed.assert_called_once()
