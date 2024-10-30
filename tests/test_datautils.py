import unittest

from backend.datautils import flatten_dict


class TestDataUtils(unittest.TestCase):
    """Testing the datautils module."""

    def test_flatten_dict(self):
        """Tests the flatten_dict function."""
        # Sample nested dictionary
        nested_data = {
            "name": "John Doe",
            "contact": {
                "email": "johndoe@example.com",
                "phone": "123-456-7890"
            },
            "employment": {
                "company": "OpenAI",
                "position": "Engineer",
                "projects": [
                    {"name": "Project Alpha", "status": "completed"},
                    {"name": "Project Beta", "status": "in progress"}
                ]
            }
        }

        # Expected flattened dictionary
        expected_flattened_data = {
            "name": "John Doe",
            "contact.email": "johndoe@example.com",
            "contact.phone": "123-456-7890",
            "employment.company": "OpenAI",
            "employment.position": "Engineer",
            "employment.projects[0].name": "Project Alpha",
            "employment.projects[0].status": "completed",
            "employment.projects[1].name": "Project Beta",
            "employment.projects[1].status": "in progress"
        }

        # Call flatten_dict function and compare with expected output
        flattened_data = flatten_dict(nested_data)
        self.assertEqual(flattened_data, expected_flattened_data)
