import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from models.schemas import InterviewQuestion
from services.gemini_service import GeminiService


class QuestionListWrapper(BaseModel):
    questions: List[InterviewQuestion] = Field(default_factory=list)


def generate_interview_questions(
    profile_data: Dict[str, Any],
    difficulty: str = "Medium",
    num_questions: int = 20,
    gemini_service: Optional[GeminiService] = None,
) -> Dict[str, Any]:
    """
    Tool 5: generate_interview_questions
    Generate personalized interview questions based on the candidate's actual analyzed profile.
    Distributes questions across:
      - Technical Questions
      - Project-Based Questions
      - Internship/Experience Questions (or Project/Technical if candidate has no internships)
      - HR Questions
      - Coding Questions
    Strictly adapts to the requested difficulty level ('Easy', 'Medium', 'Hard').
    Never invents unmentioned skills, projects, or work history.
    """
    service = gemini_service or GeminiService()
    if not service.is_configured():
        raise ValueError("GeminiService is not configured with an API key.")

    # Calculate proportional distribution for the requested total count
    total = max(1, num_questions)
    # Target proportions: Tech (25%), Projects (25%), HR (15%), Coding (20%), Experience (15%)
    n_tech = max(1, round(total * 0.25))
    n_proj = max(1, round(total * 0.25))
    n_hr = max(1, round(total * 0.15))
    n_coding = max(1, round(total * 0.20))
    n_exp = total - (n_tech + n_proj + n_hr + n_coding)
    if n_exp < 0:
        n_exp = 0

    has_experience = bool(profile_data.get("internships") or profile_data.get("work_experience"))

    system_prompt = (
        "You are an elite Senior Technical Hiring Manager and Interviewer. Your task is to generate "
        "personalized, highly relevant interview questions for the student based EXCLUSIVELY on their "
        "uploaded resume profile.\n\n"
        "GUIDELINES:\n"
        f"1. Target Difficulty: {difficulty}. Ensure question depth, nuance, and complexity match this level.\n"
        f"   - Easy: Foundational knowledge, syntax, basic concepts, simple problem walkthroughs.\n"
        f"   - Medium: Practical applications, debugging, edge cases, trade-offs, architecture decisions.\n"
        f"   - Hard: Deep internals, performance optimization, concurrency, scalability, complex failure modes.\n"
        f"2. Total Questions required: {total}.\n"
        f"3. Categories distribution target:\n"
        f"   - Technical: ~{n_tech} questions (on languages, frameworks, databases mentioned in resume)\n"
        f"   - Project-Based: ~{n_proj} questions (on architecture, challenges, API design from their projects)\n"
        f"   - HR: ~{n_hr} questions (strengths, career goals, behavioral questions grounded in their background)\n"
        f"   - Coding: ~{n_coding} questions (logic, DSA, or coding questions tailored to their stated skills)\n"
        f"   - Internship/Experience: ~{n_exp} questions.\n"
        "   CRITICAL NOTE ON EXPERIENCE: If the candidate has NO internship or work experience listed, "
        "   DO NOT fabricate any! Instead, re-allocate the experience questions to their personal projects "
        "   or practical technical problem-solving.\n"
        "4. NEVER invent skills, projects, or employment history not found in the profile.\n"
        "5. For every question provide:\n"
        "   - question_id (sequential integer 1..N)\n"
        "   - category ('Technical', 'Project-Based', 'Internship/Experience', 'HR', or 'Coding')\n"
        "   - question (concise, clear, personalized)\n"
        f"   - difficulty ('{difficulty}')\n"
        "   - related_skill (exact skill, project, or role from profile)\n"
        "   - reason (concrete explanation referencing their resume)\n"
        "   - expected_answer_points (3-5 key criteria the candidate should cover)\n"
    )

    profile_json_str = json.dumps(profile_data, indent=2)
    prompt = (
        f"Generate {total} personalized interview questions at difficulty '{difficulty}' "
        f"for this candidate profile:\n\n{profile_json_str}"
    )

    try:
        response = service.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            response_schema=QuestionListWrapper,
            temperature=0.3,
        )
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"Error in generate_interview_questions tool: {str(e)}") from e
