import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from services.gemini_service import GeminiService


class SkillsCategorization(BaseModel):
    technical_skills: List[str] = Field(default_factory=list, description="General CS or tech concepts, e.g. OOP, REST APIs, Git, Docker")
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages explicitly present, e.g. Python, Java, C++, TypeScript")
    frameworks_libraries: List[str] = Field(default_factory=list, description="Frameworks and libraries explicitly present, e.g. React, Spring Boot, PyTorch, Pandas")
    databases: List[str] = Field(default_factory=list, description="Databases and data stores explicitly present, e.g. PostgreSQL, MongoDB, Redis")


def identify_skills(resume_text: str, gemini_service: Optional[GeminiService] = None) -> Dict[str, Any]:
    """
    Tool 3: identify_skills
    Identify technical skills, programming languages, frameworks, and databases strictly
    present in the resume text.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    service = gemini_service or GeminiService()
    if not service.is_configured():
        raise ValueError("GeminiService is not configured with an API key.")

    system_prompt = (
        "You are a specialized technical recruiter assistant. Your sole role is to accurately identify "
        "all technical skills, programming languages, frameworks/libraries, and databases present in the resume.\n"
        "RULES:\n"
        "1. Only include skills and tools that are explicitly mentioned in the resume text.\n"
        "2. Do not invent any skills.\n"
        "3. Accurately categorize each item."
    )

    prompt = f"Identify all skills, programming languages, frameworks, and databases from this resume text:\n\n{resume_text}"

    try:
        response = service.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            response_schema=SkillsCategorization,
            temperature=0.1,
        )
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"Error in identify_skills tool: {str(e)}") from e
