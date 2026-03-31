import fitz
import os

def create_resume_pdf(filepath, content):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), content, fontsize=11)
    doc.save(filepath)
    doc.close()
    print(f"Created: {filepath}")

resumes = {
    # ML Engineers
    "data/resumes/alice_ml.pdf": """
Alice Johnson
Email: alice@email.com

SKILLS
Python, PyTorch, TensorFlow, scikit-learn, deep learning,
machine learning, SQL, Git, Docker, MLflow

EXPERIENCE
Senior ML Engineer — TechCorp (4 years)
- Built and deployed 10+ production ML models
- Reduced model inference time by 40%
- Led team of 3 junior engineers

EDUCATION
M.Tech Computer Science — IIT Delhi
""",

    "data/resumes/bob_ml.pdf": """
Bob Smith
Email: bob@email.com

SKILLS
Python, scikit-learn, machine learning, SQL, Git,
statistics, data preprocessing, NumPy, pandas

EXPERIENCE
ML Engineer — DataStartup (3 years)
- Developed recommendation system
- Built data pipelines for model training
- Worked with cross-functional teams

EDUCATION
B.Tech Computer Science — NIT Trichy
""",

    "data/resumes/carol_ml.pdf": """
Carol White
Email: carol@email.com

SKILLS
Python, TensorFlow, deep learning, computer vision,
NLP, SQL, Git, AWS, Kubernetes

EXPERIENCE
ML Research Engineer — AI Labs (5 years)
- Published 3 research papers
- Built state of the art NLP models
- Deployed models on AWS at scale

EDUCATION
PhD Computer Science — IISc Bangalore
""",

    "data/resumes/david_ml.pdf": """
David Brown
Email: david@email.com

SKILLS
Python, machine learning basics, pandas, NumPy,
Excel, SQL, Git

EXPERIENCE
Junior Data Scientist — Analytics Co (1 year)
- Assisted in building ML models
- Performed data cleaning and EDA
- Created basic visualizations

EDUCATION
B.Sc Statistics — Delhi University
""",

    # Data Analysts
    "data/resumes/eve_analyst.pdf": """
Eve Davis
Email: eve@email.com

SKILLS
Python, SQL, Tableau, Excel, statistics,
data visualization, Power BI, R

EXPERIENCE
Senior Data Analyst — RetailCorp (4 years)
- Built 20+ executive dashboards in Tableau
- Reduced reporting time by 60%
- Managed stakeholder relationships

EDUCATION
MBA Business Analytics — IIM Ahmedabad
""",

    "data/resumes/frank_analyst.pdf": """
Frank Wilson
Email: frank@email.com

SKILLS
SQL, Excel, Power BI, statistics,
data visualization, Python basics

EXPERIENCE
Data Analyst — FinanceInc (2 years)
- Created monthly financial reports
- Built automated Excel dashboards
- Worked with finance stakeholders

EDUCATION
B.Com Finance — Mumbai University
""",

    "data/resumes/grace_analyst.pdf": """
Grace Lee
Email: grace@email.com

SKILLS
Python, SQL, Tableau, statistics, R,
machine learning basics, dbt, data visualization

EXPERIENCE
Data Analyst — HealthTech (3 years)
- Analyzed patient data for insights
- Built predictive models for churn
- Created Tableau dashboards for executives

EDUCATION
M.Sc Statistics — Chennai Mathematical Institute
""",

    # Backend Developers
    "data/resumes/henry_backend.pdf": """
Henry Martinez
Email: henry@email.com

SKILLS
Python, Java, REST APIs, PostgreSQL, Docker,
Git, Redis, microservices, AWS, SQL

EXPERIENCE
Senior Backend Developer — FinTech (5 years)
- Designed microservices architecture
- Built high traffic REST APIs
- Led backend team of 4 engineers

EDUCATION
B.Tech Computer Science — BITS Pilani
""",

    "data/resumes/iris_backend.pdf": """
Iris Chen
Email: iris@email.com

SKILLS
Python, REST APIs, PostgreSQL, SQL,
Git, Docker, unit testing

EXPERIENCE
Backend Developer — EcomCorp (2 years)
- Built product catalog API
- Optimized database queries by 30%
- Wrote comprehensive unit tests

EDUCATION
B.Tech Information Technology — VIT Vellore
""",

    "data/resumes/jack_backend.pdf": """
Jack Thompson
Email: jack@email.com

SKILLS
Java, Spring Boot, REST APIs, MySQL,
Git, SQL, basic Docker

EXPERIENCE
Junior Backend Developer — SoftwareCo (1 year)
- Developed REST API endpoints
- Fixed production bugs
- Wrote API documentation

EDUCATION
B.Sc Computer Science — Pune University
"""
}

os.makedirs("data/resumes", exist_ok=True)

for filepath, content in resumes.items():
    create_resume_pdf(filepath, content)

print("\nAll sample resumes created successfully.")
print(f"Total: {len(resumes)} resumes")