# Multi-Agent RCA Platform - Architecture & Setup Guide

## 🎯 Project Overview

**Production-ready multi-agent AI system for autonomous semiconductor test failure root cause analysis (RCA)**

Reduces RCA time from **4-8 hours** (manual) to **20-30 minutes** (autonomous) with **>85% accuracy**.

---

## 🏗️ System Architecture

### Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│                   FRONTEND LAYER                       │
│        React + TypeScript + WebSocket Updates         │
│                  (Port 3000)                           │
└───────────────────────┬────────────────────────────────┘
                        │ HTTP/WebSocket
┌───────────────────────▼────────────────────────────────┐
│                   BACKEND API LAYER                    │
│        FastAPI + Uvicorn (Python 3.11+)               │
│                  (Port 8000)                           │
│  ┌──────────────────────────────────────────────────┐ │
│  │  REST API | WebSocket | Health Checks            │ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│              ORCHESTRATION LAYER                       │
│              LangGraph State Machine                   │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Workflow: DataAnalyst → Parallel Analysis →     │ │
│  │  ConclusionEngine → ReportGenerator              │ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│                   AGENT LAYER                          │
│            6 Specialized AI Agents                     │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Data Analyst      - STDF parsing & wafer maps │ │
│  │ 2. Statistical       - Statistical tests         │ │
│  │ 3. Spatial Analyst   - Pattern detection         │ │
│  │ 4. Correlation       - Feature correlation       │ │
│  │ 5. ConclusionEngine  - Hypothesis ranking        │ │
│  │ 6. Report Generator  - PDF generation            │ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│                  TOOLS & MEMORY LAYER                  │
│  ┌──────────────────────────────────────────────────┐ │
│  │ STDF Parser | Wafer Map CV | Statistical Tests  │ │
│  │ RAG Knowledge Base | In-Memory Cache             │ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│                   DATA LAYER                           │
│  ┌──────────────────────────────────────────────────┐ │
│  │ PostgreSQL    - Structured data & metadata       │ │
│  │ Qdrant        - Vector embeddings for RAG        │ │
│  │ MinIO         - Object storage (files, reports)  │ │
│  │ In-Memory     - Fast cache (TTL support)         │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 📊 Component Details

### Frontend (React + TypeScript)
- **Technology**: React 18, TypeScript, Vite
- **Features**: Real-time WebSocket updates, responsive UI, interactive dashboards
- **Port**: 3000
- **Why TypeScript**: Type-safe JavaScript - catches errors at compile time, better IDE support
- **Why WebSocket**: Real-time bidirectional communication for live agent progress updates

### Backend (FastAPI + Python)
- **Technology**: FastAPI, Python 3.11+, Async/await
- **Features**: REST API, WebSocket streaming, health monitoring
- **Port**: 8000
- **Why FastAPI**: High performance, async support, automatic API documentation

### Orchestration (LangGraph)
- **Technology**: LangGraph state machines
- **Features**: Conditional routing, parallel execution, cycle detection
- **Workflow**: Sequential + parallel agent execution

### Agents (6 Specialized)

#### 1. **Data Analyst**
- Parses STDF (semiconductor test data format) files
- Generates wafer maps
- Extracts key metrics (yield, failure patterns)

#### 2. **Statistical Analyst**
- Runs statistical tests (t-test, chi-square, ANOVA)
- Identifies significant deviations
- Calculates confidence intervals

#### 3. **Spatial Analyst**
- Analyzes wafer map patterns using OpenCV
- Detects edge effects, center clustering, quadrant patterns
- Identifies spatial correlations

#### 4. **Correlation Hunter**
- Finds correlations between test parameters
- Identifies process-failure relationships
- Uses multivariate analysis

#### 5. **ConclusionEngine** (formerly Synthesizer)
- Aggregates findings from all agents
- Uses GPT-4 to generate ranked hypotheses
- Queries RAG knowledge base for similar cases
- Ranks by confidence score with supporting evidence

#### 6. **Report Generator**
- Generates comprehensive PDF reports
- Includes visualizations, evidence, recommendations
- Production-ready formatting

### Data Storage

#### PostgreSQL
- **Purpose**: Structured data and metadata
- **Stores**: RCA sessions, agent messages, hypotheses, user feedback
- **Why**: ACID compliance, relational integrity, production-grade

#### Qdrant
- **Purpose**: Vector database for RAG
- **Stores**: Embeddings of historical RCA reports
- **Why**: Fast semantic search for similar failure cases

#### MinIO
- **Purpose**: S3-compatible object storage
- **Stores**: STDF files, wafer map images, PDF reports
- **Why**: Handles large binary files efficiently

#### In-Memory Cache
- **Purpose**: Fast temporary storage
- **Stores**: Parsed STDF data, agent status
- **Why**: Speeds up repeated operations, TTL support

---

## 🛠️ Technology Stack

### Core Framework
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Backend | FastAPI | 0.115+ | Async web framework |
| Frontend | React | 18.2+ | UI framework |
| Language | Python | 3.11+ | Backend logic |
| Language | TypeScript | 5.0+ | Frontend logic |

### AI/ML
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Orchestration | LangGraph | 0.2+ | Agent workflow |
| LLM Framework | LangChain | 0.2+ | LLM integration |
| LLM | OpenAI GPT-4 | API | Hypothesis generation |
| Embeddings | OpenAI Ada | API | Vector embeddings |

### Data
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Database | PostgreSQL | 16+ | Relational data |
| Vector DB | Qdrant | 1.11+ | Similarity search |
| Object Storage | MinIO | Latest | File storage |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Migration | Alembic | 1.13+ | Schema versioning |

### DevOps
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Containerization | Docker | 20.10+ | Service isolation |
| Orchestration | Docker Compose | 2.0+ | Multi-container |
| Monitoring | Prometheus | Latest | Metrics collection |
| Visualization | Grafana | Latest | Dashboards |

---

## 📁 Project Structure

```
LangGraph-Multi-Agent-Test-Failure-RCA-Platform/
├── backend/                          # FastAPI backend
│   ├── agents/                      # 6 specialized agents
│   │   ├── data_analyst.py
│   │   ├── statistical_analyst.py
│   │   ├── spatial_analyst.py
│   │   ├── correlation_hunter.py
│   │   ├── conclusion_engine.py     # Renamed from synthesizer
│   │   └── report_generator.py
│   ├── api/                         # REST endpoints
│   │   └── v1/
│   │       ├── rca.py              # RCA endpoints
│   │       ├── rag.py              # RAG search
│   │       └── websocket.py        # Real-time updates
│   ├── orchestration/               # LangGraph workflows
│   │   └── langgraph_orchestrator.py
│   ├── core/                        # Configuration & utilities
│   │   ├── config.py               # Settings management
│   │   ├── simple_cache.py         # In-memory cache
│   │   └── cache.py                # Cache interface
│   ├── database/                    # PostgreSQL models
│   │   ├── models.py               # SQLAlchemy models
│   │   └── session.py              # DB connection
│   ├── schemas/                     # Pydantic schemas
│   │   └── rca.py                  # Request/response models
│   ├── tools/                       # Agent tools
│   ├── alembic/                     # Database migrations
│   ├── Dockerfile                   # Backend container
│   ├── requirements.txt             # Python dependencies
│   └── main.py                      # FastAPI application
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── api/                    # API client
│   │   └── utils/                  # Utilities
│   ├── package.json                # Node dependencies
│   └── vite.config.ts              # Vite configuration
│
├── docker-compose.yml               # Docker services
├── .env.example                     # Environment template
│
├── README.md                        # Main documentation
├── ARCHITECTURE.md                  # This file
├── SIMPLIFICATION_SUMMARY.md        # Recent changes
├── PROJECT_STATUS.md                # Implementation status
├── MANUAL_TASKS.md                  # Setup instructions
├── QUICK_START.md                   # Quick start guide
└── PRD.md                           # Product requirements
```

---

## 🚀 Quick Start

### Prerequisites
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.11+
- **Node.js** 18+
- **OpenAI API Key**

### 1. Clone Repository
```bash
git clone <repository-url>
cd multi-agent-rca-platform
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Start Infrastructure
```bash
# Start all services (recommended)
docker compose up -d

# Or start individual services
docker compose up -d postgres qdrant minio
```

### 4. Start Backend (Development)
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head  # Run migrations
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```

### 6. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

---

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

```bash
# LLM API
OPENAI_API_KEY=sk-your-key-here

# Database
DATABASE_URL=postgresql+asyncpg://rca_user:rca_password@localhost:5432/rca_platform

# Vector Database
QDRANT_URL=http://localhost:6333

# Object Storage
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 📖 Key Design Decisions

### Why LangGraph (Not CrewAI)?
- **Simpler**: Single orchestration framework
- **Flexible**: Custom workflows, conditional routing
- **Transparent**: Clear state machine visualization
- **Sufficient**: Handles all our agent coordination needs

### Why In-Memory Cache (Not Redis)?
- **Simpler setup**: No external dependencies for development
- **Fast**: Direct memory access
- **Sufficient**: Handles caching needs with TTL support
- **Upgradeable**: Easy to switch to Redis for production

### Why PostgreSQL?
- **Proven**: Industry standard for production
- **ACID**: Data integrity guarantees
- **Features**: JSONB, full-text search, indexes
- **Free**: Open source, no licensing costs

### Why MinIO (Not S3)?
- **Self-hosted**: Full control, no cloud costs
- **S3-compatible**: Easy migration to AWS later
- **Fast**: Local storage performance
- **Docker-friendly**: Simple deployment

---

## 🔍 Agent Workflow & LangGraph Orchestration

### Complete Agent Flow (Mermaid Diagram)

```mermaid
graph TB
    Start([User Submits RCA Request]) --> Queue[RCA Session Created]
    Queue --> LG[LangGraph Orchestrator Starts]
    
    LG --> DA[Agent 1: Data Analyst]
    DA --> Parse{Parse STDF File}
    Parse --> WaferMap[Generate Wafer Map]
    WaferMap --> Extract[Extract Metrics: Yield, Bin Counts]
    
    Extract --> Parallel{Parallel Execution}
    
    Parallel --> SA[Agent 2: Statistical Analyst]
    Parallel --> SPA[Agent 3: Spatial Analyst]
    Parallel --> CH[Agent 4: Correlation Hunter]
    
    SA --> Stats[Run t-tests, ANOVA, chi-square]
    SPA --> Pattern[Detect edge/center/quadrant patterns]
    CH --> Corr[Find parameter correlations]
    
    Stats --> CE[Agent 5: ConclusionEngine]
    Pattern --> CE
    Corr --> CE
    
    CE --> GPT4{Use GPT-4 to Synthesize}
    GPT4 --> RAG[Query RAG Knowledge Base]
    RAG --> Rank[Rank Hypotheses by Confidence]
    
    Rank --> RG[Agent 6: Report Generator]
    RG --> PDF[Generate PDF Report]
    RG --> Viz[Create Visualizations]
    
    PDF --> Store[(Store Results)]
    Viz --> Store
    
    Store --> WS[WebSocket: Notify Frontend]
    WS --> End([User Reviews Report])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style LG fill:#fff3cd
    style CE fill:#f8d7da
    style GPT4 fill:#d1ecf1
    style Store fill:#d4edda
```

### LangGraph State Machine

```mermaid
stateDiagram-v2
    [*] --> DataAnalyst: Start RCA
    
    DataAnalyst --> ParallelGate: Data Parsed
    
    ParallelGate --> StatisticalAnalyst
    ParallelGate --> SpatialAnalyst
    ParallelGate --> CorrelationHunter
    
    StatisticalAnalyst --> ConclusionEngine: Analysis Complete
    SpatialAnalyst --> ConclusionEngine: Patterns Found
    CorrelationHunter --> ConclusionEngine: Correlations Identified
    
    ConclusionEngine --> ReportGenerator: Hypotheses Ranked
    
    ReportGenerator --> [*]: Report Generated
    
    note right of DataAnalyst
        Parses STDF
        Generates wafer maps
        Extracts metrics
    end note
    
    note right of ConclusionEngine
        Uses GPT-4
        Queries RAG database
        Ranks hypotheses
    end note
```

### Agent Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant LG as LangGraph
    participant DA as DataAnalyst
    participant SA as Statistical
    participant SP as Spatial  
    participant CH as Correlation
    participant CE as ConclusionEngine
    participant RG as ReportGen
    participant DB as PostgreSQL
    
    User->>API: Submit RCA Request
    API->>DB: Create Session
    API->>LG: Start Workflow
    
    LG->>DA: Execute
    DA->>DA: Parse STDF
    DA->>DB: Store Parsed Data
    
    par Parallel Analysis
        LG->>SA: Analyze Statistics
        LG->>SP: Detect Patterns
        LG->>CH: Find Correlations
    end
    
    SA->>DB: Store Findings
    SP->>DB: Store Patterns
    CH->>DB: Store Correlations
    
    LG->>CE: Synthesize All
    CE->>CE: Query GPT-4
    CE->>DB: Query RAG (Qdrant)
    CE->>DB: Store Hypotheses
    
    LG->>RG: Generate Report
    RG->>RG: Create PDF
    RG->>DB: Store Report
    
    API->>User: Report Ready (WebSocket)
```

---

## 📊 Data Flow

### RCA Submission
```
User → FastAPI → Create Session → Queue → LangGraph Workflow
```

### Agent Execution
```
LangGraph → Agent → Tool Execution → Update State → Next Agent
```

### Real-Time Updates
```
Agent Progress → WebSocket → Frontend → UI Update
```

### Result Storage
```
Hypotheses → PostgreSQL
Wafer Maps → MinIO
Embeddings → Qdrant
```

---

## 🎓 Learning Resources

### For Understanding Agents
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Multi-Agent Systems Explained](https://www.anthropic.com/research/multi-agent)

### For Semiconductor RCA
- STDF File Format Specification
- Wafer Map Analysis Techniques
- Statistical Process Control (SPC)

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Built with ❤️ for semiconductor engineering automation**

*Last Updated: December 2025*
