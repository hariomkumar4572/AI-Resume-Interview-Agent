import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from models.schemas import ProjectDetail
from services.gemini_service import GeminiService


class ProjectsExtraction(BaseModel):
    projects: List[ProjectDetail] = Field(default_factory=list, description="List of projects identified from the resume")


def identify_projects(resume_text: str, gemini_service: Optional[GeminiService] = None) -> Dict[str, Any]:
    """
    Tool 4: identify_projects
    Extract project names, descriptions, technologies, and candidate responsibilities
    strictly from the resume text.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    service = gemini_service or GeminiService()
    if not service.is_configured():
        raise ValueError("GeminiService is not configured with an API key.")

    system_prompt = (
        "You are an expert technical interviewer assistant. Your task is to extract every project "
        "mentioned in the resume text.\n"
        "For each project, identify:\n"
        "- title: Name of project\n"
        "- description: Objectives and overview\n"
        "- technologies: Specific technologies, tools, and libraries used\n"
        "- responsibilities: Specific tasks or features implemented by the candidate\n"
        "RULES:\n"
        "1. Do not invent any projects or features.\n"
        "2. If no projects are mentioned, return an empty list."
    )

    prompt = f"Extract all projects and their technical details from this resume text:\n\n{resume_text}"

    try:
        response = service.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            response_schema=ProjectsExtraction,
            temperature=0.1,
        )
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"Error in identify_projects tool: {str(e)}") from e
