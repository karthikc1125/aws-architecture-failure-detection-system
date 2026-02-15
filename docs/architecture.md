# Architecture
## Overview
The system follows a RAG + Agentic workflow.
1. **User Input** -> **Orchestrator**
2. **Orchestrator** -> **Knowledge Retrieval** (Vector Store)
3. **Orchestrator** -> **Failure Agent** (Identifies Risks)
4. **Orchestrator** -> **Architecture Agent** (Mitigates Risks)
5. **Orchestrator** -> **Reviewer Agent** (Validates)
6. **Orchestrator** -> **Final Output**

## Components
- **Vector Store**: FAISS index of historical incidents.
- **Rule Engine**: Deterministic dictionary mappings.
- **Agents**: Stateless LLM calls with specific prompts.
