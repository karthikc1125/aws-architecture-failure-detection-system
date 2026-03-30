# 📚 Failure-Driven AWS Architecture System - Complete Documentation

**Merged from all project documentation**  
**Date**: March 30, 2026  
**Status**: Production Analysis Complete

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Core Features](#core-features)
5. [Design Decisions](#design-decisions)
6. [API Documentation](#api-documentation)
7. [Agent Architecture](#agent-architecture)
8. [Performance Benchmarks](#performance-benchmarks)
9. [Production Readiness](#production-readiness)
10. [Testing Framework](#testing-framework)
11. [Roadmap & Future](#roadmap--future)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

### Philosophy
**Failure-Driven**: This system assumes your architecture **will fail** and designs backwards from that certainty.

Most AI coding assistants are "StackOverflow-driven"—they find code that works. This system is different.

### Core Innovation
Uses **Agentic RAG (Retrieval-Augmented Generation)** architecture:
1. **Retrieve** historical disaster data (2017 AWS S3 Outage, etc.)
2. **Detect** deterministic failure patterns (Retry Storms, SPOFs)
3. **Architect** resilient solutions using proven mitigations

### Key Metrics
- ✅ **200+ AWS failure patterns** in YAML format
- ✅ **10+ major cloud incidents** in vector memory
- ✅ **50+ configuration rules** for compliance
- ✅ **Sub-millisecond** FAISS retrieval
- ✅ **100-167 req/sec** throughput
- ⚠️ **62/100** production readiness score

---

## System Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────┐
│              INTERFACE LAYER                         │
│  Frontend (HTML/CSS/JS) - Glassmorphism UI          │
│  - Home, Analyze, Methodology, Settings              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              API LAYER                               │
│  FastAPI with Pydantic validation                    │
│  - /analyze (POST)                                   │
│  - /settings (GET/POST)                              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                     │
│  Pipeline orchestrator                               │
│  - State management                                  │
│  - Agent coordination                                │
│  - Validation & output formatting                    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              AGENT LAYER                             │
│  FailurePredictionAgent + ArchitectureAgent          │
│  - Pattern matching                                  │
│  - Graph analysis                                    │
│  - Service recommendations                          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              KNOWLEDGE LAYER                         │
│  RAG + Rules + Vector Store                          │
│  - Embeddings (FAISS)                                │
│  - Patterns (YAML)                                   │
│  - Incident history                                  │
│  - Mitigation rules                                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              DATA LAYER                              │
│  Raw truth: JSON/YAML files                          │
│  - /data/incidents - historical outages              │
│  - /data/patterns - failure definitions              │
│  - /data/adr - architecture decision records         │
└─────────────────────────────────────────────────────┘
```

### Directory Structure

```
.
├── api/                    # FastAPI application
│   ├── main.py            # Entry point
│   ├── routes.py          # API endpoints
│   └── models.py          # Pydantic schemas
├── agents/                # Multi-agent system
│   ├── base_agent.py      # Base class
│   ├── failure_prediction_agent.py
│   ├── architecture_agent.py
│   ├── text_to_graph.py   # NLP → graph conversion
│   └── iac_parser.py      # Terraform parser
├── orchestration/         # Pipeline management
│   ├── pipeline.py        # Main orchestrator
│   ├── state.py          # State management
│   └── validator.py      # Output validation
├── embeddings/           # Vector embeddings
│   ├── embedder.py       # SentenceTransformer
│   ├── build_index.py    # FAISS index builder
│   └── embedding_config.py
├── rag/                  # Retrieval-augmented generation
│   ├── retriever.py      # Query retriever
│   ├── query_builder.py  # Query optimization
│   └── context_formatter.py
├── frontend/             # Web UI
│   ├── index.html        # Home page
│   ├── analyze.html      # Analysis interface
│   ├── methodology.html  # Docs page
│   ├── app.js           # Frontend logic
│   └── style.css        # Glassmorphism styling
├── schemas/             # Data validation
│   ├── failure_schema.py
│   ├── architecture_schema.py
│   └── output_schema.py
├── rules/              # Deterministic rules
│   ├── pattern_to_service.py
│   ├── service_catalog.py
│   └── failure_to_pattern.py
├── data/               # Knowledge base
│   ├── incidents/      # Historical outages
│   ├── patterns/       # 200+ failure YAML files
│   └── adr/           # Architecture decisions
├── vector_store/       # FAISS indices
├── tests/             # Test suite
│   ├── test_pattern_matching.py
│   ├── test_failure_prediction.py
│   ├── test_rag_retrieval.py
│   └── test_iac_analysis.py
└── docs/              # Documentation
    ├── architecture.md
    ├── design_decisions.md
    ├── failure_taxonomy.md
    └── future_roadmap.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip or poetry
- 2GB RAM (minimum)
- 500MB disk space

### Step 1: Clone Repository
```bash
git clone https://github.com/karthikc1125/aws-architecture-failure-detection-system.git
cd aws-architecture-failure-detection-system
```

### Step 2: Set Up Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Build Vector Index (One-time)
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 embeddings/build_index.py
```

### Step 5: Run the System
```bash
python3 api/main.py
```

### Step 6: Access Web Interface
Open browser to: **http://localhost:8000**

---

## Core Features

### 1. Failure Pattern Detection
- **200+ AWS failure patterns** (YAML definitions)
- Pattern matching on user input
- Graph-based cyclic dependency detection
- SPOF (Single Point of Failure) identification

### 2. Architecture Analysis
- **Multi-agent reasoning** on failures
- Rule-based service recommendations
- Proposed architecture generation
- Mitigation strategy synthesis

### 3. Vector-Based Retrieval
- FAISS index for sub-millisecond queries
- Semantic search on incident history
- Context-aware recommendations

### 4. IaC Support
- Terraform file parsing
- Remote module resolution
- Configuration analysis
- Compliance rule checking

### 5. Modern Web Interface
- Glassmorphism design
- Real-time analysis
- Settings modal for AI provider config
- Responsive layout

---

## Design Decisions

### Why Separate Agents?
Single-prompt "do everything" approaches fail at complexity.

**FailurePredictionAgent**: Understands the problem  
**ArchitectureAgent**: Proposes solutions

This prevents "solutioneering" (jumping to solutions without problem analysis).

### Why No Model Fine-Tuning?
Fine-tuning on architecture diagrams is brittle and requires constant retraining.

**Instead, we use**:
- **Rules**: Deterministic logic ("If A then B")
- **Vectors**: Semantic similarity ("This looks like the 2017 outage")

### Why Deterministic Rules > LLM Probability?
Production systems need certainty, not probabilistic answers.

Example:
```python
# ✅ Deterministic
if "single partition" in description and "DynamoDB" in description:
    failure = HotPartitionFailure()

# ❌ Probabilistic (unreliable)
# LLM: "50% chance of hot partition issue"
```

### Why FAISS for Vector Store?
- ✅ CPU-based (no GPU needed)
- ✅ Sub-millisecond retrieval
- ✅ In-memory (fast)
- ❌ Not persistent (needs rebuild on restart)

**Future**: PostgreSQL with pgvector for persistence.

---

## API Documentation

### Endpoint: POST /analyze

**Request**:
```json
{
  "description": "I have API Gateway → Lambda → DynamoDB (single partition) architecture",
  "provider": "openrouter",
  "model_id": "google/gemini-2.0-flash-exp:free"
}
```

**Response**:
```json
{
  "input_summary": "User upload service with...",
  "detected_failures": [
    {
      "name": "Hot Partition",
      "failure_class": "Performance Degradation",
      "description": "Single partition writes will throttle at scale",
      "mitigation": "Sharding or UUID suffixes",
      "likelihood": 85
    }
  ],
  "proposed_architecture": {
    "components": [
      {"name": "Resilient-SQS", "type": "SQS", "connections": []},
      {"name": "Resilient-DynamoDB", "type": "DynamoDB", "connections": []}
    ],
    "description": "Proposed Resilient Architecture:\n- Added SQS to decouple API Gateway and Lambda"
  },
  "review_score": 7,
  "review_comments": "Architecture has improved resilience"
}
```

### Status Codes
- **200**: Success
- **400**: Bad request (validation error)
- **500**: Server error
- **503**: Service unavailable (LLM API down)

---

## Agent Architecture

### FailurePredictionAgent

**Input**: Natural language architecture description  
**Output**: List of detected failure modes

**Process**:
1. Load 200+ YAML patterns
2. Build architecture graph via NLP
3. Analyze graph for:
   - Cyclic dependencies
   - SPOFs (Single Points of Failure)
   - Resource bottlenecks
   - Configuration issues
4. Match against pattern library
5. Retrieve similar incidents from RAG

**Example**:
```
Input: "EC2 instance reads from RDS with 1 replica"
        ↓
Graph: EC2 → RDS (single read replica)
        ↓
Analysis: Missing AZ redundancy
        ↓
Detected: SPOF in database tier
        ↓
Retrieved: AWS RDS outage case study (2015)
```

### ArchitectureAgent

**Input**: List of failures  
**Output**: Proposed resilient architecture

**Process**:
1. For each failure detected:
   - Extract mitigation strategy
   - Map to AWS services
   - Create component
2. Deduplicate services
3. Generate design rationale

**Example**:
```
Failure: "Hot Partition"
Mitigation: "Sharding or UUID suffixes"
        ↓
Services: DynamoDB (with on-demand pricing)
        ↓
Proposed: Add DAX for caching
```

---

## Performance Benchmarks

### Throughput
| Codebase Size | Before | After | Improvement |
|---------------|--------|-------|-------------|
| Small (10 resources) | 33 req/s | 33 req/s | - |
| Medium (100 resources) | 30 req/s | 100 req/s | 3.3x |
| Large (500 resources) | 30 req/s | 143 req/s | 4.8x |
| Very Large (1000 resources) | 30 req/s | 167 req/s | 5.6x |

### Latency
- Pattern matching: 10-50ms
- Graph analysis: 20-100ms
- RAG retrieval: 1-5ms
- LLM call: 2000-5000ms (bottleneck)

**Total E2E latency: 2-6 seconds** (mostly waiting for LLM)

---

## Production Readiness

### Current Score: 62/100 🟡

### Suitable For:
- ✅ Internal tool (company intranet)
- ✅ Research/academic project
- ✅ Open-source foundation

### NOT Suitable For:
- ❌ Public SaaS (no auth)
- ❌ Enterprise (no monitoring)
- ❌ Critical systems (no HA)

### Critical Gaps:
1. **Testing**: 2/10 - Only placeholder tests
2. **Error Handling**: 2/10 - Almost none
3. **Security**: 3/10 - No authentication
4. **Monitoring**: 1/10 - Only print statements
5. **Deployment**: 1/10 - No Docker/K8s

### Path to Production (6-12 weeks):
- Week 1-2: Testing + Error Handling
- Week 2-3: Security (Auth, Rate Limiting)
- Week 3-4: Monitoring (Logging, Metrics)
- Week 4+: Deployment (Docker, K8s)

---

## Testing Framework

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=

# Specific test file
python -m pytest tests/test_pattern_matching.py -v
```

### Current Test Coverage
- ❌ Pattern matching: Empty stub
- ❌ Failure prediction: No tests
- ❌ RAG retrieval: No tests
- ❌ IaC analysis: No tests
- ❌ API endpoints: No tests

### Recommended Test Suite
See `TESTING_CLI_GUIDE.md` for comprehensive testing framework.

---

## Roadmap & Future

### Q1 2026 (Current)
- ✅ Failure detection engine
- ✅ Architecture recommendations
- ✅ Web UI (basic)
- ⏳ Testing framework

### Q2 2026
- [ ] Terraform generation from recommendations
- [ ] Cost analysis agent
- [ ] Multi-cloud support (Azure, GCP)
- [ ] API versioning & documentation

### Q3 2026
- [ ] Cross-account analysis
- [ ] Real-time monitoring integration
- [ ] CI/CD pipeline integration
- [ ] Custom pattern creation UI

### Q4 2026
- [ ] GraphQL API option
- [ ] Advanced ML-based recommendations
- [ ] Compliance reporting
- [ ] Enterprise features (RBAC, SSO)

---

## Troubleshooting

### Server Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check port 8000 in use
lsof -i :8000

# Try alternate port
python3 -m uvicorn api.main:app --port 8001
```

### FAISS Index Error
```bash
# Rebuild index
python3 embeddings/build_index.py

# Verify index exists
ls -la vector_store/
```

### LLM API Errors
```bash
# Check OpenRouter API key
echo $OPENROUTER_API_KEY

# Test connectivity
curl https://openrouter.ai/api/v1/models
```

### Memory Issues
```bash
# FAISS loads entire index in RAM
# For large indices, use PostgreSQL instead
# See docs/database_migration.md
```

---

## Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-your-key-here

# Optional
LLM_MODEL=google/gemini-2.0-flash-exp:free
AI_PROVIDER=openrouter  # or "simulation" for offline mode
PYTHONPATH=.
```

---

## Contributing

### Development Setup
```bash
# Install dev dependencies
pip install pytest pytest-cov black flake8 mypy

# Format code
black api/ agents/ orchestration/

# Type check
mypy api/ agents/

# Lint
flake8 api/ agents/
```

### Commit Message Format
```
[TYPE] Brief description

TYPE: feature, fix, test, docs, refactor
```

---

## License

MIT License - See LICENSE.md

---

## Support

- 📧 Email: contact@safecloud.ai
- 🐙 GitHub: https://github.com/karthikc1125/aws-architecture-failure-detection-system
- 📚 Docs: http://localhost:8000/methodology

---

**Last Updated**: March 30, 2026  
**Version**: 1.0.0-beta  
**Status**: Active Development

