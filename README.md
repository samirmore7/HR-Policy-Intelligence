# PeopleOps AI — HR Policy Intelligence & Service Desk

An AI-powered HR service desk that combines Retrieval-Augmented Generation (RAG), policy-aware question answering, sensitive-case escalation, SLA monitoring, and anomaly detection.

Built as part of the YottaFlex AI Forward Deployed Engineer coding challenge.

## Overview

PeopleOps AI is a synthetic HR support platform designed to demonstrate how AI can assist with routine employee queries while routing sensitive cases for human review.

The platform combines a Streamlit interface, FastAPI backend, SQLite database, semantic policy retrieval, Gemini-powered answer generation, workflow escalation, and operational monitoring.

## Key Features

### 1. AI-Powered HR Assistant
- Retrieves relevant HR policy content using sentence-transformer embeddings.
- Uses Gemini to generate answers grounded in retrieved policy context.
- Includes policy source information in responses.
- Avoids inventing policy details when retrieved context is insufficient.

### 2. Sensitive Case Routing
- Detects sensitive topics such as harassment, discrimination, misconduct, and salary disputes.
- Routes sensitive requests for human HR handling.
- Updates ticket assignments and status.
- Records escalation events for traceability.

### 3. SLA Monitoring
- Supports 24×7 and business-hours SLA calculations.
- Calculates first-response and resolution deadlines.
- Evaluates SLA performance.
- Records SLA breach events and prevents duplicate breach records.

### 4. Anomaly Detection
Four deliberately injected anomalies are detected:

| ID | Anomaly |
|---|---|
| ANOM-001 | Obsolete policy citation |
| ANOM-002 | Restricted case misrouting |
| ANOM-003 | Invalid business-hours SLA |
| ANOM-004 | Unsupported assistant policy claim |

### 5. Synthetic Data Generation
The project generates:
- 5,000 HR tickets
- 150 knowledge articles
- 20,000 messages
- 25 policy documents
- 30 policy versions
- 24 SLA rules
- Assignment, resolution, and audit-event records

The dataset uses a fixed random seed of `20261022` for reproducibility.

### 6. Interactive Dashboard
The Streamlit application includes:
- Overview dashboard
- HR Assistant
- Ticket Explorer
- SLA Command Center
- Anomaly Intelligence
- Policy Library

Four interface themes are available: Midnight, Light, Ocean, and Forest.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Frontend | Streamlit |
| Backend API | FastAPI, Uvicorn |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Embeddings | Sentence Transformers |
| Vector Retrieval | NumPy similarity search |
| LLM | Google Gemini |
| PDF Processing | pypdf |
| Testing | Pytest |

## Project Structure

```text
HR-Policy-Intelligence/
│
├── app.py
├── requirements.txt
├── .gitignore
├── .env
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
├── docs/
│
├── rag/
│   ├── assistant.py
│   ├── embeddings.py
│   ├── escalation.py
│   ├── generator.py
│   ├── ingest.py
│   ├── retriever.py
│   ├── router.py
│   └── tests
│
├── src/
│   ├── schema.sql
│   ├── generate_data.py
│   ├── generate_policies.py
│   ├── generate_sla.py
│   ├── generate_tickets.py
│   ├── generate_messages.py
│   ├── generate_workflow.py
│   ├── generate_events.py
│   ├── inject_anomalies.py
│   ├── validate_data.py
│   ├── verify_anomalies.py
│   ├── anomaly_detector.py
│   ├── evaluate_anomalies.py
│   └── sla_engine.py
│
└── tests/
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd HR-Policy-Intelligence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API access

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit your actual API key.

### 5. Prepare the database and synthetic data

Run the database initialization and data-generation scripts in their dependency order:

```bash
python -m src.test_schema
python -m src.generate_data
python -m src.generate_policies
python -m src.generate_sla
python -m src.generate_tickets
python -m src.generate_messages
python -m src.generate_workflow
python -m src.generate_events
python -m src.validate_data
```

### 6. Inject and verify anomalies

```bash
python -m src.inject_anomalies
python -m src.verify_anomalies
```

### 7. Prepare the RAG knowledge base

```bash
python -m rag.ingest
python -m rag.embeddings
```

### 8. Run the application

```bash
streamlit run app.py
```

### 9. Run the REST API

In a separate terminal:

```bash
uvicorn backend.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Anomaly Detection Evaluation

The rule-based detector was evaluated against the four injected ground-truth anomalies.

| Metric | Result |
|---|---:|
| Expected anomalies | 4 |
| True positives | 4 |
| False positives | 0 |
| False negatives | 0 |
| Precision | 100% |
| Recall | 100% |
| F1-score | 100% |

These results apply to the four deliberately injected anomalies and should not be interpreted as performance on unseen anomalies.

Run the evaluation:

```bash
python -m src.evaluate_anomalies
```

## Data Integrity and Reproducibility

- Synthetic data generation uses a fixed seed.
- A clean database backup is maintained separately from the operational database.
- Ground-truth anomaly labels are stored separately from operational data.
- Validation scripts check data integrity and relationships.
- Anomaly injection and verification are handled by separate scripts.

## Important Notes

- All HR data and policy content are synthetic and intended for demonstration.
- The policy documents are illustrative placeholders, not actual employment policies.
- Sensitive-case routing uses a deterministic rule-based baseline.
- Anomaly detection uses rules designed for the challenge scenarios.
- The application is a prototype and is not intended for production HR operations without authentication, authorization, and additional security controls.

## Future Improvements

- Role-based access control and authentication.
- More advanced sensitive-case classification.
- Generalized policy-grounded claim verification.
- Improved SLA handling with holiday calendars.
- Expanded automated testing.
- Production deployment and monitoring.

## Author

Developed as an AI engineering challenge project demonstrating Python development, RAG, LLM integration, API development, database design, workflow automation, and anomaly detection.
