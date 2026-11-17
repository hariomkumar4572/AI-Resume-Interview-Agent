import json
import logging
from typing import Dict, Any, List, Optional, Callable
from google.genai import types

from services.gemini_service import GeminiService
from tools.question_generator import generate_interview_questions
from tools.question_validator import validate_questions

logger = logging.getLogger(__name__)


class InterviewAgent:
    """
    Autonomous Interview Agent that employs Gemini Function Calling to
    generate, inspect, and validate personalized interview questions
    based on student profile data.
    """

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service or GeminiService()

    def generate_interview_package(
        self,
        profile_data: Dict[str, Any],
        difficulty: str = "Medium",
        num_questions: int = 20,
        on_step_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes an agentic question generation and validation cycle
        using genuine Gemini Function Calling.
        """
        if not self.gemini_service.is_configured():
            raise ValueError("Gemini API key is required to run Interview Agent.")

        step = lambda tool_name, desc: on_step_callback(tool_name, desc) if on_step_callback else None

        # Build tools for the Interview Agent
        def tool_generate_interview_questions(diff_level: str = difficulty, total_count: int = num_questions) -> str:
            """Tool 5: generate_interview_questions - Generate personalized interview questions based on the candidate's profile."""
            res = generate_interview_questions(
                profile_data=profile_data,
                difficulty=diff_level or difficulty,
                num_questions=total_count or num_questions,
                gemini_service=self.gemini_service,
            )
            return json.dumps(res)

        def tool_validate_questions(raw_questions_json: str) -> str:
            """Tool 6: validate_questions - Verify that questions are relevant, technically appropriate and non-repetitive."""
            try:
                parsed = json.loads(raw_questions_json)
                q_list = parsed.get("questions", parsed) if isinstance(parsed, dict) else parsed
            except Exception:
                q_list = []
            res = validate_questions(
                questions=q_list,
                profile_data=profile_data,
                gemini_service=self.gemini_service,
            )
            return json.dumps(res)

        tools_list = [
            tool_generate_interview_questions,
            tool_validate_questions,
        ]

        system_instruction = (
            "You are the Lead Technical Interview Agent. Your role is to generate personalized, high-caliber "
            "interview questions tailored specifically to a candidate's verified profile.\n"
            "WORKFLOW:\n"
            "1. Call `tool_generate_interview_questions` to create questions matching the requested count and difficulty.\n"
            "2. Call `tool_validate_questions` with the generated questions to verify technical accuracy and eliminate repetition.\n"
            "3. Conclude by returning the validated question list conforming to the expected JSON format.\n"
        )

        user_prompt = (
            f"Please generate {num_questions} {difficulty}-difficulty interview questions for this candidate. "
            f"Use `tool_generate_interview_questions` first, then validate them with `tool_validate_questions`."
        )

        contents = [user_prompt]
        max_turns = 6
        last_generated_questions: List[Dict[str, Any]] = []
        last_validated_questions: List[Dict[str, Any]] = []

        for turn in range(max_turns):
            response = self.gemini_service.client.models.generate_content(
                model=self.gemini_service.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=tools_list,
                    temperature=0.2,
                ),
            )

            function_calls = response.function_calls
            if not function_calls:
                # Model done calling tools
                break

            contents.append(response.candidates[0].content)

            tool_responses_parts = []
            for call in function_calls:
                fn_name = call.name
                fn_args = call.args or {}
                step(fn_name, f"Executing tool {fn_name}...")

                result_output = ""
                if fn_name == "tool_generate_interview_questions":
                    result_output = tool_generate_interview_questions(**fn_args)
                    try:
                        data = json.loads(result_output)
                        last_generated_questions = data.get("questions", [])
                    except Exception:
                        pass
                elif fn_name == "tool_validate_questions":
                    result_output = tool_validate_questions(**fn_args)
                    try:
                        data = json.loads(result_output)
                        last_validated_questions = data.get("validated_questions", [])
                    except Exception:
                        pass
                else:
                    result_output = json.dumps({"error": f"Unknown tool: {fn_name}"})

                tool_responses_parts.append(
                    types.Part.from_function_response(
                        name=fn_name,
                        response={"result": result_output},
                    )
                )

            contents.append(types.Content(parts=tool_responses_parts, role="tool"))

        # Fallback guarantee: if function calling didn't reach validation
        if not last_generated_questions:
            step("generate_interview_questions", "Generating personalized interview questions...")
            gen_res = generate_interview_questions(
                profile_data=profile_data,
                difficulty=difficulty,
                num_questions=num_questions,
                gemini_service=self.gemini_service,
            )
            last_generated_questions = gen_res.get("questions", [])

        if not last_validated_questions:
            step("validate_questions", "Validating questions against profile...")
            val_res = validate_questions(
                questions=last_generated_questions,
                profile_data=profile_data,
                gemini_service=self.gemini_service,
            )
            last_validated_questions = val_res.get("validated_questions", last_generated_questions)

        # Assemble compact candidate profile for standard output
        skills_summary = (
            profile_data.get("programming_languages", [])
            + profile_data.get("frameworks_libraries", [])
            + profile_data.get("databases", [])
            + profile_data.get("technical_skills", [])
        )
        # Deduplicate skills summary while preserving order
        dedup_skills = list(dict.fromkeys([s for s in skills_summary if s and s != "Not Provided"]))

        projects_summary = []
        for p in profile_data.get("projects", []):
            if isinstance(p, dict):
                title = p.get("title", "")
                if title:
                    projects_summary.append(title)
            elif isinstance(p, str):
                projects_summary.append(p)

        experience_summary = []
        for exp in profile_data.get("internships", []) + profile_data.get("work_experience", []):
            if isinstance(exp, dict):
                role = exp.get("role", "")
                company = exp.get("company", "")
                if role or company:
                    experience_summary.append(f"{role} at {company}".strip(" at "))
            elif isinstance(exp, str):
                experience_summary.append(exp)

        output_payload = {
            "student_profile": {
                "name": profile_data.get("name", "Student Name"),
                "skills": dedup_skills,
                "projects": projects_summary,
                "experience": experience_summary,
            },
            "questions": last_validated_questions,
        }

        return output_payload
