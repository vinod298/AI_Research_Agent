# Enterprise AI Research & Knowledge Assistant

> **Production-Ready | Full Stack | RAG | TensorFlow | Enterprise Architecture**

A high-performance enterprise software application designed for multi-PDF document ingestion, intelligent text & semantic chunking, Qdrant vector database indexing, hybrid BM25 + dense retrieval with Reciprocal Rank Fusion (RRF), anti-hallucination Retrieval-Augmented Generation (RAG) with page citations, multi-document comparative analysis, multi-granularity summarization, automated TensorFlow 2.x category classification, and live operational analytics dashboards.

---

## 🏗️ Architecture Overview

```
[ PDF Upload ] ──► [ PyMuPDF / pdfplumber ] ──► [ Text & Metadata Extraction ]
                                                         │
                                                         ▼
[ TF Classifier ] ◄── [ TensorFlow 2.x ] ◄─── [ Intelligent Text Chunker ]
       │                                                 │
       ▼                                                 ▼
[ Category Label ]                              [ SentenceTransformers ]
                                                         │
                                                         ▼
[ Qdrant Vector DB ] ◄───────────────────────── [ 384-d Vector Embeddings ]
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
[ Dense Vector Search ]                [ BM25 Keyword Search ]
       │                                         │
       └───────────────────┬─────────────────────┘
                           ▼
              [ Reciprocal Rank Fusion (RRF) ]
                           │
                           ▼
               [ Anti-Hallucination Prompt ]
                           │
                           ▼
               [ Multi-LLM Provider Adapter ]
            (OpenAI, Anthropic, Gemini, Ollama, DeepSeek)
                           │
                           ▼
          [ Grounded Response + Inline Citations ]
```

---

## 🛠️ Tech Stack & Key Technologies

- **Language & Runtime**: Python 3.11
- **REST Framework**: FastAPI & Uvicorn ASGI Server
- **Database & ORM**: PostgreSQL / SQLite fallback using async SQLAlchemy 2.0 ORM
- **Caching & Rate Limiting**: Redis 7 with in-memory fallback
- **Vector Database**: Qdrant Vector Database
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Document Classifier**: TensorFlow 2.x Keras Neural Classifier (Embedding + Conv1D + GlobalMaxPooling) covering 10 enterprise domains
- **Document Processing**: PyMuPDF (`fitz`), `pdfplumber`, `pypdf`
- **Retrieval Engine**: BM25 + Qdrant Dense Vector Search with Reciprocal Rank Fusion (RRF)
- **Security & Authentication**: JWT (JSON Web Tokens), bcrypt password hashing, API Keys, RBAC roles
- **Containerization & CI/CD**: Docker, Docker Compose, GitHub Actions

---

## 🚀 Quick Start & Installation

### Option 1: Running Locally with Python

1. **Clone & Setup Environment**:
   ```bash
   git clone https://github.com/enterprise/ai-research-assistant.git
   cd ai-research-assistant
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Train / Initialize TensorFlow Classifier**:
   ```bash
   python -m scripts.train_classifier
   ```

3. **Seed Sample Research Documents** (Optional):
   ```bash
   python -m scripts.seed_sample_docs
   ```

4. **Launch Application**:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access Interfaces**:
   - **Interactive Web Dashboard**: `http://localhost:8000/`
   - **Swagger OpenAPI Docs**: `http://localhost:8000/docs`
   - **ReDoc Documentation**: `http://localhost:8000/redoc`

---

### Option 2: Running with Docker Compose

Provision PostgreSQL 15, Redis 7, Qdrant, and FastAPI application in containers:

```bash
docker-compose up --build -d
```

---

## 🧪 Testing Strategy

Run the comprehensive pytest test suite covering authentication, document upload pipeline, hybrid search, RAG pipeline with citations, TensorFlow classifier inference, and analytics:

```bash
pytest -v --asyncio-mode=auto
```

---

## 🌐 API Endpoint Specification

### Authentication (`/api/v1/auth`)
- `POST /register`: Register new enterprise user
- `POST /login`: Authenticate and obtain JWT access token
- `GET /me`: Get active user profile
- `POST /api-keys`: Generate cryptographically secure API key

### Document Management (`/api/v1/documents`)
- `POST /upload`: Upload PDF document and trigger background ingestion pipeline
- `GET /`: List all uploaded documents
- `GET /{id}`: Retrieve detailed document info with extracted text chunks
- `DELETE /{id}`: Delete document, database chunks, and Qdrant vectors
- `POST /{id}/reprocess`: Re-run ingestion pipeline with custom chunk parameters

### Semantic & Hybrid Search (`/api/v1/search`)
- `POST /search`: Execute semantic, keyword, or hybrid retrieval with metadata filtering

### RAG QA Engine (`/api/v1/chat`)
- `POST /chat`: RAG Question-Answering with session conversation memory and verified page citations

### Comparative Analysis & Summarization
- `POST /compare`: Side-by-side comparative matrix across documents
- `POST /summarize`: Multi-granularity summary generator (Executive, Technical, Detailed, Bullet points)

### TensorFlow Classifier (`/api/v1/classify`)
- `POST /classify`: Classify text or document into 10 enterprise domains

### Operational Analytics (`/api/v1/analytics`)
- `GET /analytics`: Operational metrics overview, category distributions, and latency stats
- `GET /health`: System health status
- `GET /metrics`: Service metrics

---

## 🛡️ Production & Security Considerations

1. **Anti-Hallucination Enforcer**: The RAG prompt builder forces strict grounding. If retrieved context is insufficient, it responds: `"I cannot determine the answer from the uploaded documents."`
2. **Graceful Fallbacks**: In environments where PostgreSQL, Redis, or external Qdrant servers are offline, the system seamlessly uses SQLite async, in-memory caching, and in-memory vector storage so that development and testing operate without friction.
3. **Secrets Management**: Sensitive credentials (JWT Secret, Database URIs, LLM API Keys) are managed through Pydantic V2 Settings reading from `.env`.
