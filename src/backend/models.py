from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel


class TITLE(Enum):
    """Enum to represent title of a person."""
    MR = 'Mr'
    MS = 'Ms'
    NA = 'na'


class InterviewType(Enum):
    """Enum to represent type of interview."""
    RECRUITER = 'recruiter'
    TECH_CODE = 'tech_code'
    TECH_DESIGN = 'tech_design'
    REC_MANAGER = 'rec_manager'
    TEAM = 'team'


class WorkLocation(Enum):
    """Enum to represent work location type."""
    ON_SITE = 'on_site'
    HYBRID = 'hybrid'
    REMOTE = 'remote'


class EmploymentType(Enum):
    """Enum to represent employment type."""
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    CONTRACT = 'contract'


class Person(BaseModel):
    """Model representing a person with first name, last name, and other properties."""
    firstName: str
    lastName: str
    role: str
    description: str
    title: TITLE


class Interview(BaseModel):
    """Model representing an interview."""
    sequence: int
    title: str
    type: InterviewType
    date: date
    interviewers: List[Person]


class Role(BaseModel):
    """Model representing an applied role."""
    sequence: int
    title: str
    applied_date: date
    employment_type: EmploymentType
    work_location: WorkLocation
    steps: List[Interview]


class Company(BaseModel):
    """Model representing a company."""
    name: str
    website: str
    recruiters: List[Person]
    roles: List[Role]
