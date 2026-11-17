import os
import unittest
from tools.resume_extractor import extract_resume, extract_resume_from_pdf, extract_resume_from_docx
from utils.pdf_generator import generate_interview_pdf
from models.schemas import InterviewOutput, StudentProfileCompact, InterviewQuestion

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "samples")


class TestResumeExtractionAndTools(unittest.TestCase):
    def test_extract_pdf_python_developer(self):
        pdf_path = os.path.join(SAMPLES_DIR, "python_developer.pdf")
        self.assertTrue(os.path.exists(pdf_path), "Sample PDF must exist")
        text = extract_resume(pdf_path)
        self.assertIn("Aarav Sharma", text)
        self.assertIn("FastAPI", text)
        self.assertIn("PostgreSQL", text)

    def test_extract_docx_python_developer(self):
        docx_path = os.path.join(SAMPLES_DIR, "python_developer.docx")
        self.assertTrue(os.path.exists(docx_path), "Sample DOCX must exist")
        text = extract_resume(docx_path)
        self.assertIn("Aarav Sharma", text)
        self.assertIn("FastAPI", text)

    def test_extract_fresher_no_experience(self):
        pdf_path = os.path.join(SAMPLES_DIR, "fresher_no_experience.pdf")
        self.assertTrue(os.path.exists(pdf_path), "Fresher sample PDF must exist")
        text = extract_resume(pdf_path)
        self.assertIn("Sneha Reddy", text)
        self.assertIn("Algorithmic Pathfinding Visualizer", text)

    def test_empty_resume_raises_error(self):
        with self.assertRaises(ValueError):
            extract_resume("")

    def test_generate_pdf_report(self):
        sample_data = {
            "student_profile": {
                "name": "Test Student",
                "skills": ["Python", "Docker"],
                "projects": ["Order API"],
                "experience": ["Intern at Tech Corp"],
            },
            "questions": [
                {
                    "question_id": 1,
                    "category": "Technical",
                    "question": "Explain Python GIL.",
                    "difficulty": "Medium",
                    "related_skill": "Python",
                    "reason": "Python is listed on resume.",
                    "expected_answer_points": ["Global Interpreter Lock", "Thread safety", "Multiprocessing alternative"],
                }
            ],
        }
        pdf_bytes = generate_interview_pdf(sample_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_pydantic_schema_validation(self):
        payload = {
            "student_profile": {
                "name": "Aarav Sharma",
                "skills": ["Python", "FastAPI"],
                "projects": ["Order API"],
                "experience": ["CloudWave Solutions"],
            },
            "questions": [
                {
                    "question_id": 1,
                    "category": "Technical",
                    "question": "What is FastAPI dependency injection?",
                    "difficulty": "Medium",
                    "related_skill": "FastAPI",
                    "reason": "FastAPI is prominent in candidate projects.",
                    "expected_answer_points": ["Depends() syntax", "Reusability", "Yielding resources"],
                }
            ],
        }
        validated = InterviewOutput(**payload)
        self.assertEqual(validated.student_profile.name, "Aarav Sharma")
        self.assertEqual(len(validated.questions), 1)


if __name__ == "__main__":
    unittest.main()
