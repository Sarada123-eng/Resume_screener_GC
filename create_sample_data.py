import fitz
import os

def create_resume_pdf(filepath, content):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), content, fontsize=10)
    doc.save(filepath)
    doc.close()
    print(f"Created: {filepath}")

resumes = {
    # ── ML Engineers ──────────────────────────────────────────────────────────
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

PROJECTS
- ProductionML Framework: Built end-to-end ML pipeline with MLflow tracking
- DeepVision: Computer vision model for quality inspection at scale
- AutoFeature: Automated feature engineering library for tabular data

CERTIFICATIONS
- AWS Certified Machine Learning Specialty
- Deep Learning Specialization — Coursera (Andrew Ng)
- MLflow Certified Practitioner

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
- Developed recommendation system serving 1M users
- Built data pipelines for model training
- Worked with cross-functional teams

PROJECTS
- RecoEngine: Collaborative filtering recommendation system
- DataPipeline: Automated ETL pipeline for model training data

CERTIFICATIONS
- Google Professional Data Engineer
- Coursera Machine Learning Specialization

EDUCATION
B.Tech Computer Science — NIT Trichy
""",

    "data/resumes/carol_ml.pdf": """
Carol White
Email: carol@email.com

SKILLS
Python, TensorFlow, deep learning, computer vision,
NLP, SQL, Git, AWS, Kubernetes, Docker, MLflow

EXPERIENCE
ML Research Engineer — AI Labs (5 years)
- Published 3 research papers in top conferences
- Built state of the art NLP models for multilingual tasks
- Deployed models on AWS at scale using Kubernetes

PROJECTS
- MultilingualBERT: Fine-tuned BERT for 8 Indian languages — 2k GitHub stars
- VisionTransformer: Image classification with ViT achieving SOTA on benchmark
- NLPPipeline: Production NLP pipeline on AWS SageMaker

CERTIFICATIONS
- AWS Certified Machine Learning Specialty
- Kubernetes Administrator (CKA)
- TensorFlow Developer Certificate
- Deep Learning Specialization — Coursera

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
- Created basic visualizations for stakeholders

PROJECTS
- SalesForecast: Time series forecasting model for retail sales
- ChurnPredictor: Basic logistic regression churn model

CERTIFICATIONS
- Coursera Python for Data Science

EDUCATION
B.Sc Statistics — Delhi University
""",

    # ── Data Analysts ─────────────────────────────────────────────────────────
    "data/resumes/eve_analyst.pdf": """
Eve Davis
Email: eve@email.com

SKILLS
Python, SQL, Tableau, Excel, statistics,
data visualization, Power BI, R, dbt

EXPERIENCE
Senior Data Analyst — RetailCorp (4 years)
- Built 20+ executive dashboards in Tableau
- Reduced reporting time by 60% through automation
- Managed stakeholder relationships across 5 departments

PROJECTS
- ExecutiveDash: Real-time Tableau dashboard for C-suite KPIs
- SQLAutomation: Automated 30+ monthly SQL reports saving 40 hours/month
- CohortAnalysis: Customer cohort analysis tool in Python

CERTIFICATIONS
- Tableau Desktop Specialist
- Google Data Analytics Certificate
- Microsoft Power BI Data Analyst

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
- Created monthly financial reports for board
- Built automated Excel dashboards using VBA
- Worked with finance stakeholders on budgeting analysis

PROJECTS
- FinanceReport: Automated monthly P&L report in Excel + Power BI
- BudgetTracker: Budget vs actuals dashboard for finance team

CERTIFICATIONS
- Microsoft Excel Expert
- Power BI Data Analyst Associate

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
- Analyzed patient data for clinical insights
- Built predictive models for patient churn
- Created Tableau dashboards for medical executives

PROJECTS
- PatientChurn: ML model predicting patient dropout with 85% accuracy
- ClinicalDash: Tableau dashboard tracking 50+ health KPIs in real time
- dbtPipeline: Data transformation pipeline using dbt for analytics warehouse

CERTIFICATIONS
- Tableau Desktop Certified Associate
- dbt Analytics Engineer Certification
- Google Advanced Data Analytics

EDUCATION
M.Sc Statistics — Chennai Mathematical Institute
""",

    # ── Backend Developers ────────────────────────────────────────────────────
    "data/resumes/henry_backend.pdf": """
Henry Martinez
Email: henry@email.com

SKILLS
Python, Java, REST APIs, PostgreSQL, Docker,
Git, Redis, microservices, AWS, SQL, Kubernetes

EXPERIENCE
Senior Backend Developer — FinTech (5 years)
- Designed microservices architecture handling 10k TPS
- Built high traffic REST APIs with 99.9% uptime
- Led backend team of 4 engineers

PROJECTS
- PaymentGateway: Microservices-based payment processing system on AWS
- APIGateway: Custom API gateway with Redis caching reducing latency by 50%
- DBOptimizer: PostgreSQL query optimization toolkit

CERTIFICATIONS
- AWS Certified Developer Associate
- Docker Certified Associate
- Kubernetes Application Developer (CKAD)

EDUCATION
B.Tech Computer Science — BITS Pilani
""",

    "data/resumes/iris_backend.pdf": """
Iris Chen
Email: iris@email.com

SKILLS
Python, REST APIs, PostgreSQL, SQL,
Git, Docker, unit testing, FastAPI

EXPERIENCE
Backend Developer — EcomCorp (2 years)
- Built product catalog API serving 500k products
- Optimized database queries improving speed by 30%
- Wrote comprehensive unit and integration tests

PROJECTS
- CatalogAPI: FastAPI-based product catalog with PostgreSQL backend
- TestSuite: Automated test suite achieving 95% code coverage
- DBMigration: Zero-downtime database migration framework

CERTIFICATIONS
- AWS Cloud Practitioner
- Python Institute PCEP Certification

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
- Developed REST API endpoints for mobile app
- Fixed production bugs and improved response time
- Wrote API documentation using Swagger

PROJECTS
- TaskAPI: Spring Boot REST API for task management app
- MySQLOptimizer: Basic query optimization scripts for MySQL

CERTIFICATIONS
- Oracle Java SE 11 Developer

EDUCATION
B.Sc Computer Science — Pune University
""",
}

os.makedirs("data/resumes", exist_ok=True)

for filepath, content in resumes.items():
    create_resume_pdf(filepath, content)

print("\nAll sample resumes created successfully.")
print(f"Total: {len(resumes)} resumes")