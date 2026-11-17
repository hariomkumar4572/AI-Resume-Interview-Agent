# AI Resume-Based Interview Question Generator Agent

An autonomous AI Agent built with Python and the official Google GenAI SDK (`google-genai`) that reads student resumes (in PDF or DOCX format), extracts profile information without hallucination, and generates personalized, structured interview questions across five core categories using **Gemini Function Calling**.

---

## 🌟 Key Features

1. **Multi-Format Resume Ingestion**:
   - High-fidelity PDF extraction using `PyMuPDF`.
   - DOCX paragraph and table extraction using `python-docx`.
   - Robust error handling for corrupt, empty, or unsupported files.

2. **Autonomous AI Agents & Genuine Gemini Function Calling**:
   - **ResumeAgent**: Executes function calling with `tool_extract_resume`, `tool_analyze_resume`, `tool_identify_skills`, and `tool_identify_projects` to build the candidate profile.
   - **InterviewAgent**: Coordinates `tool_generate_interview_questions` and `tool_validate_questions` to assemble personalized interview packages.
   - Non-simulated tool calling: The Gemini model explicitly returns function call declarations, the agent dispatches execution in Python, and returns structured function responses to the model.

3. **Strict Resume Grounding (No Hallucination)**:
   - Evaluates only technologies, projects, and experiences explicitly present in the resume.
   - Gracefully handles **Fresher Profiles**: If no internships or work experiences are listed, it marks them as empty/None and pivots questions toward personal projects and foundational computer science rather than fabricating roles.

4. **Structured Question Categories**:
   - **Technical Questions**: Tailored to declared languages, frameworks, and databases.
   - **Project-Based Questions**: Architectural decisions, challenges, and implementation details.
   - **Internship & Experience Questions**: Grounded in listed company roles (or reallocated if fresher).
   - **HR Questions**: Behavioral questions rooted in candidate background.
   - **Coding Questions**: Data structures, algorithmic thinking, and language-specific problems.

5. **Configurable Difficulty & Quantity**:
   - Calibrate questions across **Easy**, **Medium**, and **Hard**.
   - Customize question counts (5 to 30) with proportional distribution.

6. **Interactive Streamlit Web Interface**:
   - Upload PDF/DOCX resumes or choose from 6 built-in test profiles.
   - Real-time agent tool invocation tracking.
   - Category filtering and expected answer rubrics.
   - **PDF Export**: Generate downloadable, print-ready PDF evaluation sheets.
   - **JSON Export**: Export structured JSON conforming strictly to schema standards.

---

## 🏗️ Architecture & Function Calling Flow

```
                           +----------------------+
                           |   Student Resume     |
                           |   (PDF or DOCX)      |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           |  extract_resume Tool |
                           +----------+-----------+
                                      |
                                      v
       +--------------------------------------------------------------+
       |                         ResumeAgent                          |
       |                                                              |
       |  +--------------------------------------------------------+  |
       |  |  Gemini Model (Function Calling Loop)                  |  |
       |  |  Tools:                                                |  |
       |  |   • tool_extract_resume                                |  |
       |  |   • tool_analyze_resume                                |  |
       |  |   • tool_identify_skills                               |  |
       |  |   • tool_identify_projects                             |  |
       |  +--------------------------------------------------------+  |
       +------------------------------+-------------------------------+
                                      |
                                      v
       +--------------------------------------------------------------+
       |                       InterviewAgent                         |
       |                                                              |
       |  +--------------------------------------------------------+  |
       |  |  Gemini Model (Function Calling Loop)                  |  |
       |  |  Tools:                                                |  |
       |  |   • tool_generate_interview_questions                  |  |
       |  |   • tool_validate_questions                            |  |
       |  +--------------------------------------------------------+  |
       +------------------------------+-------------------------------+
                                      |
                                      v
                     +----------------------------------+
                     |        Structured Output         |
                     |  - Streamlit UI Dashboard        |
                     |  - PDF Interview Evaluation Sheet|
                     |  - Standard JSON Export          |
                     +----------------------------------+
```

---

## 🛠️ Project Structure

```
ai-resume-interview-agent/
│
├── main.py                     # Entry point to launch Streamlit application
├── app.py                      # Interactive Streamlit UI and dashboard
├── requirements.txt            # Project dependencies
├── .env                        # Local environment variables (API Key)
├── .env.example                # Example configuration template
├── README.md                   # Documentation and execution guide
│
├── agents/                     # Autonomous AI Agents
│   ├── __init__.py
│   ├── resume_agent.py         # Multi-turn tool-calling agent for resume analysis
│   └── interview_agent.py      # Multi-turn tool-calling agent for question synthesis
│
├── tools/                      # Core agent tools
│   ├── __init__.py
│   ├── resume_extractor.py     # Tool 1: extract_resume (PDF / DOCX)
│   ├── resume_analyzer.py      # Tool 2: analyze_resume (Profile extraction)
│   ├── skill_identifier.py     # Tool 3: identify_skills (Tech stack extraction)
│   ├── project_identifier.py   # Tool 4: identify_projects (Projects extraction)
│   ├── question_generator.py   # Tool 5: generate_interview_questions
│   └── question_validator.py   # Tool 6: validate_questions (Deduplication & QA)
│
├── services/                   # Backend services
│   ├── __init__.py
│   └── gemini_service.py       # Official google-genai client wrapper
│
├── models/                     # Data schemas
│   ├── __init__.py
│   └── schemas.py              # Pydantic schemas for structured outputs
│
├── utils/                      # Helper utilities
│   ├── __init__.py
│   └── pdf_generator.py        # ReportLab PDF question sheet generator
│
├── samples/                    # Built-in sample resumes (PDF & DOCX)
│   ├── generate_samples.py     # Script to generate sample resumes
│   ├── python_developer.pdf
│   ├── java_developer.pdf
│   ├── web_developer.pdf
│   ├── data_analyst.pdf
│   ├── ai_ml_engineer.pdf
│   ├── fresher_no_experience.pdf
│   └── sample_resume.pdf
│
└── tests/                      # Automated test suite
    ├── test_core.py            # Unit tests for text extraction, PDF generation & schemas
    └── test_agent.py           # Unit tests for agent workflows and fresher handling
```

---

## 📋 Installation & Setup

### Prerequisites
- Python 3.10+
- Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone the repository and navigate into the folder:
```bash
cd AI-Resume-Interview-Agent
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure the Gemini API Key:
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```
*(You can also configure or change the API key directly in the Streamlit web sidebar).*

---

## 🚀 Running the Application

### Launch Streamlit Interface:
```bash
python main.py
```
or directly:
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Running the Tests

To verify resume extraction, deduplication, schema validation, and fresher workflows:
```bash
python -m unittest discover tests
```

---

## 📑 Structured JSON Output Schema

The agent returns JSON conforming directly to:

```json
{
  "student_profile": {
    "name": "Aarav Sharma",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "projects": ["High-Throughput E-Commerce Order Processing API"],
    "experience": ["Backend Engineering Intern at CloudWave Solutions"]
  },
  "questions": [
    {
      "question_id": 1,
      "category": "Technical",
      "question": "How did you implement Redis-based distributed locking in your order processing API to prevent race conditions during flash sales?",
      "difficulty": "Medium",
      "related_skill": "Redis",
      "reason": "Resume mentions implementing Redis-based distributed locking to avoid inventory overselling.",
      "expected_answer_points": [
        "SETNX or Redlock algorithm usage",
        "Key TTL and expiration to prevent deadlocks",
        "Handling network partitions and release safety with unique tokens"
      ]
    }
  ]
}
```
