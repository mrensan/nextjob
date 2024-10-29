from datetime import date
import unittest

from unittest.mock import patch, MagicMock

from tinydb import Query
from backend.models import Company, Person, Role, TITLE, EmploymentType, WorkLocation, Interview, InterviewType
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

    def test_get_company_by_interview_uuid_found(self):
        """Test get_company_by_interview_uuid found"""
        mock_company = {
            "uuid": "12345",
            "name": "Test Company",
            "recruiters": [],
            "roles": [
                {
                    "uuid": "role123",
                    "title": "Engineer",
                    "applied_date": str(date.today()),
                    "interviews": [
                        {
                            "uuid": "interview123",
                            "sequence": 1,
                            "title": "Recruiter",
                            "type": "Recruiter",
                            "date": str(date.today())
                        }
                    ]
                }
            ]
        }
        self.mock_companies_table.search.return_value = [mock_company]
        result = self.data_service.get_company_by_interview_uuid("interview123")

        query = Query()
        self.mock_companies_table.search.assert_called_once_with(
            query.roles.any(query.interviews.any(query.uuid == "interview123"))
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Company)
        self.assertEqual(result.name, "Test Company")

    def test_get_company_by_interview_uuid_not_found(self):
        """Test get_company_by_interview_uuid not found"""
        self.mock_companies_table.search.return_value = []
        result = self.data_service.get_company_by_interview_uuid("interview123")

        query = Query()
        self.mock_companies_table.search.assert_called_once_with(
            query.roles.any(query.interviews.any(query.uuid == "interview123"))
        )
        self.assertIsNone(result)

    def test_get_company_by_role_uuid_found(self):
        """Test get_company_by_role_uuid found"""
        mock_company = {
            "uuid": "12345",
            "name": "Test Company",
            "recruiters": [],
            "roles": [
                {"uuid": "role123", "title": "Engineer", "applied_date": str(date.today())}
            ]
        }
        self.mock_companies_table.search.return_value = [mock_company]
        result = self.data_service.get_company_by_role_uuid("role123")

        query = Query()
        self.mock_companies_table.search.assert_called_once_with(
            query.roles.any(query.uuid == "role123")
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Company)
        self.assertEqual(result.name, "Test Company")

    def test_get_company_by_role_uuid_not_found(self):
        """Test get_company_by_role_uuid not found"""
        self.mock_companies_table.search.return_value = []
        result = self.data_service.get_company_by_role_uuid("role123")

        query = Query()
        self.mock_companies_table.search.assert_called_once_with(
            query.roles.any(query.uuid == "role123")
        )
        self.assertIsNone(result)

    @patch('backend.models.Company.model_dump_json')
    def test_insert_company(self, mock_model_dump_json):
        """Test insert_company"""
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
        self.data_service.insert_company(mock_company)

        mock_model_dump_json.assert_called_once_with(exclude_none=True)
        self.mock_companies_table.insert.assert_called_once_with(
            {"uuid": "12345", "name": "Test Company"}
        )

    @patch('backend.models.Company.model_dump_json')
    def test_update_company(self, mock_model_dump_json):
        """Test update_company"""
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
        self.data_service.update_company(mock_company)

        mock_model_dump_json.assert_called_once_with(exclude_none=True)
        query = Query()
        self.mock_companies_table.update.assert_called_once_with(
            {"uuid": "12345", "name": "Test Company"}, query.uuid == "12345"
        )

    def test_delete_company(self):
        """Test delete_company"""
        query = Query()
        self.data_service.delete_company("12345")
        self.mock_companies_table.remove.assert_called_once_with(query.uuid == "12345")

    def test_delete_role(self):
        """Test delete_role"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[],
            roles=[
                Role(uuid="role123", title="Engineer", applied_date=date.today())
            ]
        )
        with patch.object(self.data_service, 'get_company_by_role_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_role("role123")
                self.assertEqual(len(mock_company.roles), 0)
                mock_update_company.assert_called_once_with(mock_company)

    def test_delete_role_not_found(self):
        """Test delete_role when role is not found"""
        mock_company = Company(uuid="12345", name="Test Company", recruiters=[], roles=[])
        with patch.object(self.data_service, 'get_company_by_role_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_role("role123")
                mock_update_company.assert_not_called()

    def test_delete_interview(self):
        """Test delete_interview"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[],
            roles=[
                Role(
                    uuid="role123",
                    title="Engineer",
                    applied_date=date.today(),
                    interviews=[Interview(uuid="interview123", sequence=1, title="Recruiter", type="Recruiter",
                                          date=date.today())]
                )
            ]
        )
        with patch.object(self.data_service, 'get_company_by_interview_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_interview("interview123")
                self.assertEqual(len(mock_company.roles[0].interviews), 0)
                mock_update_company.assert_called_once_with(mock_company)

    def test_delete_interview_not_found(self):
        """Test delete_interview when interview is not found"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[],
            roles=[
                Role(
                    uuid="role123",
                    title="Engineer",
                    applied_date=date.today(),
                    interviews=[]
                )
            ]
        )
        with patch.object(self.data_service, 'get_company_by_interview_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_interview("interview123")
                mock_update_company.assert_not_called()

    def test_delete_interviewer(self):
        """Test delete_interviewer"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[],
            roles=[
                Role(
                    uuid="role123",
                    title="Engineer",
                    applied_date=date.today(),
                    interviews=[
                        Interview(
                            uuid="interview123",
                            sequence=1,
                            title="Recruiter",
                            type=InterviewType.RECRUITER,
                            date=date.today(),
                            interviewers=[Person(uuid="interviewer123", name="Interviewer", title=TITLE.MR)]
                        )
                    ]
                )
            ]
        )
        with patch.object(self.data_service, 'get_company_by_interview_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_interviewer("interviewer123", "interview123")
                self.assertEqual(len(mock_company.roles[0].interviews[0].interviewers), 0)
                mock_update_company.assert_called_once_with(mock_company)

    def test_delete_interviewer_not_found(self):
        """Test delete_interviewer when interviewer is not found"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[],
            roles=[
                Role(
                    uuid="role123",
                    title="Engineer",
                    applied_date=date.today(),
                    interviews=[
                        Interview(
                            uuid="interview123",
                            sequence=1,
                            title="Recruiter",
                            type=InterviewType.RECRUITER,
                            date=date.today(),
                            interviewers=[Person(uuid="different_uuid", name="Other Interviewer", title=TITLE.MR)]
                        )
                    ]
                )
            ]
        )
        with patch.object(self.data_service, 'get_company_by_interview_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_interviewer("interviewer123", "interview123")
                self.assertEqual(len(mock_company.roles[0].interviews[0].interviewers), 1)
                mock_update_company.assert_not_called()

    def test_delete_recruiter(self):
        """Test delete_recruiter"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[Person(uuid="recruiter123", name="Recruiter", title=TITLE.MR)],
            roles=[]
        )
        with patch.object(self.data_service, 'get_company_by_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_recruiter("recruiter123", "12345")
                self.assertEqual(len(mock_company.recruiters), 0)
                mock_update_company.assert_called_once_with(mock_company)

    def test_delete_recruiter_not_found(self):
        """Test delete_recruiter when recruiter is not found"""
        mock_company = Company(
            uuid="12345",
            name="Test Company",
            recruiters=[Person(uuid="different_uuid", name="Other Recruiter", title=TITLE.MS)],
            roles=[]
        )
        with patch.object(self.data_service, 'get_company_by_uuid', return_value=mock_company):
            with patch.object(self.data_service, 'update_company') as mock_update_company:
                self.data_service.delete_recruiter("recruiter123", "12345")
                self.assertEqual(len(mock_company.recruiters), 1)
                mock_update_company.assert_not_called()
