PeopleOps AI — HR Policy Intelligence & Service Desk

An AI-powered HR service desk that combines Retrieval-Augmented Generation (RAG), policy-aware question answering, sensitive-case escalation, SLA monitoring, and anomaly detection.

Built as part of the YottaFlex AI Forward Deployed Engineer coding challenge.

GitHub Repository

Overview

PeopleOps AI is a synthetic HR support platform designed to demonstrate how AI can assist with routine employee queries while routing sensitive cases for human review.

The platform combines a Streamlit interface, FastAPI backend, SQLite database, semantic policy retrieval, Gemini-powered answer generation, workflow escalation, and operational monitoring.

The objective is to demonstrate an end-to-end AI engineering workflow involving data generation, database design, RAG implementation, LLM integration, API development, workflow automation, and operational anomaly detection.

Key Features

1. AI-Powered HR Assistant

Retrieves relevant HR policy content using Sentence Transformer embeddings.

Uses Google Gemini to generate answers grounded in retrieved policy context.

Includes policy source information in responses.

Avoids inventing policy details when retrieved context is insufficient.

Recommends human HR assistance when the available policy information cannot answer a question.

2. Sensitive Case Routing

Detects sensitive topics such as:

Harassment

Discrimination

Workplace misconduct

Salary disputes

The system:

Routes sensitive requests for human HR handling.

Updates ticket assignments and status.

Records escalation events for traceability.

Maintains an audit trail of workflow changes.

3. SLA Monitoring

Supports 24×7 and business-hours SLA calculations.

Calculates first-response and resolution deadlines.

Evaluates SLA performance.

Identifies SLA breaches.

Records breach events and prevents duplicate breach records.

4. Anomaly Detection

The system detects four deliberately injected anomalies:

Anomaly ID

Description

ANOM-001

Obsolete policy citation

ANOM-002

Restricted case misrouting

ANOM-003

Invalid business-hours SLA

ANOM-004

Unsupported assistant policy claim

The anomaly detector uses rule-based checks to identify these predefined challenge scenarios.

5. Synthetic Data Generation

The project generates:

Data Entity

Records

HR Tickets

5,000

Knowledge Articles

150

Messages

20,000

Policy Documents

25

Policy Versions

30

SLA Rules

24

Additional records include employees, departments, assignments, resolutions, and audit events.

A fixed random seed of 20261022 is used for reproducibility.

6. Interactive Dashboard

The Streamlit application includes six sections:

Overview Dashboard

HR Assistant

Ticket Explorer

SLA Command Center

Anomaly Intelligence

Policy Library

Four interface themes are available:

Midnight

Light

Ocean

Forest

Application Screenshots

Add screenshots of the running application in the screenshots/ folder and display them here.

Overview Dashboard



HR Assistant



SLA Command Center



Anomaly Intelligence



Ticket Explorer



Technology Stack

Area

Technologies

Programming Language

Python

Frontend

Streamlit

Backend API

FastAPI, Uvicorn

Database

SQLite

Data Processing

Pandas, NumPy

Embeddings

Sentence Transformers

Vector Retrieval

NumPy similarity search

LLM Integration

Google Gemini

PDF Processing

pypdf

Testing

Pytest

Version Control

Git, GitHub

System Architecture

The application follows a modular architecture.

1. User Interface

Streamlit provides the dashboard, HR assistant, ticket exploration, SLA monitoring, and anomaly intelligence.

2. Request Routing

The query router identifies whether a request is routine or requires sensitive-case escalation.

3. RAG Pipeline

Routine questions are converted into embeddings, matched against policy knowledge, and passed to Gemini with retrieved policy context.

4. Workflow Management

Sensitive requests are escalated through the workflow module. Ticket assignments, statuses, and audit events are updated.

5. Monitoring and Evaluation

The SLA engine calculates deadlines and detects breaches. The anomaly detector evaluates predefined operational inconsistencies.

6. Backend API

FastAPI exposes REST endpoints for health checks, ticket information, and ticket messages.

Project Structure

HR-Policy-Intelligence/
│
├── app.py
├── README.md
├── requirements.txt
├── requirements-lock.txt
├── .gitignore
│
├── backend/
│   └── main.py
│
├── data/
│   ├── hr_policy.db
│   ├── hr_policy_clean.db
│   ├── policy_chunks.json
│   └── policy_embeddings.npy
│
├── audit/
│   └── anomaly_ground_truth.csv
│
├── rag/
│   ├── assistant.py
│   ├── embeddings.py
│   ├── escalation.py
│   ├── generator.py
│   ├── ingest.py
│   ├── retriever.py
│   ├── router.py
│   ├── test_assistant.py
│   ├── test_assistant_escalation.py
│   ├── test_escalation.py
│   ├── test_rag.py
│   └── test_router.py
│
└── src/
    ├── schema.sql
    ├── generate_data.py
    ├── generate_policies.py
    ├── generate_sla.py
    ├── generate_tickets.py
    ├── generate_messages.py
    ├── generate_workflow.py
    ├── generate_events.py
    ├── inject_anomalies.py
    ├── validate_data.py
    ├── verify_anomalies.py
    ├── anomaly_detector.py
    ├── evaluate_anomalies.py
    ├── sla_engine.py
    ├── test_schema.py
    └── test_sla_engine.py

Setup Instructions

Prerequisites

Python 3.11 or later

Git

Google Gemini API key

1. Clone the repository

git clone https://github.com/samirmore7/HR-Policy-Intelligence.git

cd HR-Policy-Intelligence

2. Create a virtual environment

python -m venv .venv

Activate it on Windows PowerShell:

.\.venv\Scripts\Activate.ps1

3. Install dependencies

pip install -r requirements.txt

For an environment using the exact captured package versions, use:

pip install -r requirements-lock.txt

4. Configure Gemini API access

Create a .env file in the project root:

GEMINI_API_KEY=your_gemini_api_key

Obtain an API key from Google AI Studio.

Important: Never commit your actual API key to GitHub.

5. Run the Streamlit application

The repository includes the generated SQLite database, policy chunks, and embeddings.

Therefore, after installing dependencies and configuring Gemini, you can launch the application directly:

streamlit run app.py

6. Run the FastAPI backend

Open a separate terminal, activate the virtual environment, and execute:

uvicorn backend.main:app --reload

API documentation:

http://127.0.0.1:8000/docs

Full Data Regeneration

To recreate the synthetic dataset and RAG knowledge base from scratch, execute the following commands in order.

1. Initialize the database schema

python -m src.test_schema

2. Generate synthetic data

python -m src.generate_data
python -m src.generate_policies
python -m src.generate_sla
python -m src.generate_tickets
python -m src.generate_messages
python -m src.generate_workflow
python -m src.generate_events

3. Validate the generated dataset

python -m src.validate_data

4. Inject and verify challenge anomalies

python -m src.inject_anomalies
python -m src.verify_anomalies

5. Rebuild the RAG knowledge base

python -m rag.ingest
python -m rag.embeddings

This process recreates the database, synthetic records, anomaly scenarios, policy chunks, and embeddings.

Run the data-generation process on a fresh database. The anomaly injection script also creates a clean database backup and a separate ground-truth file.

Anomaly Detection Evaluation

The rule-based anomaly detector was evaluated against the four deliberately injected ground-truth anomalies.

Metric

Result

Expected Anomalies

4

True Positives

4

False Positives

0

False Negatives

0

Precision

100%

Recall

100%

F1-score

100%

Run the evaluation

python -m src.evaluate_anomalies

Evaluation limitation: These results demonstrate detection of the four predefined challenge scenarios. They should not be interpreted as evidence of generalization to unseen anomalies or real-world HR data.

Data Integrity and Reproducibility

The project includes several mechanisms to support reproducibility and data validation:

Synthetic data generation uses a fixed random seed.

A clean database backup is maintained separately from the operational database.

Ground-truth anomaly labels are stored separately from operational data.

Validation scripts check data integrity and relationships.

Anomaly injection and verification are handled by separate scripts.

Policy embeddings and chunks are stored as generated artifacts.

Important Notes and Limitations

All HR data and policy content are synthetic and intended for demonstration.

Policy documents are illustrative placeholders, not actual employment policies.

Sensitive-case routing uses a deterministic, keyword-based baseline.

Anomaly detection uses rules designed for the challenge scenarios.

The anomaly evaluation covers only four injected cases.

The application is a prototype and is not intended for production HR operations without authentication, authorization, privacy controls, and additional security measures.

The API currently demonstrates basic endpoints and should not be exposed as a production service without access controls.

Future Improvements

Role-based access control and authentication.

More advanced sensitive-case classification.

Generalized policy-grounded claim verification.

Improved SLA handling with holiday calendars.

Expanded automated testing.

Production deployment and monitoring.

Cloud-based database and vector search integration.

Author

Developed as an AI engineering challenge project demonstrating:

Python development

Retrieval-Augmented Generation (RAG)

LLM integration

Semantic search and embeddings

REST API development

Database design

Workflow automation

SLA monitoring

Anomaly detection

Data validation and reproducibility

GitHub: samirmore7

Project Repository: PeopleOps AI — HR Policy Intelligence & Service Desk
