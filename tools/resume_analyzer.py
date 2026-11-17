import json
from typing import Dict, Any, Optional
from models.schemas import StudentProfile
from services.gemini_service import GeminiService


def analyze_resume(resume_text: str, gemini_service: Optional[GeminiService] = None) -> Dict[str, Any]:
    """
    Tool 2: analyze_resume
    Analyzes the resume text to extract candidate name, educational qualification,
    college/university, technical skills, languages, frameworks, databases, projects,
    internships, work experience, and certifications.
    Never invents skills or experience; missing items are marked as 'Not Provided' or empty list.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty. Cannot analyze resume.")

    service = gemini_service or GeminiService()
    if not service.is_configured():
        raise ValueError("GeminiService is not configured with an API key.")

    system_prompt = (
        "You are an expert AI Resume Analyzer. Your job is to accurately extract "
        "the student's profile information strictly from the provided resume text.\n"
        "RULES:\n"
        "1. Extract ONLY information that is explicitly stated in the resume.\n"
        "2. NEVER invent, hallucinate, or extrapolate skills, projects, or experiences.\n"
        "3. If a field (e.g. name, college, qualification, duration) is missing, mark it as 'Not Provided'.\n"
        "4. If no projects, internships, or work experiences exist, return an empty list for that field.\n"
        "5. Categorize skills carefully into programming_languages, frameworks_libraries, databases, and general technical_skills.\n"
        "6. Return the exact JSON schema provided."
    )

    prompt = f"Please analyze this resume text and extract the candidate's profile strictly according to instructions:\n\n{resume_text}"

    try:
        response = service.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            response_schema=StudentProfile,
            temperature=0.1,
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        raise RuntimeError(f"Error in analyze_resume tool: {str(e)}") from e
