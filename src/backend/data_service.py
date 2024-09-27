import json
from typing import List

from tinydb import TinyDB, Query

from backend.models import Company


class DataService:
    """Class for data service."""

    def __init__(self):
        self.db = TinyDB("../../db.json")
        self.companies_table = self.db.table("companies")

    def get_companies(self) -> List[Company]:
        """Get all companies."""
        return [Company(**document) for document in self.companies_table.all()]

    def get_company_by_uuid(self, company_uuid) -> Company:
        """Get company by uuid."""
        query = Query()
        document = self.companies_table.search(query.uuid == company_uuid)
        return Company(**document[0]) if document and len(document) > 0 else None

    def save_company(self, company):
        """Save company."""
        self.companies_table.insert(self.__company_to_json(company))

    def __company_to_json(self, company):
        str_value = company.model_dump_json(exclude_none=True)
        return json.loads(str_value)
