import unittest
from unittest.mock import MagicMock
from tools.question_validator import validate_questions
from agents.interview_agent import InterviewAgent


class TestAgentWorkflows(unittest.TestCase):
    def test_fresher_experience_handling(self):
        """Verify that a candidate with no internships or experience gets marked correctly."""
        fresher_profile = {
            "name": "Sneha Reddy",
            "educational_qualification": "B.Tech CSE",
            "college_university": "JNTU",
            "programming_languages": ["Python", "Java"],
            "frameworks_libraries": ["Flask", "Streamlit"],
            "databases": ["SQLite"],
            "technical_skills": ["Data Structures", "Algorithms"],
            "projects": [
                {
                    "title": "Academic Tracker",
                    "description": "Flask app for GPA calculation",
                    "technologies": ["Flask", "SQLite"],
                    "responsibilities": ["Full development"],
                }
            ],
            "internships": [],
            "work_experience": [],
            "certifications": ["HackerRank"],
        }

        # Mock gemini service with simulated function calling
        mock_gemini = MagicMock()
        mock_gemini.is_configured.return_value = True
        mock_gemini.model_name = "gemini-3.8-flash"

        # Mock generate_content response on service when tools call service.generate_content
        mock_tool_resp = MagicMock()
        mock_tool_resp.text = '{"questions": [{"question_id": 1, "category": "Technical", "question": "What is Python?", "difficulty": "Medium", "related_skill": "Python", "reason": "Mentioned in resume", "expected_answer_points": ["Interpreted language"]}]}'
        mock_gemini.generate_content.return_value = mock_tool_resp

        # Mock client generate_content response simulating agent loop function calling cycle
        mock_resp1 = MagicMock()
        mock_call1 = MagicMock()
        mock_call1.name = "tool_generate_interview_questions"
        mock_call1.args = {"diff_level": "Medium", "total_count": 5}
        mock_resp1.function_calls = [mock_call1]
        mock_resp1.candidates = [MagicMock()]

        mock_resp2 = MagicMock()
        mock_call2 = MagicMock()
        mock_call2.name = "tool_validate_questions"
        mock_call2.args = {
            "raw_questions_json": '{"questions": [{"question_id": 1, "category": "Technical", "question": "What is Python?", "difficulty": "Medium", "related_skill": "Python", "reason": "Mentioned in resume", "expected_answer_points": ["Interpreted language"]}]}'
        }
        mock_resp2.function_calls = [mock_call2]
        mock_resp2.candidates = [MagicMock()]

        mock_resp3 = MagicMock()
        mock_resp3.function_calls = []  # Finished tool calling

        mock_gemini.client.models.generate_content.side_effect = [
            mock_resp1,
            mock_resp2,
            mock_resp3,
        ]

        agent = InterviewAgent(gemini_service=mock_gemini)
        
        output = agent.generate_interview_package(
            profile_data=fresher_profile,
            difficulty="Medium",
            num_questions=5,
        )

        self.assertEqual(output["student_profile"]["name"], "Sneha Reddy")
        # Fresher has no experience - ensure experience list is strictly empty
        self.assertEqual(len(output["student_profile"]["experience"]), 0)
        self.assertIn("Academic Tracker", output["student_profile"]["projects"])
        self.assertIn("Python", output["student_profile"]["skills"])
        self.assertTrue(len(output["questions"]) >= 1)

    def test_question_validator_deduplication(self):
        """Test local fallback deduplication in validate_questions."""
        dup_questions = [
            {
                "question_id": 1,
                "category": "Technical",
                "question": "What is Python GIL?",
                "difficulty": "Medium",
                "related_skill": "Python",
                "reason": "Resume",
                "expected_answer_points": ["Point 1"],
            },
            {
                "question_id": 2,
                "category": "Technical",
                "question": "What is Python GIL?",  # Duplicate
                "difficulty": "Medium",
                "related_skill": "Python",
                "reason": "Resume",
                "expected_answer_points": ["Point 1"],
            },
            {
                "question_id": 3,
                "category": "Coding",
                "question": "Implement a binary search in Python.",
                "difficulty": "Medium",
                "related_skill": "Python",
                "reason": "Resume",
                "expected_answer_points": ["O(log n) time", "Pointers"],
            },
        ]
        res = validate_questions(dup_questions, profile_data={}, gemini_service=None)
        self.assertTrue(res["is_valid"])
        val_q = res["validated_questions"]
        self.assertEqual(len(val_q), 2)
        self.assertEqual(val_q[0]["question_id"], 1)
        self.assertEqual(val_q[1]["question_id"], 2)


if __name__ == "__main__":
    unittest.main()
