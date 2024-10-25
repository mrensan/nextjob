from datetime import date
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TITLE(Enum):
    """Enum to represent title of a person."""
    MR = 'Mr'
    MS = 'Ms'
    NA = '-'


class InterviewType(Enum):
    """Enum to represent type of interview."""
    RECRUITER = 'Recruiter'
    TECH_CODE = 'Code technical'
    TECH_DESIGN = 'Design technical'
    REC_MANAGER = 'Recruiter manager'
    TEAM = 'Team'


class WorkLocation(Enum):
    """Enum to represent work location type."""
    ON_SITE = 'On site'
    HYBRID = 'Hybrid'
    REMOTE = 'Remote'


class EmploymentType(Enum):
    """Enum to represent employment type."""
    FULL_TIME = 'Full time'
    PART_TIME = 'Part time'
    CONTRACT = 'Contract'


class Person(BaseModel):
    """Model representing a person with first name, last name, and other properties."""
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    title: TITLE


class Interview(BaseModel):
    """Model representing an interview."""
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    sequence: int
    title: str
    type: InterviewType
    date: date
    interviewers: Optional[List[Person]] = []


class Role(BaseModel):
    """Model representing an applied role."""
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    applied_date: date
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    work_location: WorkLocation = Field(default=WorkLocation.HYBRID)
    description: Optional[str] = None
    interviews: Optional[List[Interview]] = []


class Company(BaseModel):
    """Model representing a company."""
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    website: Optional[str] = None
    recruiters: List[Person] = []
    roles: List[Role] = []
