from datetime import date
from uuid import UUID

import pytest
from pydantic import ValidationError

from backend.models import (Person, TITLE, Interview, InterviewType,
                            Role, EmploymentType, WorkLocation, Company)


def test_person_validation():
    """Test Person validity"""
    person = Person(name="John Doe", title=TITLE.MR)
    assert person.name == "John Doe"
    assert person.title == TITLE.MR
    assert person.role is None
    assert person.email is None
    assert person.description is None

    # Test missing required fields
    with pytest.raises(ValidationError):
        Person(role="Developer")  # Missing name and title

    # Test invalid title
    with pytest.raises(ValidationError):
        Person(name="John Doe", title="Unknown")  # Invalid enum value


def test_interview_validation():
    """Test Interview validity"""
    interview = Interview(
        sequence=1,
        title="Technical Interview",
        type=InterviewType.TECH_CODE,
        date=date.today()
    )
    assert interview.sequence == 1
    assert interview.title == "Technical Interview"
    assert interview.type == InterviewType.TECH_CODE
    assert interview.date == date.today()
    assert not interview.interviewers

    # Test missing required fields
    with pytest.raises(ValidationError):
        Interview(
            title="Technical Interview",
            type=InterviewType.TECH_CODE
        )  # Missing sequence and date


def test_role_validation():
    """Test Role validity"""
    role = Role(title="Software Engineer", applied_date=date.today())
    assert role.title == "Software Engineer"
    assert role.applied_date == date.today()
    assert role.employment_type == EmploymentType.FULL_TIME
    assert role.work_location == WorkLocation.HYBRID
    assert role.description is None
    assert not role.interviews

    # Test missing required fields
    with pytest.raises(ValidationError):
        Role(employment_type=EmploymentType.CONTRACT)  # Missing title and applied_date

    # Test invalid enum values
    with pytest.raises(ValidationError):
        Role(title="Engineer", applied_date=date.today(),
             work_location="anywhere")  # Invalid enum value for work_location


def test_company_validation():
    """Test Company validity"""
    person1 = Person(name="Jane Doe", title=TITLE.MS)
    person2 = Person(name="John Smith", title=TITLE.MR)
    role = Role(title="Data Scientist", applied_date=date.today())

    # Test valid Company
    company = Company(name="Tech Corp", recruiters=[person1, person2], roles=[role])
    assert isinstance(company.uuid, str)
    assert UUID(company.uuid)  # Valid UUID format
    assert company.name == "Tech Corp"
    assert company.recruiters == [person1, person2]
    assert company.roles == [role]

    # Test missing required fields
    with pytest.raises(ValidationError):
        Company(recruiters=[person1], roles=[role])  # Missing name
