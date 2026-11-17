"""
Script to generate sample resume documents (PDF and DOCX) across 6 candidate profiles:
1. Python Developer
2. Java Developer
3. Web Developer
4. Data Analyst
5. AI/ML Engineer
6. Fresher with no internship experience
"""

import os
import docx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

PROFILES = [
    {
        "filename_base": "python_developer",
        "name": "Aarav Sharma",
        "title": "Python Developer",
        "email": "aarav.sharma@example.com | +91 98765 43210 | Bengaluru, India",
        "education": "B.Tech in Computer Science and Engineering, National Institute of Technology (2020 - 2024), CGPA: 8.7/10",
        "skills": {
            "Languages": "Python, SQL, Bash",
            "Frameworks": "FastAPI, Django, Flask, Celery, Pytest",
            "Databases": "PostgreSQL, Redis, MongoDB",
            "Tools & Concepts": "Docker, Git, CI/CD, REST APIs, Microservices, Asynchronous Programming",
        },
        "projects": [
            {
                "title": "High-Throughput E-Commerce Order Processing API",
                "tech": "FastAPI, PostgreSQL, Redis, Celery, Docker",
                "points": [
                    "Designed and deployed asynchronous RESTful microservices handling 2,000+ orders per minute.",
                    "Implemented Redis-based distributed locking to prevent inventory overselling during flash sales.",
                    "Optimized PostgreSQL query latency by 45% using composite indexes and connection pooling.",
                ],
            },
            {
                "title": "Automated Web Scraping and ETL Pipeline",
                "tech": "Python, BeautifulSoup, Pandas, PostgreSQL, Airflow",
                "points": [
                    "Built resilient web scrapers extracting daily product pricing data across 10+ e-commerce platforms.",
                    "Orchestrated daily ETL workflows in Apache Airflow with automated failure alerting.",
                ],
            },
        ],
        "experience": [
            {
                "role": "Backend Engineering Intern",
                "company": "CloudWave Solutions",
                "duration": "Jan 2024 - Jun 2024",
                "points": [
                    "Developed backend endpoints using Django Rest Framework and PostgreSQL.",
                    "Authored automated unit and integration tests using Pytest, boosting code coverage to 92%.",
                    "Integrated JWT-based authentication and role-based access control.",
                ],
            }
        ],
        "certifications": [
            "AWS Certified Solutions Architect - Associate",
            "Python Institute PCAP - Certified Associate in Python Programming",
        ],
    },
    {
        "filename_base": "java_developer",
        "name": "Priya Patel",
        "title": "Java Backend Developer",
        "email": "priya.patel@example.com | +91 98123 45678 | Pune, India",
        "education": "B.E. in Information Technology, Pune Institute of Computer Technology (2019 - 2023), CGPA: 8.9/10",
        "skills": {
            "Languages": "Java (Java 17/21), SQL",
            "Frameworks": "Spring Boot, Spring Cloud, Spring Data JPA, Hibernate, JUnit 5, Mockito",
            "Databases": "MySQL, PostgreSQL, Oracle DB",
            "Tools & Concepts": "Kafka, Docker, Kubernetes, Maven, Design Patterns, Microservices",
        },
        "projects": [
            {
                "title": "FinTech Core Banking Transaction Engine",
                "tech": "Java 17, Spring Boot, Apache Kafka, MySQL, Docker",
                "points": [
                    "Engineered an event-driven payment ledger processing over 50,000 daily financial transactions.",
                    "Integrated Apache Kafka for asynchronous transaction auditing and fraud alert notifications.",
                    "Applied Circuit Breaker pattern with Resilience4j to preserve 99.99% service uptime.",
                ],
            }
        ],
        "experience": [
            {
                "role": "Java Developer Intern",
                "company": "Infosys Finacle Labs",
                "duration": "Jul 2023 - Dec 2023",
                "points": [
                    "Constructed REST APIs for multi-currency currency exchange rates using Spring Boot.",
                    "Migrated legacy monolithic SOAP services into clean REST microservices.",
                ],
            }
        ],
        "certifications": [
            "Oracle Certified Professional: Java SE 17 Developer",
        ],
    },
    {
        "filename_base": "web_developer",
        "name": "Rohan Verma",
        "title": "Full Stack Web Developer",
        "email": "rohan.verma@example.com | +91 97654 32109 | Delhi, India",
        "education": "B.Tech in Computer Science, Delhi Technological University (2020 - 2024), CGPA: 8.4/10",
        "skills": {
            "Languages": "JavaScript (ES6+), TypeScript, HTML5, CSS3, Python",
            "Frameworks": "React, Next.js, Node.js, Express.js, Tailwind CSS, Redux Toolkit",
            "Databases": "MongoDB, PostgreSQL, Supabase",
            "Tools & Concepts": "Git, Webpack, Vercel, RESTful APIs, GraphQL, Responsive Design",
        },
        "projects": [
            {
                "title": "Collaborative Real-time Kanban Workspace",
                "tech": "Next.js, TypeScript, Tailwind CSS, Node.js, Socket.io, MongoDB",
                "points": [
                    "Built an agile project board with drag-and-drop task workflows and real-time live updates via WebSockets.",
                    "Implemented server-side rendering (SSR) and dynamic image optimization, achieving 98+ Google Lighthouse score.",
                ],
            }
        ],
        "experience": [
            {
                "role": "Frontend Web Intern",
                "company": "PixelCraft Studios",
                "duration": "May 2023 - Aug 2023",
                "points": [
                    "Engineered responsive UI components using React, TypeScript, and Tailwind CSS.",
                    "Improved web vitals by optimizing bundle sizes and implementing code splitting.",
                ],
            }
        ],
        "certifications": ["Meta Front-End Developer Professional Certificate"],
    },
    {
        "filename_base": "data_analyst",
        "name": "Neha Kulkarni",
        "title": "Data Analyst",
        "email": "neha.kulkarni@example.com | +91 99887 76655 | Hyderabad, India",
        "education": "B.Sc in Statistics & Data Science, St. Xavier's College (2020 - 2023), CGPA: 9.1/10",
        "skills": {
            "Languages": "Python, SQL, R",
            "Libraries": "Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn",
            "Databases & Warehouses": "PostgreSQL, BigQuery, Snowflake",
            "BI Tools & Concepts": "Tableau, Power BI, Excel (Advanced), Statistical Modeling, Hypothesis Testing",
        },
        "projects": [
            {
                "title": "Customer Churn Prediction and Cohort Analysis",
                "tech": "Python, Pandas, Scikit-learn, Tableau, BigQuery",
                "points": [
                    "Analyzed telecom customer dataset of 100,000+ accounts to identify key drivers of customer attrition.",
                    "Built classification models achieving 86% ROC-AUC score, uncovering actionable retention strategies.",
                    "Created interactive executive dashboards in Tableau demonstrating projected revenue impact.",
                ],
            }
        ],
        "experience": [
            {
                "role": "Data Analyst Intern",
                "company": "MarketPulse Analytics",
                "duration": "Jan 2023 - Jun 2023",
                "points": [
                    "Wrote complex SQL queries involving multi-table window functions and aggregations.",
                    "Automated weekly stakeholder reports, cutting manual processing time from 8 hours to 15 minutes.",
                ],
            }
        ],
        "certifications": ["Google Data Analytics Professional Certificate"],
    },
    {
        "filename_base": "ai_ml_engineer",
        "name": "Vikram Sen",
        "title": "AI/ML Engineer",
        "email": "vikram.sen@example.com | +91 98223 34455 | Bengaluru, India",
        "education": "M.Tech in Artificial Intelligence, IIT Madras (2022 - 2024), CGPA: 9.3/10",
        "skills": {
            "Languages": "Python, C++, CUDA",
            "Frameworks": "PyTorch, Hugging Face Transformers, LangChain, TensorFlow, OpenCV",
            "Databases & Vector DBs": "Qdrant, ChromaDB, PostgreSQL (pgvector)",
            "ML Concepts": "RAG, LLM Fine-Tuning, LoRA, Computer Vision, Model Quantization, ONNX",
        },
        "projects": [
            {
                "title": "Domain-Specific Multimodal RAG Assistant",
                "tech": "PyTorch, Hugging Face, Qdrant, FastAPI, Docker",
                "points": [
                    "Developed a Retrieval-Augmented Generation system over 50,000 technical engineering schematics.",
                    "Fine-tuned Mistral-7B using LoRA for domain adaptation, improving retrieval faithfulness by 38%.",
                    "Deployed low-latency inference endpoints utilizing ONNX Runtime and vLLM.",
                ],
            }
        ],
        "experience": [
            {
                "role": "Machine Learning Research Intern",
                "company": "DeepMind Research Collaborations Lab",
                "duration": "Jun 2023 - Dec 2023",
                "points": [
                    "Researched parameter-efficient fine-tuning methods for vision-language models.",
                    "Implemented custom PyTorch data loading pipelines accelerating GPU utilization from 65% to 94%.",
                ],
            }
        ],
        "certifications": ["DeepLearning.AI Deep Learning Specialization"],
    },
    {
        "filename_base": "fresher_no_experience",
        "name": "Sneha Reddy",
        "title": "Computer Science Graduate / Aspiring Software Engineer",
        "email": "sneha.reddy@example.com | +91 91234 56789 | Hyderabad, India",
        "education": "B.Tech in Computer Science and Engineering, Jawaharlal Nehru Technological University (2021 - 2025), CGPA: 8.6/10",
        "skills": {
            "Languages": "Python, Java, C, SQL",
            "Frameworks": "Flask, Streamlit, SQLite",
            "Core Concepts": "Data Structures & Algorithms, Object-Oriented Programming (OOP), Database Management, Operating Systems, Computer Networks",
            "Tools": "Git, GitHub, VS Code, Linux",
        },
        "projects": [
            {
                "title": "Student Academic Performance Tracker",
                "tech": "Python, Flask, SQLite, HTML/CSS",
                "points": [
                    "Developed a full web application for tracking semester attendance, test grades, and GPA calculations.",
                    "Implemented SQLite relational database schema with referential integrity and user authentication.",
                    "Created visual analytics charts using Chart.js to help students identify weak subject areas.",
                ],
            },
            {
                "title": "Algorithmic Pathfinding Visualizer",
                "tech": "Python, Pygame",
                "points": [
                    "Built an interactive visualizer for Dijkstra's, A* Search, and Breadth-First Search algorithms.",
                    "Implemented custom grid maze generators with real-time heuristic cost adjustments.",
                ],
            },
        ],
        "experience": [],  # Explicitly empty: FRESHER WITH NO INTERNSHIP EXPERIENCE
        "certifications": [
            "HackerRank Problem Solving (Intermediate) Certificate",
            "Python for Everybody Specialization - Coursera",
        ],
    },
]


def create_pdf(profile: dict, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle("Hdr", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#0f172a"))
    sub_style = ParagraphStyle("Sub", fontName="Helvetica", fontSize=9.5, leading=13, textColor=colors.HexColor("#475569"))
    sec_style = ParagraphStyle("Sec", fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#1e3a8a"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle("Bdy", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"))
    bullet_style = ParagraphStyle("Blt", fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#334155"), leftIndent=12)

    story = []
    story.append(Paragraph(profile["name"], header_style))
    story.append(Paragraph(f"<b>{profile['title']}</b> | {profile['email']}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563eb"), spaceAfter=8))

    # Education
    story.append(Paragraph("EDUCATION", sec_style))
    story.append(Paragraph(profile["education"], body_style))
    story.append(Spacer(1, 4))

    # Technical Skills
    story.append(Paragraph("TECHNICAL SKILLS", sec_style))
    for k, v in profile["skills"].items():
        story.append(Paragraph(f"• <b>{k}:</b> {v}", bullet_style))
    story.append(Spacer(1, 4))

    # Projects
    story.append(Paragraph("PROJECTS", sec_style))
    for proj in profile["projects"]:
        story.append(Paragraph(f"<b>{proj['title']}</b> ({proj['tech']})", body_style))
        for pt in proj["points"]:
            story.append(Paragraph(f"• {pt}", bullet_style))
        story.append(Spacer(1, 3))

    # Experience
    if profile.get("experience"):
        story.append(Paragraph("EXPERIENCE & INTERNSHIPS", sec_style))
        for exp in profile["experience"]:
            story.append(Paragraph(f"<b>{exp['role']}</b> - {exp['company']} ({exp.get('duration', '')})", body_style))
            for pt in exp["points"]:
                story.append(Paragraph(f"• {pt}", bullet_style))
            story.append(Spacer(1, 3))

    # Certifications
    if profile.get("certifications"):
        story.append(Paragraph("CERTIFICATIONS", sec_style))
        for cert in profile["certifications"]:
            story.append(Paragraph(f"• {cert}", bullet_style))

    doc.build(story)


def create_docx(profile: dict, output_path: str):
    doc = docx.Document()
    
    # Header
    doc.add_heading(profile["name"], level=0)
    p = doc.add_paragraph()
    p.add_run(f"{profile['title']} | {profile['email']}").italic = True

    # Education
    doc.add_heading("Education", level=1)
    doc.add_paragraph(profile["education"])

    # Skills
    doc.add_heading("Technical Skills", level=1)
    for k, v in profile["skills"].items():
        doc.add_paragraph(f"{k}: {v}", style="List Bullet")

    # Projects
    doc.add_heading("Projects", level=1)
    for proj in profile["projects"]:
        p_proj = doc.add_paragraph()
        run = p_proj.add_run(f"{proj['title']} ({proj['tech']})")
        run.bold = True
        for pt in proj["points"]:
            doc.add_paragraph(pt, style="List Bullet")

    # Experience
    if profile.get("experience"):
        doc.add_heading("Experience & Internships", level=1)
        for exp in profile["experience"]:
            p_exp = doc.add_paragraph()
            run = p_exp.add_run(f"{exp['role']} - {exp['company']} ({exp.get('duration', '')})")
            run.bold = True
            for pt in exp["points"]:
                doc.add_paragraph(pt, style="List Bullet")

    # Certifications
    if profile.get("certifications"):
        doc.add_heading("Certifications", level=1)
        for cert in profile["certifications"]:
            doc.add_paragraph(cert, style="List Bullet")

    doc.save(output_path)


def main():
    print("Generating sample resumes...")
    for prof in PROFILES:
        pdf_path = os.path.join(SAMPLES_DIR, f"{prof['filename_base']}.pdf")
        docx_path = os.path.join(SAMPLES_DIR, f"{prof['filename_base']}.docx")

        create_pdf(prof, pdf_path)
        create_docx(prof, docx_path)
        print(f"Generated: {pdf_path} and {docx_path}")

    # Standard default sample_resume.pdf for requirement
    std_pdf = os.path.join(SAMPLES_DIR, "sample_resume.pdf")
    create_pdf(PROFILES[0], std_pdf)
    print(f"Generated default sample: {std_pdf}")


if __name__ == "__main__":
    main()
