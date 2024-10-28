import json
import logging
from pathlib import Path
from typing import List

from tinydb import TinyDB, Query

from backend.models import Company

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class DataService:
    """Class for data service."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        database_absolute_path = Path(__file__).resolve().parent / "../../db.json"

        self.db = TinyDB(database_absolute_path)
        self.companies_table = self.db.table("companies", cache_size=0)

    def get_companies(self) -> List[Company]:
        """Get all companies."""
        return [Company(**document) for document in self.companies_table.all()]

    def get_company_by_uuid(self, company_uuid) -> Company:
        """Get company by uuid."""
        query = Query()
        document = self.companies_table.search(query.uuid == company_uuid)
        return Company(**document[0]) if document and len(document) > 0 else None

    def get_company_by_interview_uuid(self, interview_uuid) -> Company:
        """Get company by role_uuid."""
        query = Query()
        document = self.companies_table.search(
            query.roles.any(query.interviews.any(query.uuid == interview_uuid))
        )
        self.logger.debug("Found company by interview uuid: %s", document)
        return Company(**document[0]) if document and len(document) > 0 else None

    def get_company_by_role_uuid(self, role_uuid) -> Company:
        """Get company by role_uuid."""
        query = Query()
        document = self.companies_table.search(
            query.roles.any(query.uuid == role_uuid)
        )
        self.logger.debug("Found company by role uuid: %s", document)
        return Company(**document[0]) if document and len(document) > 0 else None

    def insert_company(self, company):
        """Insert a new company."""
        self.companies_table.insert(self.__company_to_json(company))

    def update_company(self, company):
        """Update a company."""
        query = Query()
        self.companies_table.update(
            self.__company_to_json(company), query.uuid == company.uuid
        )

    def delete_company(self, company_uuid):
        """Delete a company."""
        query = Query()
        self.companies_table.remove(query.uuid == company_uuid)

    def delete_role(self, role_uuid):
        """Delete a role."""
        company = self.get_company_by_role_uuid(role_uuid)
        for role in company.roles:
            if role.uuid == role_uuid:
                company.roles.remove(role)
                self.update_company(company)
                return

    def delete_interview(self, interview_uuid):
        """Delete an interview."""
        company = self.get_company_by_interview_uuid(interview_uuid)
        for role in company.roles:
            for interview in role.interviews:
                if interview.uuid == interview_uuid:
                    role.interviews.remove(interview)
                    self.update_company(company)
                    return

    @staticmethod
    def __company_to_json(company):
        str_value = company.model_dump_json(exclude_none=True)
        return json.loads(str_value)
