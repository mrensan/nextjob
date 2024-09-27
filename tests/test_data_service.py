from datetime import date
import unittest

from unittest.mock import patch, MagicMock

from tinydb import Query
from backend.models import Company, Person, Role, TITLE, EmploymentType, WorkLocation
from backend.data_service import DataService


class TestDataService(unittest.TestCase):
    """Testing DataService"""

    @patch('backend.data_service.TinyDB')
    def setUp(self, MockTinyDB): # pylint: disable=arguments-differ
        self.mock_db = MagicMock()
        MockTinyDB.return_value = self.mock_db
        self.data_service = DataService()
        self.mock_companies_table = self.mock_db.table.return_value

    def test_get_companies(self):
        """Test get_companies"""
        mock_company = {
            "uuid": "12345",
            "name": "Test Company",
            "recruiters": [],
            "roles": []
        }
        self.mock_companies_table.all.return_value = [mock_company]
        result = self.data_service.get_companies()

        self.mock_companies_table.all.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Company)
        self.assertEqual(result[0].name, "Test Company")

    def test_get_company_by_uuid_found(self):
        """Test get_company_by_uuid"""
        mock_company = {
            "uuid": "12345",
            "name": "Test Company",
            "recruiters": [],
            "roles": []
        }
        self.mock_companies_table.search.return_value = [mock_company]
        result = self.data_service.get_company_by_uuid("12345")

        query = Query()
        self.mock_companies_table.search.assert_called_once_with(query.uuid == "12345")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Company)
        self.assertEqual(result.name, "Test Company")

    def test_get_company_by_uuid_not_found(self):
        """Test get_company by uuid not found"""
        self.mock_companies_table.search.return_value = []
        result = self.data_service.get_company_by_uuid("12345")

        query = Query()
        self.mock_companies_table.search.assert_called_once_with(query.uuid == "12345")
        self.assertIsNone(result)

    @patch('backend.models.Company.model_dump_json')
    def test_save_company(self, mock_model_dump_json):
        """Test save company"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[Person(name="Recruiter", title=TITLE.MR)],
            roles=[
                Role(
                    title="Engineer",
                    applied_date=date.today(),
                    employment_type=EmploymentType.FULL_TIME,
                    work_location=WorkLocation.REMOTE
                )
            ]
        )
        mock_model_dump_json.return_value = '{"uuid": "12345", "name": "Test Company"}'
        self.data_service.save_company(mock_company)

        mock_model_dump_json.assert_called_once_with(exclude_none=True)
        self.mock_companies_table.insert.assert_called_once_with(
            {"uuid": "12345", "name": "Test Company"}
        )
