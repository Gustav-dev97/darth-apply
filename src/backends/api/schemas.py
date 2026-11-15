"""
Pydantic schemas for the profile API.

NOTE: this project pins pydantic 1.x, so ORM-to-schema conversion uses
`orm_mode = True` (not pydantic v2's `from_attributes`).
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# --- Profile (scalar fields) -------------------------------------------------


class UserProfileBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=3, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=120)
    state: Optional[str] = Field(None, max_length=2)
    headline: Optional[str] = Field(None, max_length=300)
    summary: Optional[str] = None


class UserProfileUpdate(UserProfileBase):
    """Payload accepted by PUT /api/profile."""


# --- Experience --------------------------------------------------------------


class ExperienceBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceRead(ExperienceBase):
    id: int

    class Config:
        orm_mode = True


# --- Education ---------------------------------------------------------------


class EducationBase(BaseModel):
    institution: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=200)
    field_of_study: Optional[str] = Field(None, max_length=200)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False


class EducationCreate(EducationBase):
    pass


class EducationRead(EducationBase):
    id: int

    class Config:
        orm_mode = True


# --- Skill -------------------------------------------------------------------


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=80)
    proficiency: Optional[int] = Field(None, ge=1, le=5)


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int

    class Config:
        orm_mode = True


# --- Link --------------------------------------------------------------------


class LinkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=3, max_length=500)


class LinkCreate(LinkBase):
    pass


class LinkRead(LinkBase):
    id: int

    class Config:
        orm_mode = True


# --- Project -----------------------------------------------------------------


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    link: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int

    class Config:
        orm_mode = True


# --- AI Requests -------------------------------------------------------------


class EnhanceSummaryRequest(BaseModel):
    raw_summary: str = Field(..., min_length=10)


class EnhanceDescriptionRequest(BaseModel):
    raw_text: str = Field(..., min_length=5)
    context_type: str = Field(..., description="'experience' ou 'project'")
    context_title: Optional[str] = Field(None, description="Cargo ou Nome do Projeto")

# --- Nested profile ----------------------------------------------------------


class UserProfileRead(UserProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    experiences: list[ExperienceRead] = []
    educations: list[EducationRead] = []
    skills: list[SkillRead] = []
    links: list[LinkRead] = []
    projects: list[ProjectRead] = []

    class Config:
        orm_mode = True