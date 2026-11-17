import os
import json
import streamlit as st
from dotenv import load_dotenv

from services.gemini_service import GeminiService
from agents.resume_agent import ResumeAgent
from agents.interview_agent import InterviewAgent
from tools.resume_extractor import extract_resume
from utils.pdf_generator import generate_interview_pdf

# Page configuration
st.set_page_config(
    page_title="AI Resume Interview Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables
load_dotenv()

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .badge-technical { background-color: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    .badge-project { background-color: #fef3c7; color: #92400e; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    .badge-experience { background-color: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    .badge-hr { background-color: #f3e8ff; color: #6b21a8; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    .badge-coding { background-color: #ffedd5; color: #9a3412; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    .badge-diff { background-color: #f1f5f9; color: #334155; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "gemini_service" not in st.session_state:
    st.session_state.gemini_service = GeminiService()
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "student_profile" not in st.session_state:
    st.session_state.student_profile = None
if "interview_package" not in st.session_state:
    st.session_state.interview_package = None
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Agent Settings")
    st.markdown("Configure Gemini API credentials and interview generation parameters.")

    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=env_api_key,
        type="password",
        help="Enter your Google AI Studio Gemini API Key. It is kept secure in memory.",
    )

    model_options = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-2.5-pro"]
    env_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    default_idx = model_options.index(env_model) if env_model in model_options else 0
    selected_model = st.selectbox("Gemini Model", options=model_options, index=default_idx)

    if api_key_input:
        st.session_state.gemini_service.set_api_key(api_key_input)
        st.session_state.gemini_service.model_name = selected_model
        st.success("API Key configured", icon="✅")
    else:
        st.warning("Please provide a Gemini API Key to run agent tools.", icon="⚠️")

    st.markdown("---")
    st.subheader("🎯 Interview Customization")
    selected_difficulty = st.selectbox(
        "Question Difficulty",
        options=["Easy", "Medium", "Hard"],
        index=1,
        help="Calibrate the complexity, architectural depth, and internal workings tested.",
    )

    num_questions = st.slider(
        "Total Questions",
        min_value=5,
        max_value=30,
        value=20,
        step=1,
        help="Default is 20: 5 Technical, 5 Project-Based, 4 Coding, 3 HR, 3 Experience.",
    )

    st.caption("Default target distribution:")
    st.caption("• 5 Technical | 5 Project-Based")
    st.caption("• 4 Coding | 3 HR | 3 Experience")

    st.markdown("---")
    st.subheader("📁 Sample Resumes")
    sample_resumes = {
        "None (Upload my own)": None,
        "Python Developer": "samples/python_developer.pdf",
        "Java Backend Developer": "samples/java_developer.pdf",
        "Full Stack Web Developer": "samples/web_developer.pdf",
        "Data Analyst": "samples/data_analyst.pdf",
        "AI/ML Engineer": "samples/ai_ml_engineer.pdf",
        "Fresher (No Experience)": "samples/fresher_no_experience.pdf",
    }
    selected_sample = st.selectbox("Load Sample Resume", options=list(sample_resumes.keys()))


# Main View Header
st.markdown('<div class="main-header">💼 AI Resume Interview Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Autonomous Agentic Interview Question Generator powered by Google Gemini Function Calling</div>',
    unsafe_allow_html=True,
)

# Step 1: Resume Upload & Extraction
st.markdown("### 1. Upload Student Resume")
col1, col2 = st.columns([2, 1])

uploaded_file = None
with col1:
    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX Resume",
        type=["pdf", "docx"],
        help="Upload candidate resume in PDF or DOCX format. Scanned non-text images are not supported.",
    )

with col2:
    st.markdown("#### Sample Resume Loader")
    if selected_sample and selected_sample != "None (Upload my own)":
        sample_path = sample_resumes[selected_sample]
        if os.path.exists(sample_path):
            st.info(f"Loaded: `{os.path.basename(sample_path)}`")
            if st.button("Use Selected Sample", key="use_sample_btn"):
                try:
                    ext_text = extract_resume(sample_path)
                    st.session_state.extracted_text = ext_text
                    st.session_state.student_profile = None
                    st.session_state.interview_package = None
                    st.session_state.agent_logs = []
                    st.success("Loaded sample resume text successfully!")
                except Exception as e:
                    st.error(f"Error loading sample: {e}")

# Process uploaded file if user uploaded one
if uploaded_file is not None:
    try:
        # Determine file type from filename or MIME
        ftype = "pdf" if uploaded_file.name.lower().endswith(".pdf") else "docx"
        # Always obtain fresh bytes via getvalue() rather than read() to avoid consumed stream pointers
        content_bytes = uploaded_file.getvalue()
        extracted_text = extract_resume(content_bytes, file_type=ftype)
        st.session_state.extracted_text = extracted_text
        st.success(f"Resume `{uploaded_file.name}` extracted successfully! ({len(extracted_text)} characters)", icon="✅")
    except Exception as e:
        st.error(f"Error extracting resume: {str(e)}")

# Display Extracted Resume Text for verification
if st.session_state.extracted_text:
    with st.expander("📄 View Extracted Resume Text (Verification)", expanded=False):
        st.text_area("Extracted Text", st.session_state.extracted_text, height=220, disabled=True)

st.markdown("---")

# Step 2: Agentic Resume Analysis
st.markdown("### 2. Autonomous Resume Analysis")

col_an1, col_an2 = st.columns([1, 3])
with col_an1:
    analyze_btn = st.button("🔍 Analyze Resume with Agent", type="primary", use_container_width=True)

if analyze_btn:
    if not st.session_state.extracted_text:
        st.warning("Please upload a resume or select a sample resume first.")
    elif not st.session_state.gemini_service.is_configured():
        st.error("Please configure your Gemini API Key in the sidebar.")
    else:
        st.session_state.agent_logs = []
        progress_placeholder = st.empty()
        log_placeholder = st.empty()

        def agent_callback(tool_name: str, desc: str):
            msg = f"🔧 **Tool Invoked**: `{tool_name}` — {desc}"
            st.session_state.agent_logs.append(msg)
            progress_placeholder.info(f"AI Agent executing: **{tool_name}**...")
            with log_placeholder.container():
                for l in st.session_state.agent_logs:
                    st.write(l)

        try:
            resume_agent = ResumeAgent(gemini_service=st.session_state.gemini_service)
            profile_result = resume_agent.run_analysis_cycle(
                resume_source=st.session_state.extracted_text,
                file_type="text",
                on_step_callback=agent_callback,
            )
            st.session_state.student_profile = profile_result
            progress_placeholder.success("Resume analysis completed successfully by Agent!")
        except Exception as e:
            progress_placeholder.error(f"Analysis failed: {str(e)}")

# Display Analyzed Profile
if st.session_state.student_profile:
    prof = st.session_state.student_profile
    st.markdown("#### Extracted Profile Information")

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.markdown(f"**Candidate Name:** {prof.get('name', 'Not Provided')}")
        st.markdown(f"**Qualification:** {prof.get('educational_qualification', 'Not Provided')}")
        st.markdown(f"**College / University:** {prof.get('college_university', 'Not Provided')}")
        st.markdown(f"**Programming Languages:** {', '.join(prof.get('programming_languages', [])) or 'Not Provided'}")
        st.markdown(f"**Frameworks & Libraries:** {', '.join(prof.get('frameworks_libraries', [])) or 'Not Provided'}")

    with pcol2:
        st.markdown(f"**Databases:** {', '.join(prof.get('databases', [])) or 'Not Provided'}")
        st.markdown(f"**Technical Skills:** {', '.join(prof.get('technical_skills', [])) or 'Not Provided'}")
        st.markdown(f"**Certifications:** {', '.join(prof.get('certifications', [])) or 'Not Provided'}")
        internships = prof.get("internships", [])
        work_exp = prof.get("work_experience", [])
        if internships or work_exp:
            all_exp = [f"{e.get('role')} at {e.get('company')}" for e in (internships + work_exp) if isinstance(e, dict)]
            st.markdown(f"**Experience / Internships:** {', '.join(all_exp)}")
        else:
            st.markdown("**Experience / Internships:** *None Listed (Fresher Profile)*")

    # Projects Display
    projects = prof.get("projects", [])
    if projects:
        st.markdown("**Identified Projects:**")
        for p in projects:
            if isinstance(p, dict):
                title = p.get("title", "Project")
                tech = ", ".join(p.get("technologies", []))
                desc = p.get("description", "")
                st.caption(f"• **{title}** [{tech}]: {desc}")

st.markdown("---")

# Step 3: Interview Question Generation
st.markdown("### 3. Generate Personalized Interview Questions")

col_q1, col_q2 = st.columns([1, 3])
with col_q1:
    gen_btn = st.button("🚀 Generate Interview Questions", type="primary", use_container_width=True)

if gen_btn:
    if not st.session_state.student_profile:
        st.warning("Please analyze the resume first before generating questions.")
    elif not st.session_state.gemini_service.is_configured():
        st.error("Please configure your Gemini API Key in the sidebar.")
    else:
        q_progress = st.empty()
        q_logs = []

        def interview_callback(tool_name: str, desc: str):
            msg = f"⚙️ **Agent Tool**: `{tool_name}` — {desc}"
            q_logs.append(msg)
            q_progress.info(f"AI Agent invoking: **{tool_name}**...")

        try:
            interview_agent = InterviewAgent(gemini_service=st.session_state.gemini_service)
            output_pkg = interview_agent.generate_interview_package(
                profile_data=st.session_state.student_profile,
                difficulty=selected_difficulty,
                num_questions=num_questions,
                on_step_callback=interview_callback,
            )
            st.session_state.interview_package = output_pkg
            q_progress.success("Personalized questions successfully generated and validated by Agent!")
        except Exception as e:
            q_progress.error(f"Question generation failed: {str(e)}")

# Display Generated Questions
if st.session_state.interview_package:
    pkg = st.session_state.interview_package
    questions = pkg.get("questions", [])

    st.markdown(f"#### 🎯 Personalized Interview Questions ({len(questions)} Generated)")

    # Category Filter
    categories = ["All"] + sorted(list(set(q.get("category", "General") for q in questions)))
    filter_col1, filter_col2 = st.columns([2, 2])
    with filter_col1:
        selected_cat = st.selectbox("Filter by Category", options=categories)

    filtered_questions = [
        q for q in questions if selected_cat == "All" or q.get("category") == selected_cat
    ]

    badge_map = {
        "Technical": "badge-technical",
        "Project-Based": "badge-project",
        "Internship/Experience": "badge-experience",
        "HR": "badge-hr",
        "Coding": "badge-coding",
    }

    for q in filtered_questions:
        q_id = q.get("question_id", 1)
        cat = q.get("category", "General")
        diff = q.get("difficulty", "Medium")
        q_text = q.get("question", "")
        skill = q.get("related_skill", "")
        reason = q.get("reason", "")
        answer_pts = q.get("expected_answer_points", [])

        badge_cls = badge_map.get(cat, "badge-technical")

        with st.container():
            st.markdown(
                f"""
                <div class="card">
                    <span class="{badge_cls}">{cat}</span>
                    <span class="badge-diff">{diff}</span>
                    <span style="font-size: 0.85rem; color: #475569; margin-left: 8px;"><b>Target Skill/Topic:</b> {skill}</span>
                    <div style="font-size: 1.05rem; font-weight: 600; color: #0f172a; margin-top: 8px; margin-bottom: 6px;">
                        Q{q_id}. {q_text}
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b; font-style: italic; margin-bottom: 8px;">
                        <b>Resume Reference:</b> {reason}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if answer_pts:
                with st.expander(f"💡 Expected Answer Points for Q{q_id}", expanded=False):
                    for pt in answer_pts:
                        st.markdown(f"- {pt}")

    st.markdown("---")

    # Step 4: Export Options
    st.markdown("### 4. Export & Download Options")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        st.markdown("#### 📥 Download PDF Evaluation Sheet")
        try:
            pdf_bytes = generate_interview_pdf(pkg)
            cand_name = pkg.get("student_profile", {}).get("name", "Candidate").replace(" ", "_")
            st.download_button(
                label="📄 Download Interview Questions PDF",
                data=pdf_bytes,
                file_name=f"Interview_Questions_{cand_name}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

    with exp_col2:
        st.markdown("#### 📋 Download Structured JSON")
        json_str = json.dumps(pkg, indent=2)
        st.download_button(
            label="💾 Download Structured JSON",
            data=json_str,
            file_name=f"interview_questions_{cand_name}.json",
            mime="application/json",
            use_container_width=True,
        )

    # View Raw JSON
    with st.expander("🔍 View Structured JSON Output", expanded=False):
        st.json(pkg)
