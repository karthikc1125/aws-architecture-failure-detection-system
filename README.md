---
title: AWS Architecture Failure Detection
emoji: 🏗️
colorFrom: blue
colorTo: green
sdk: docker
app_file: app_hf.py
pinned: false
license: mit
---

# 🏗️ Failure-Driven AWS Solution Architect

> **A Production-Grade, Research-Oriented AI System for Resilient Cloud Architecture.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)
![Status](https://img.shields.io/badge/status-research_preview-orange.svg)

## 📖 Philosophy
Most AI coding assistants are "StackOverflow-driven"—they find code that works.
**This system is Failure-Driven.** It assumes your architecture *will* fail and designs backwards from that certainty.

It uses a **Agentic RAG (Retrieval-Augmented Generation)** architecture to:
1.  **Retrieve** historical disaster data (e.g., the 2017 AWS S3 Outage).
2.  **Detect** deterministic failure patterns (e.g., Retry Storms, SPOFs) using heuristic agents.
3.  **Architect** resilient solutions using proven mitigation straegies (Rule-Based).

## 🚀 Features
-   **Multi-Page Research Interface**: A modern, research-grade UI to interact with the system.
-   **Vector Memory**: FAISS-based knowledge retrieval of over 10+ major cloud incidents.
-   **Explainable AI**: Every recommendation is tied to a specific failure pattern and mitigation rule.
-   **No Hallucinations**: Core logic is governed by deterministic rules (`rules/`), not just LLM probability.

---

## 🛠️ Installation

### Prerequisites
-   Python 3.9+
-   `pip`
-   (Optional) Virtual Environment

### Quick Start
```bash
# 1. Clone the repo
git clone https://github.com/your-username/failure-driven-architect.git
cd failure-driven-architect

# 2. Install Dependencies
pip install -r requirements.txt
# OR if using venv (Recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Build the Memory Bank (Vector Index)
# Only needed once to ingest data/ into FAISS
export PYTHONPATH=$PYTHONPATH:.
python3 embeddings/build_index.py

# 4. Run the System
python3 api/main.py
```

Now open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 🧠 System Architecture

### 1. Data Layer (`data/`)
Contains "Raw Truth" - JSON files of post-mortems and ADRs.
-   `incidents/`: Historical outage data.
-   `patterns/`: YAML definitions of failure modes.

### 2. Memory Layer (`embeddings/` & `vector_store/`)
Converting raw text into `all-MiniLM-L6-v2` vector embeddings stored in a FAISS index for sub-millisecond retrieval.

### 3. Agent Layer (`agents/`)
-   **FailurePredictionAgent**: Scans input for specific keywords defined in `patterns/*.yaml`.
-   **ArchitectureAgent**: consults `rules/pattern_to_service.py` to map mitigations to AWS Services.

### 4. Interface Layer (`frontend/`)
A Glassmorphism-styled Research UI consisting of:
-   **Home**: Philosophy and entry point.
-   **Analyze**: The core interactive tool.
-   **Methodology**: Technical whitepaper-style explanation.

---

## 🧪 Example Analysis

**Input:**
> "I have a user upload service where API Gateway triggers a Lambda function. The Lambda resizes images synchronously and updates a metadata table in DynamoDB (Single Partition)."

**System Output:**
-   **⚠️ Detected Risk**: `Retry Storm`
    -   *Reasoning*: Synchronous invocations can cascade failures.
    -   *Mitigation*: Implement Async Queue.
-   **⚠️ Detected Risk**: `Hot Partition`
    -   *Reasoning*: Single partition writes will throttle at scale.
    -   *Mitigation*: Sharding or UUID suffixes.
-   **🏗️ Proposed Architecture**:
    -   Added **SQS** (to decouple API Gateway and Lambda).
    -   Added **DynamoDB On-Demand** (for adaptive capacity).

---

## 🔮 Future Roadmap
-   [ ] **Terraform Generation**: Auto-convert the `proposed_architecture` JSON into deployable `.tf` files.
-   [ ] **Cost Analysis Agent**: Estimate the monthly bill of the resilient architecture.
-   [ ] **Multi-Cloud**: Support for Azure and GCP patterns.

---

*Built with ❤️ by the Failure-Driven Architecture Team.*
