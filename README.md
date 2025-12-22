# P03: Multi-Agent Test Failure RCA Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Enterprise-grade multi-agent AI system that orchestrates 6 specialized agents using LangGraph to autonomously perform comprehensive root cause analysis (RCA) of semiconductor test failures. Reduces RCA time from 4-8 hours to 20-30 minutes (target) with >85% accuracy (target).

### Key Features

- **Multi-Agent Collaboration**: 6 specialized agents (Data Analyst, Statistical Analyst, Spatial Pattern Detector, Correlation Hunter, ConclusionEngine, Report Generator)
- **LangGraph State Machines**: Conditional agent routing with cycle detection and recovery
- **Shared Memory**: Blackboard architecture with PostgreSQL storage
- **RAG Integration**: Retrieval-augmented generation from 10+ years of RCA reports
- **Real-Time Updates**: WebSocket streaming of agent progress and findings
- **24/7 Autonomous Operation**: Process 500+ RCAs per day with <99.9% uptime

### Business Impact

- **Time Savings**: 4-8 hours → 20-30 minutes (target)
- **Accuracy**: >85% match with expert conclusions (target)

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    UI LAYER                          │
│  React + TypeScript + WebSocket Real-Time Updates   │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              ORCHESTRATION LAYER                     │
│         LangGraph State Machine                      │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│                 AGENT LAYER                          │
│  6 Specialized Agents (Data, Statistical, Spatial,  │
│  Correlation, ConclusionEngine, Report Generator)        │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              TOOL & MEMORY LAYER                     │
│  STDF Parser | Wafer Map CV | Stats Tests | RAG     │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│                 DATA LAYER                           │
│     PostgreSQL | Qdrant | MinIO                     │
└──────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16
- OpenAI API key (for GPT-4)

### Installation

```bash
# Clone repository
git clone https://github.com/rajendarmuddasani/LangGraph-Multi-Agent-Test-Failure-RCA-Platform.git
cd LangGraph-Multi-Agent-Test-Failure-RCA-Platform

# Set up environment
cp .env.example .env
# Edit .env with your API keys and configuration

# Start infrastructure services
docker-compose up -d postgres qdrant minio

# Install backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal, install frontend dependencies
cd frontend
npm install
npm start
```

### First RCA Submission

```bash
# Submit test RCA via API
curl -X POST http://localhost:8000/api/v1/rca/submit \
  -H "Content-Type: application/json" \
  -d '{
    "lot_id": "DEV1_LOT123",
    "wafer_id": "W05",
    "bin": 5,
    "priority": "normal"
  }'
```

Or use the web UI at `http://localhost:3000`

## Project Structure

```
P03_Multi_Agent_RCA_Platform/
├── backend/                 # FastAPI backend
│   ├── agents/             # 6 specialized agents
│   │   ├── data_analyst.py
│   │   ├── statistical_analyst.py
│   │   ├── spatial_analyst.py
│   │   ├── correlation_hunter.py
│   │   ├── conclusion_engine.py
│   │   └── report_generator.py
│   ├── tools/              # Agent tools (STDF parser, stats, etc.)
│   ├── orchestration/      # LangGraph + CrewAI
│   ├── api/                # REST endpoints
│   ├── database/           # PostgreSQL models
│   ├── vector_db/          # Qdrant integration
│   ├── auth/               # OAuth2/JWT authentication
│   └── tests/              # Unit + integration tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # React hooks
│   │   ├── api/           # API client
│   │   └── utils/         # Utilities
│   └── public/
├── k8s/                    # Kubernetes manifests
├── monitoring/             # Prometheus + Grafana
├── scripts/                # Utility scripts
├── data/                   # Sample data
├── docs/                   # Documentation
├── tests/                  # E2E tests
├── .env.example            # Environment template
├── docker-compose.yml      # Docker services
├── MANUAL_TASKS.md        # Manual setup guide
├── PRD.md                 # Product requirements
└── README.md              # This file
```

## Core Components

### 1. Multi-Agent System with LangGraph

**LangGraph State Machine**:
```python
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("data_analyst", data_analyst_agent)
workflow.add_node("statistical_analyst", statistical_analyst_agent)
workflow.add_node("spatial_analyst", spatial_analyst_agent)
workflow.add_node("conclusion_engine", conclusion_engine_agent)

workflow.set_entry_point("data_analyst")
workflow.add_edge("data_analyst", "statistical_analyst")
workflow.add_edge("statistical_analyst", "conclusion_engine")
```

### 2. RAG Integration

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma(
    collection_name="rca_reports",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large")
)

# Semantic search
similar_rcas = vectorstore.similarity_search(
    query="Edge effect DEV1 BGA436",
    k=5,
    filter={"product": "DEV1"}
)
```

### 3. Real-Time Updates

```python
# Backend WebSocket
from fastapi import WebSocket

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    async for update in agent_progress_stream(session_id):
        await websocket.send_json(update)
```

```javascript
// Frontend WebSocket client
const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  setAgentProgress(update);
};
```

## API Documentation

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rca/submit` | POST | Submit new RCA request |
| `/api/v1/rca/{id}/status` | GET | Get RCA status |
| `/api/v1/rca/{id}/results` | GET | Get RCA results |
| `/api/v1/rca/{id}/feedback` | POST | Submit user feedback |
| `/api/v1/rag/search` | POST | Search knowledge base |
| `/api/v1/reports/{id}.pdf` | GET | Download PDF report |

Full API documentation: http://localhost:8000/docs (Swagger UI)

## Configuration

### Environment Variables

See `.env.example` for full list. Key variables:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Fallback

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/rca_platform

# Vector Database
QDRANT_URL=http://localhost:6333

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET_KEY=your-256-bit-secret
OAUTH2_CLIENT_ID=azure-ad-client-id
```

### Agent Configuration

Edit `backend/config/agents.yaml`:

```yaml
agents:
  data_analyst:
    llm_model: gpt-4-turbo
    temperature: 0.0
    max_tokens: 2000
    tools: [parse_stdf, generate_wafer_map, sql_query]
  
  statistical_analyst:
    llm_model: gpt-4-turbo
    temperature: 0.0
    max_tokens: 3000
    tools: [ttest, anova, correlation, outlier_detection]
```

## Testing

```bash
# Unit tests
cd backend
pytest tests/unit -v --cov=.

# Integration tests
pytest tests/integration -v

# E2E tests (requires running services)
pytest tests/e2e -v

# Load testing
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## Deployment

### Docker Compose (Development)

```bash
docker-compose up
```

### Kubernetes (Production)

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
```

### Helm Chart (Alternative)

```bash
helm install rca-platform ./helm/rca-platform \
  --namespace rca-platform \
  --values values.production.yaml
```

## Monitoring

### Prometheus Metrics

```
# RCA throughput
rca_submissions_total{status="completed"} 450
rca_duration_seconds{quantile="0.95"} 1200  # 20 minutes

# Agent performance
agent_executions_total{agent="StatisticalAnalyst",status="success"} 420
agent_duration_seconds{agent="StatisticalAnalyst",quantile="0.95"} 120

# LLM usage
llm_tokens_total{provider="openai",type="input"} 30000
llm_api_latency_seconds{provider="openai",quantile="0.95"} 4.5
```

### Grafana Dashboards

Pre-built dashboards in `monitoring/grafana/dashboards/`:
- Operational Dashboard (RCA throughput, latency, errors)
- Business Dashboard (user adoption, satisfaction, ROI)
- ML Dashboard (agent performance, LLM usage, RAG effectiveness)

Access: http://localhost:3000 (admin / password from .env)



## Troubleshooting

### Common Issues

**Agent timeout errors**:
```bash
# Check LLM API connectivity
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"

# Increase timeout in agent config
# backend/config/agents.yaml: timeout: 600  # 10 minutes
```

**Vector search returns no results**:
```bash
# Verify Qdrant collection exists
curl http://localhost:6333/collections/rca_knowledge_base

# Re-embed knowledge base
python scripts/embed_knowledge_base.py --force
```

**WebSocket connection fails**:
```bash
# Check nginx proxy configuration
# Ensure Upgrade header is set:
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection "upgrade";
```

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open pull request

### Development Guidelines

- Follow PEP 8 (Python) and Airbnb (JavaScript) style guides
- Write unit tests for all new features (>85% coverage required)
- Update documentation for API changes
- Run linters before commit: `ruff check .` (Python), `npm run lint` (JavaScript)

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- LangChain team for LangGraph framework
- CrewAI team for hierarchical agent orchestration
- Qdrant team for vector database
- OpenAI and Anthropic for LLM APIs

## Support

- **Issue Tracker**: https://github.com/rajendarmuddasani/LangGraph-Multi-Agent-Test-Failure-RCA-Platform/issues

## Roadmap

### 1
- [ ] Self-reflection agents (agents critique own hypotheses)
- [ ] Dynamic tool creation (agents write custom Python functions)
- [ ] Multi-modal integration (shmoo plots, FA images)

### 2
- [ ] **Knowledge Graph Enhancement**: Neo4j for explicit causality relationships and parameter-defect correlations
  - Store explicit rules: "If edge_effect AND die_cracking → substrate_issue"
  - Graph-based parameter correlation tracing (param → defect relationships)
- [ ] **Domain Ontology**: Formal taxonomy for test parameters, defect types, and failure modes
  - Test parameter hierarchy: TestParam → ElectricalParam → VoltageParam
  - Defect taxonomy: PhysicalDefect → CrackDefect → DieCrack
- [ ] **Rule-Based Reasoning**: Expert rule engine for deterministic hypothesis generation
  - Example: `if spatial_pattern == "edge" and correlation["substrate_temp"] > 0.7: add_hypothesis("Substrate temperature gradient", confidence=0.9)`
  - Combine data-driven (LLM) with rule-driven (expert knowledge) approaches
- [ ] **Active Learning Loop**: Update knowledge base weights from engineer feedback (confirmed/rejected hypotheses)
  - Currently: Store feedback passively
  - Enhancement: Adjust RAG retrieval weights, retrain embeddings, update rule confidence scores
- [ ] RLHF fine-tuning (reinforcement learning from human feedback)
- [ ] On-premise LLM deployment (Llama 3.1 70B)
- [ ] Mobile app (iOS/Android)

### 3
- [ ] Cross-product learning (DEV1 insights inform DEV2 agents)
- [ ] Predictive RCA (predict failures before they occur)
- [ ] Integration with ML Data Pipeline

## Citation

If you use this platform in research or production, please cite:

```bibtex
@software{multi_agent_rca_platform,
  title={Multi-Agent Test Failure RCA Platform},
  author={Rajendar Muddasani},
  year={2025},
  version={1.0},
  url={https://github.com/rajendarmuddasani/LangGraph-Multi-Agent-Test-Failure-RCA-Platform}
}
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-22
