import json
import logging
from typing import Dict, Any, Optional, Callable
from google.genai import types

from services.gemini_service import GeminiService
from tools.resume_extractor import extract_resume
from tools.resume_analyzer import analyze_resume
from tools.skill_identifier import identify_skills
from tools.project_identifier import identify_projects

logger = logging.getLogger(__name__)


class ResumeAgent:
    """
    Autonomous AI Resume Agent that uses Gemini Function Calling to inspect,
    extract, and comprehensively analyze student resumes.
    """

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service or GeminiService()

    def run_analysis_cycle(
        self,
        resume_source: Any,
        file_type: str = "",
        on_step_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes an agentic analysis cycle using genuine Gemini Function Calling.
        The agent determines how to call tools to inspect and analyze the resume.
        """
        if not self.gemini_service.is_configured():
            raise ValueError("Gemini API key is required to run the AI Resume Agent.")

        step = lambda tool_name, desc: on_step_callback(tool_name, desc) if on_step_callback else None

        # Pre-extract or store resume locally in agent state so tool calls can reference it cleanly
        step("extract_resume", "Extracting raw text from resume document...")
        raw_text = extract_resume(resume_source, file_type=file_type)

        # Build tools declarations for Gemini Function Calling
        # In google-genai SDK, Python functions can be passed directly as tools
        def tool_extract_resume(query: str = "") -> str:
            """Tool 1: extract_resume - Extract and return readable resume text from the candidate document."""
            return raw_text[:4000]

        def tool_analyze_resume(summary_focus: str = "full") -> str:
            """Tool 2: analyze_resume - Analyze the resume and identify student's profile, skills, projects and experience."""
            data = analyze_resume(raw_text, gemini_service=self.gemini_service)
            return json.dumps(data)

        def tool_identify_skills() -> str:
            """Tool 3: identify_skills - Identify technical skills, programming languages, frameworks and databases."""
            data = identify_skills(raw_text, gemini_service=self.gemini_service)
            return json.dumps(data)

        def tool_identify_projects() -> str:
            """Tool 4: identify_projects - Extract project names, descriptions, technologies and candidate responsibilities."""
            data = identify_projects(raw_text, gemini_service=self.gemini_service)
            return json.dumps(data)

        tools_list = [
            tool_extract_resume,
            tool_analyze_resume,
            tool_identify_skills,
            tool_identify_projects,
        ]

        system_instruction = (
            "You are the Lead AI Resume Analysis Agent. Your responsibility is to analyze a candidate's resume "
            "by using your registered tools.\n"
            "INSTRUCTIONS:\n"
            "1. First, call `tool_extract_resume` or `tool_analyze_resume` to examine the candidate's background.\n"
            "2. If needed, call `tool_identify_skills` and `tool_identify_projects` to ensure exhaustive technical extraction.\n"
            "3. Once tools have returned all necessary data, return a final synthesis in JSON format containing:\n"
            "   name, educational_qualification, college_university, technical_skills, programming_languages, "
            "   frameworks_libraries, databases, projects, internships, work_experience, certifications.\n"
            "Never invent any experience or skills."
        )

        user_prompt = (
            "Please analyze the candidate's resume by executing the necessary tools to extract their complete profile, "
            "including education, skills, projects, internships, and work experience."
        )

        # Multi-turn tool execution loop using Google GenAI SDK
        contents = [user_prompt]
        max_turns = 6
        final_profile_data = None

        for turn in range(max_turns):
            response = self.gemini_service.client.models.generate_content(
                model=self.gemini_service.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=tools_list,
                    temperature=0.1,
                ),
            )

            # Check for tool/function calls
            function_calls = response.function_calls
            if not function_calls:
                # Agent completed without more tool calls; try parsing text
                try:
                    text = response.text.strip()
                    # Strip markdown fence if present
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                    final_profile_data = json.loads(text)
                except Exception:
                    pass
                break

            # Process function calls returned by Gemini
            # Append model turn
            contents.append(response.candidates[0].content)

            tool_responses_parts = []
            for call in function_calls:
                fn_name = call.name
                fn_args = call.args or {}
                step(fn_name, f"Executing tool {fn_name}...")

                result_output = ""
                if fn_name == "tool_extract_resume":
                    result_output = tool_extract_resume(**fn_args)
                elif fn_name == "tool_analyze_resume":
                    result_output = tool_analyze_resume(**fn_args)
                    try:
                        final_profile_data = json.loads(result_output)
                    except Exception:
                        pass
                elif fn_name == "tool_identify_skills":
                    result_output = tool_identify_skills()
                elif fn_name == "tool_identify_projects":
                    result_output = tool_identify_projects()
                else:
                    result_output = json.dumps({"error": f"Unknown tool: {fn_name}"})

                tool_responses_parts.append(
                    types.Part.from_function_response(
                        name=fn_name,
                        response={"result": result_output},
                    )
                )

            # Feed function responses back into conversation for Gemini
            contents.append(types.Content(parts=tool_responses_parts, role="tool"))

        # Fallback guarantee: if model didn't finalize direct profile json, run analyze_resume tool directly
        if not final_profile_data or not isinstance(final_profile_data, dict) or "name" not in final_profile_data:
            step("analyze_resume", "Finalizing profile synthesis...")
            final_profile_data = analyze_resume(raw_text, gemini_service=self.gemini_service)

        final_profile_data["raw_text"] = raw_text
        return final_profile_data
