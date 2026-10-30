# PeopleOps AI — HR Policy Intelligence & Service Desk

**An AI-powered HR service desk combining Retrieval-Augmented Generation (RAG), policy-aware question answering, sensitive-case escalation, SLA monitoring, and anomaly detection.**

Built as part of the **YottaFlex AI Forward Deployed Engineer Coding Challenge**.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://www.sqlite.org/)
[![LLM](https://img.shields.io/badge/LLM-Google%20Gemini-orange.svg)](https://ai.google.dev/)

**GitHub Repository:** [HR-Policy-Intelligence](https://github.com/samirmore7/HR-Policy-Intelligence)

---

## 1. Overview

PeopleOps AI is a synthetic HR support platform designed to demonstrate how AI can assist with routine employee queries while routing sensitive cases for human review.

The platform combines a Streamlit interface, FastAPI backend, SQLite database, semantic policy retrieval, Gemini-powered answer generation, workflow escalation, and operational monitoring.

The objective is to demonstrate an end-to-end AI engineering workflow involving data generation, database design, RAG implementation, LLM integration, API development, workflow automation, and operational anomaly detection.

### Key Objectives

- Automate routine HR queries using Retrieval-Augmented Generation.
- Generate policy-grounded responses using Google Gemini.
- Identify and escalate sensitive employee requests.
- Monitor ticket response and resolution SLAs.
- Detect predefined operational anomalies.
- Maintain data integrity, auditability, and reproducibility.

---

## 2. Key Features

### 2.1 AI-Powered HR Assistant

- Retrieves relevant HR policy content using Sentence Transformer embeddings.
- Uses Google Gemini to generate answers grounded in retrieved policy context.
- Includes policy source information in responses.
- Avoids inventing policy details when retrieved context is insufficient.
- Recommends human HR assistance when available policy information cannot answer a question.

### 2.2 Sensitive Case Routing

Detects sensitive topics such as:

- Harassment
- Discrimination
- Workplace misconduct
- Salary disputes

The system:

- Routes sensitive requests for human HR handling.
- Updates ticket assignments and status.
- Records escalation events for traceability.
- Maintains an audit trail of workflow changes.

### 2.3 SLA Monitoring

- Supports 24×7 and business-hours SLA calculations.
- Calculates first-response and resolution deadlines.
- Evaluates SLA performance.
- Identifies SLA breaches.
- Records breach events.
- Prevents duplicate breach records.

### 2.4 Anomaly Detection

The system detects four deliberately injected anomalies:

| Anomaly ID | Description |
|---|---|
| ANOM-001 | Obsolete policy citation |
| ANOM-002 | Restricted case misrouting |
| ANOM-003 | Invalid business-hours SLA |
| ANOM-004 | Unsupported assistant policy claim |

The anomaly detector uses rule-based checks to identify these predefined challenge scenarios.

### 2.5 Synthetic Data Generation

The project generates the following synthetic records:

| Data Entity | Records |
|---|---:|
| HR Tickets | 5,000 |
| Knowledge Articles | 150 |
| Messages | 20,000 |
| Policy Documents | 25 |
| Policy Versions | 30 |
| SLA Rules | 24 |

Additional records include employees, departments, assignments, resolutions, and audit events.

A fixed random seed of `20261022` is used for reproducibility.

### 2.6 Interactive Dashboard

The Streamlit application includes six sections:

1. Overview Dashboard
2. HR Assistant
3. Ticket Explorer
4. SLA Command Center
5. Anomaly Intelligence
6. Policy Library

Four interface themes are available:

- Midnight
- Light
- Ocean
- Forest

---

## 3. Application Screenshots

The following screenshots demonstrate the application's main features.

Add your actual dashboard screenshots to a `screenshots/` folder using the filenames below.

### 3.1 Overview Dashboard

![Overview Dashboard](screenshots/overview.png)

### 3.2 HR Assistant

![HR Assistant](screenshots/hr-assistant.png)

### 3.3 SLA Command Center

![SLA Command Center](screenshots/sla-command-center.png)

### 3.4 Anomaly Intelligence

![Anomaly Intelligence](screenshots/anomaly-intelligence.png)

### 3.5 Ticket Explorer

![Ticket Explorer](screenshots/ticket-explorer.png)

---

## 4. Technology Stack

| Area | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend API | FastAPI, Uvicorn |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Embeddings | Sentence Transformers |
| Vector Retrieval | NumPy Similarity Search |
| LLM Integration | Google Gemini |
| PDF Processing | pypdf |
| Testing | Pytest |
| Version Control | Git, GitHub |

---

## 5. System Architecture

The application follows a modular architecture consisting of six major components.

### 5.1 User Interface

Streamlit provides the interactive dashboard, HR assistant, ticket exploration, SLA monitoring, anomaly intelligence, and policy library.

### 5.2 Request Routing

The query router identifies whether an incoming request is routine or requires sensitive-case escalation.

Routine requests are directed to the RAG pipeline, while sensitive requests are routed for human HR handling.

### 5.3 RAG Pipeline

The RAG pipeline follows these steps:

1. Receives an employee question.
2. Converts the question into an embedding.
3. Retrieves relevant policy content using semantic similarity.
4. Passes the retrieved context to Google Gemini.
5. Generates a response grounded in the retrieved policy information.
6. Provides policy source information with the response.

### 5.4 Workflow Management

Sensitive requests are escalated through the workflow module.

Ticket assignments, ticket statuses, and audit events are updated to maintain traceability.

### 5.5 Monitoring and Evaluation

The SLA engine calculates response and resolution deadlines and identifies SLA breaches.

The anomaly detector evaluates operational records against predefined anomaly rules.

### 5.6 Backend API

FastAPI exposes REST endpoints for:

- Health checks
- Ticket information
- Individual ticket details
- Ticket messages

Interactive API documentation is available through Swagger UI.

---

## 6. Project Structure

```text
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
```

---

## 7. Setup Instructions

### 7.1 Prerequisites

Ensure the following are installed:

- Python 3.11 or later
- Git
- Google Gemini API key

### 7.2 Clone the Repository

```bash
git clone https://github.com/samirmore7/HR-Policy-Intelligence.git

cd HR-Policy-Intelligence
```

### 7.3 Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 7.4 Install Dependencies

```bash
pip install -r requirements.txt
```

For an environment using the exact captured package versions, use:

```bash
pip install -r requirements-lock.txt
```

### 7.5 Configure Gemini API Access

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Obtain an API key from [Google AI Studio](https://aistudio.google.com/).

**Important:** Never commit your actual API key to GitHub.

### 7.6 Run the Streamlit Application

The repository already includes the generated SQLite database, policy chunks, and embeddings.

After installing dependencies and configuring Gemini, launch the application:

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

### 7.7 Run the FastAPI Backend

Open a separate terminal, activate the virtual environment, and execute:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

**Swagger API Documentation:**

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 8. Full Data Regeneration

To recreate the synthetic dataset and RAG knowledge base from scratch, execute the following commands in dependency order.

### 8.1 Initialize the Database Schema

```bash
python -m src.test_schema
```

### 8.2 Generate Synthetic Data

Execute the following scripts:

```bash
python -m src.generate_data
python -m src.generate_policies
python -m src.generate_sla
python -m src.generate_tickets
python -m src.generate_messages
python -m src.generate_workflow
python -m src.generate_events
```

### 8.3 Validate the Generated Dataset

```bash
python -m src.validate_data
```

### 8.4 Inject and Verify Challenge Anomalies

```bash
python -m src.inject_anomalies
python -m src.verify_anomalies
```

### 8.5 Rebuild the RAG Knowledge Base

```bash
python -m rag.ingest
python -m rag.embeddings
```

This process recreates the database, synthetic records, anomaly scenarios, policy chunks, and embeddings.

**Note:** Run the data-generation process on a fresh database. The anomaly injection script also creates a clean database backup and a separate ground-truth file.

---

## 9. Anomaly Detection Evaluation

The rule-based anomaly detector was evaluated against the four deliberately injected ground-truth anomalies.

### 9.1 Evaluation Metrics

| Metric | Result |
|---|---:|
| Expected Anomalies | 4 |
| True Positives | 4 |
| False Positives | 0 |
| False Negatives | 0 |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

### 9.2 Run the Evaluation

```bash
python -m src.evaluate_anomalies
```

### 9.3 Evaluation Limitations

These results demonstrate detection of the four predefined challenge scenarios.

They should not be interpreted as evidence of generalization to unseen anomalies or real-world HR data.

---

## 10. Data Integrity and Reproducibility

The project includes several mechanisms to support reproducibility and data validation:

- Synthetic data generation uses a fixed random seed.
- A clean database backup is maintained separately from the operational database.
- Ground-truth anomaly labels are stored separately from operational data.
- Validation scripts check data integrity and relationships.
- Anomaly injection and verification are handled by separate scripts.
- Policy embeddings and chunks are stored as generated artifacts.

---

## 11. Important Notes and Limitations

- All HR data and policy content are synthetic and intended for demonstration.
- Policy documents are illustrative placeholders, not actual employment policies.
- Sensitive-case routing uses a deterministic, keyword-based baseline.
- Anomaly detection uses rules designed for the challenge scenarios.
- The anomaly evaluation covers only four injected cases.
- The application is a prototype and is not intended for production HR operations without authentication, authorization, privacy controls, and additional security measures.
- The API currently demonstrates basic endpoints and should not be exposed as a production service without access controls.

---

## 12. Future Improvements

Potential future enhancements include:

- Role-based access control and authentication.
- More advanced sensitive-case classification.
- Generalized policy-grounded claim verification.
- Improved SLA handling with holiday calendars.
- Expanded automated testing.
- Production deployment and monitoring.
- Cloud-based database and vector search integration.

---

## 13. Author

Developed as an AI engineering challenge project demonstrating practical skills in:

- Python Development
- Retrieval-Augmented Generation (RAG)
- LLM Integration
- Semantic Search and Embeddings
- REST API Development
- Database Design
- Workflow Automation
- SLA Monitoring
- Anomaly Detection
- Data Validation and Reproducibility

**GitHub Profile:** [samirmore7](https://github.com/samirmore7)

**Project Repository:** [PeopleOps AI — HR Policy Intelligence & Service Desk](https://github.com/samirmore7/HR-Policy-Intelligence)

---

*PeopleOps AI — Bringing intelligence, traceability, and automation to HR service operations.*
