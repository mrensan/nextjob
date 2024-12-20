import json
import logging
from typing import List

from tinydb import TinyDB, Query

from backend.datautils import flatten_dict, get_data_file, sort_companies_by_applied_date
from backend.models import Company


class DataService:
    """Class for data service."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.db = TinyDB(get_data_file())
        self.companies_table = self.db.table("companies", cache_size=0)

    def get_companies(self) -> List[Company]:
        """Get all companies."""
        return sort_companies_by_applied_date([Company(**document) for document in self.companies_table.all()])

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

    def delete_interviewer(self, person_uuid, interview_uuid):
        """Delete an interviewer."""
        company = self.get_company_by_interview_uuid(interview_uuid)
        for role in company.roles:
            for interview in role.interviews:
                if interview.uuid == interview_uuid:
                    for person in interview.interviewers:
                        if person.uuid == person_uuid:
                            interview.interviewers.remove(person)
                            self.update_company(company)
                            return

    def delete_recruiter(self, person_uuid, company_uuid):
        """Delete a recruiter."""
        company = self.get_company_by_uuid(company_uuid)
        for recruiter in company.recruiters:
            if recruiter.uuid == person_uuid:
                company.recruiters.remove(recruiter)
                self.update_company(company)
                return

    def search_in_db(self, search_string):
        """Search in db."""
        results = []
        for doc in self.companies_table.all():
            flat_doc = flatten_dict(doc)
            if any(search_string.lower() in value.lower() for value in flat_doc.values()):
                results.append(doc)
        return sort_companies_by_applied_date([Company(**document) for document in results])

    @staticmethod
    def __company_to_json(company):
        str_value = company.model_dump_json(exclude_none=True)
        return json.loads(str_value)
