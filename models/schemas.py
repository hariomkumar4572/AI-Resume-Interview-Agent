from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectDetail(BaseModel):
    title: str = Field(description="Name or title of the project")
    description: str = Field(description="Brief overview and objectives of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies, libraries, or tools used")
    responsibilities: List[str] = Field(default_factory=list, description="Key tasks or contributions performed by the candidate")


class ExperienceDetail(BaseModel):
    role: str = Field(description="Job title or role (e.g. Software Engineer Intern)")
    company: str = Field(description="Organization or company name")
    duration: Optional[str] = Field(default="Not Provided", description="Dates or duration of the experience")
    tasks: List[str] = Field(default_factory=list, description="Key tasks, achievements, or responsibilities")
    technologies: List[str] = Field(default_factory=list, description="Technologies or tools used")


class StudentProfile(BaseModel):
    name: str = Field(default="Not Provided", description="Candidate's full name")
    educational_qualification: str = Field(default="Not Provided", description="Degree or highest qualification")
    college_university: str = Field(default="Not Provided", description="Institution or university name")
    technical_skills: List[str] = Field(default_factory=list, description="General technical concepts or skills")
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages (e.g., Python, Java)")
    frameworks_libraries: List[str] = Field(default_factory=list, description="Frameworks & libraries (e.g., React, FastAPI)")
    databases: List[str] = Field(default_factory=list, description="Databases (e.g., PostgreSQL, MongoDB)")
    projects: List[ProjectDetail] = Field(default_factory=list, description="Projects extracted from resume")
    internships: List[ExperienceDetail] = Field(default_factory=list, description="Internship experiences")
    work_experience: List[ExperienceDetail] = Field(default_factory=list, description="Full-time or part-time work experience")
    certifications: List[str] = Field(default_factory=list, description="Certifications, licenses or accreditations")


class StudentProfileCompact(BaseModel):
    """Compact profile format conforming directly to section 8 schema."""
    name: str = "Not Provided"
    skills: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)


class InterviewQuestion(BaseModel):
    question_id: int = Field(description="Sequential identifier for the question")
    category: str = Field(description="Category: 'Technical', 'Project-Based', 'Internship/Experience', 'HR', or 'Coding'")
    question: str = Field(description="The interview question text")
    difficulty: str = Field(description="Difficulty level: 'Easy', 'Medium', or 'Hard'")
    related_skill: str = Field(description="Skill, project, or topic from the resume that this question evaluates")
    reason: str = Field(description="Specific explanation of why this question is asked based on the resume")
    expected_answer_points: List[str] = Field(default_factory=list, description="Key criteria/points the interviewer expects in an answer")


class InterviewOutput(BaseModel):
    student_profile: StudentProfileCompact = Field(description="Compact summary of candidate profile")
    questions: List[InterviewQuestion] = Field(default_factory=list, description="List of generated personalized questions")
