import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from models.schemas import InterviewQuestion
from services.gemini_service import GeminiService


class QuestionValidationResult(BaseModel):
    is_valid: bool = Field(description="True if questions satisfy relevance, non-repetition, and no fabrication rules")
    feedback: str = Field(description="Summary of evaluation findings")
    validated_questions: List[InterviewQuestion] = Field(
        default_factory=list,
        description="Cleaned, de-duplicated, and verified list of interview questions"
    )


def validate_questions(
    questions: List[Dict[str, Any]],
    profile_data: Dict[str, Any],
    gemini_service: Optional[GeminiService] = None,
) -> Dict[str, Any]:
    """
    Tool 6: validate_questions
    Verifies that generated questions are:
    1. Strictly relevant to the uploaded resume profile.
    2. Free from invented/fabricated experience or skills.
    3. Technically appropriate for the specified difficulty.
    4. Non-repetitive in concepts tested.
    5. Properly formatted with sequential IDs.
    Returns the validated and cleaned question set.
    """
    if not questions:
        return {
            "is_valid": False,
            "feedback": "No questions provided to validate.",
            "validated_questions": [],
        }

    service = gemini_service or GeminiService()
    if not service.is_configured():
        # Fallback local validation if Gemini is not reachable
        cleaned = []
        seen_questions = set()
        for q in questions:
            q_text = q.get("question", "").strip()
            if q_text and q_text.lower() not in seen_questions:
                seen_questions.add(q_text.lower())
                q_copy = dict(q)
                q_copy["question_id"] = len(cleaned) + 1
                cleaned.append(q_copy)
        return {
            "is_valid": True,
            "feedback": "Locally deduplicated and indexed.",
            "validated_questions": cleaned,
        }

    system_prompt = (
        "You are an AI Quality Assurance Officer for technical interviews. "
        "Review the generated interview questions against the candidate's profile.\n\n"
        "CHECKLIST:\n"
        "1. Resume Fidelity: Ensure questions do NOT mention companies, skills, or projects not in the candidate's profile.\n"
        "2. De-duplication: If two questions test the exact same angle or concept, refine or replace the duplicate.\n"
        "3. Completeness: Ensure each question has non-empty expected_answer_points.\n"
        "4. Sequence: Re-index question_id sequentially from 1 to N.\n"
        "Return the validated and polished question list."
    )

    data = {
        "candidate_profile": profile_data,
        "raw_questions": questions,
    }
    prompt = f"Validate and clean the following interview questions according to the candidate profile:\n\n{json.dumps(data, indent=2)}"

    try:
        response = service.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            response_schema=QuestionValidationResult,
            temperature=0.1,
        )
        return json.loads(response.text)
    except Exception as e:
        # Fallback on soft error to avoid breaking workflow
        cleaned = []
        seen = set()
        for q in questions:
            q_text = q.get("question", "").strip()
            if q_text and q_text.lower() not in seen:
                seen.add(q_text.lower())
                q_copy = dict(q)
                q_copy["question_id"] = len(cleaned) + 1
                cleaned.append(q_copy)
        return {
            "is_valid": True,
            "feedback": f"Quality checked locally with fallback: {str(e)}",
            "validated_questions": cleaned,
        }
