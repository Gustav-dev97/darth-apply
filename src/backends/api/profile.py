"""
Profile endpoints.

Darth Apply is a single-user, local-first app, so there is exactly one
profile per installation. Endpoints for experiences, educations, skills,
links, projects and courses are sub-resources of /api/profile.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, selectinload

from db import (
    Course,
    Education,
    Experience,
    Link,
    Project,
    Skill,
    UserProfile,
    get_db,
)

from .schemas import (
    CourseCreate,
    CourseRead,
    EducationCreate,
    EducationRead,
    ExperienceCreate,
    ExperienceRead,
    LinkCreate,
    LinkRead,
    ProjectCreate,
    ProjectRead,
    SkillCreate,
    SkillRead,
    UserProfileRead,
    UserProfileUpdate,
)

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _require_profile(db: Session) -> UserProfile:
    """Fetch the singleton profile or fail with 409 if it doesn't exist yet."""
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile must be created before adding sub-resources",
        )
    return profile


# --- Profile -----------------------------------------------------------------


@router.get("", response_model=UserProfileRead)
def get_profile(db: Session = Depends(get_db)):
    profile = (
        db.query(UserProfile)
        .options(
            selectinload(UserProfile.experiences),
            selectinload(UserProfile.educations),
            selectinload(UserProfile.skills),
            selectinload(UserProfile.links),
            selectinload(UserProfile.projects),
            selectinload(UserProfile.courses),
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not created yet")
    return profile


@router.put("", response_model=UserProfileRead)
def upsert_profile(payload: UserProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if profile:
        for field, value in payload.dict().items():
            setattr(profile, field, value)
    else:
        profile = UserProfile(**payload.dict())
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


# --- Experience CRUD ---------------------------------------------------------


def _validate_experience_dates(start_date, end_date, is_current):
    if is_current:
        return None
    if end_date and start_date > end_date:
        raise HTTPException(
            status_code=400, detail="end_date must be greater than or equal to start_date"
        )
    return end_date


@router.post(
    "/experiences",
    response_model=ExperienceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_experience(payload: ExperienceCreate, db: Session = Depends(get_db)):
    profile = _require_profile(db)
    data = payload.dict()
    data["end_date"] = _validate_experience_dates(
        data["start_date"], data["end_date"], data["is_current"]
    )
    exp = Experience(profile_id=profile.id, **data)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.put("/experiences/{exp_id}", response_model=ExperienceRead)
def update_experience(
    exp_id: int, payload: ExperienceCreate, db: Session = Depends(get_db)
):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    data = payload.dict()
    data["end_date"] = _validate_experience_dates(
        data["start_date"], data["end_date"], data["is_current"]
    )
    for field, value in data.items():
        setattr(exp, field, value)
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/experiences/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(exp_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    db.delete(exp)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Education CRUD ----------------------------------------------------------


def _validate_education_dates(start_date, end_date, is_current):
    if is_current:
        return None
    if end_date and start_date > end_date:
        raise HTTPException(
            status_code=400, detail="end_date must be greater than or equal to start_date"
        )
    return end_date


@router.post(
    "/educations",
    response_model=EducationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_education(payload: EducationCreate, db: Session = Depends(get_db)):
    profile = _require_profile(db)
    data = payload.dict()
    data["end_date"] = _validate_education_dates(
        data["start_date"], data["end_date"], data["is_current"]
    )
    edu = Education(profile_id=profile.id, **data)
    db.add(edu)
    db.commit()
    db.refresh(edu)
    return edu


@router.put("/educations/{edu_id}", response_model=EducationRead)
def update_education(
    edu_id: int, payload: EducationCreate, db: Session = Depends(get_db)
):
    edu = db.query(Education).filter(Education.id == edu_id).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    data = payload.dict()
    data["end_date"] = _validate_education_dates(
        data["start_date"], data["end_date"], data["is_current"]
    )
    for field, value in data.items():
        setattr(edu, field, value)
    db.commit()
    db.refresh(edu)
    return edu


@router.delete("/educations/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(edu_id: int, db: Session = Depends(get_db)):
    edu = db.query(Education).filter(Education.id == edu_id).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    db.delete(edu)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Skill CRUD --------------------------------------------------------------


@router.post(
    "/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED
)
def create_skill(payload: SkillCreate, db: Session = Depends(get_db)):
    profile = _require_profile(db)
    skill = Skill(profile_id=profile.id, **payload.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.put("/skills/{skill_id}", response_model=SkillRead)
def update_skill(
    skill_id: int, payload: SkillCreate, db: Session = Depends(get_db)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    for field, value in payload.dict().items():
        setattr(skill, field, value)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Link CRUD ---------------------------------------------------------------


@router.post(
    "/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED
)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    profile = _require_profile(db)
    link = Link(profile_id=profile.id, **payload.dict())
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: int, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Project CRUD ------------------------------------------------------------


@router.post(
    "/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED
)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    profile = _require_profile(db)
    project = Project(profile_id=profile.id, **payload.dict())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Course CRUD -------------------------------------------------------------


@router.post(
    "/courses", response_model=CourseRead, status_code=status.HTTP_201_CREATED
)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    profile = _require_profile(db)
    course = Course(profile_id=profile.id, **payload.dict())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)