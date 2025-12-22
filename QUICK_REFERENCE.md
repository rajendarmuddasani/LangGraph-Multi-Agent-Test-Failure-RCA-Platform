# Quick Reference Card - Multi-Agent RCA Platform

## 🚀 Quick Start Commands

```bash
# Setup (one-time)
./start.sh

# Start services
docker-compose up -d

# Run migrations
cd backend && alembic upgrade head

# Start backend
uvicorn main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend && npm run dev
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rca/submit` | Submit new RCA request |
| GET | `/api/v1/rca/status/{session_id}` | Get RCA status |
| GET | `/api/v1/rca/results/{session_id}` | Get RCA results |
| GET | `/api/v1/rca/messages/{session_id}` | Get agent messages |
| POST | `/api/v1/rca/feedback/{session_id}` | Submit user feedback |
| GET | `/api/v1/rca/download/{session_id}/report` | Download PDF report |
| POST | `/api/v1/rag/search` | RAG semantic search |
| WS | `/api/v1/ws/rca/{session_id}` | WebSocket real-time updates |

## 🤖 Agent Workflow

```
DataAnalyst → [Statistical + Spatial + Correlation] → ConclusionEngine → ReportGenerator
     ↓              ↓          ↓          ↓               ↓             ↓
  STDF Parse   T-tests    Edge Det.  Pearson r     RAG Query    PDF Gen
  Wafer Map    ANOVA      Clusters   Feature Imp   Hypotheses   S3 Upload
```

## 🔑 Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...                    # For LLM agents

# Database (defaults work with Docker Compose)
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Optional
ANTHROPIC_API_KEY=sk-ant-...             # Fallback LLM
LOG_LEVEL=INFO
API_RATE_LIMIT=100
```

## 📊 Agent Capabilities

| Agent | Key Tools | Confidence Range |
|-------|-----------|------------------|
| **DataAnalyst** | STDF parser, wafer map generator | 0.85-0.95 |
| **StatisticalAnalyst** | T-test, ANOVA, control charts, outliers | 0.60-0.95 |
| **SpatialPatternDetector** | Edge detection, DBSCAN, radial analysis | 0.50-0.92 |
| **CorrelationHunter** | Pearson/Spearman, Random Forest, time-series | 0.50-0.90 |
| **ConclusionEngine** | RAG query, LLM synthesis, hypothesis ranking | 0.50-0.87 |
| **ReportGenerator** | ReportLab PDF, S3 upload | 1.0 |

## 🔬 Testing Shortcuts

```bash
# Submit test RCA
curl -X POST http://localhost:8000/api/v1/rca/submit \
  -H "Content-Type: application/json" \
  -d '{"lot_id":"LOT123","wafer_id":"W01","bin":5,"priority":"high","user_id":"test@co.com"}'

# Check status (replace {id})
curl http://localhost:8000/api/v1/rca/status/{id}

# Get results
curl http://localhost:8000/api/v1/rca/results/{id}

# RAG search
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query":"edge effect","top_k":10,"similarity_threshold":0.7}'

# WebSocket test (browser console)
ws = new WebSocket('ws://localhost:8000/api/v1/ws/rca/{id}');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

## 🗄️ Database Schema

```sql
-- Key tables
rca_sessions         -- RCA session metadata
agents               -- Agent execution records  
agent_messages       -- Inter-agent communication (blackboard)
hypotheses           -- Ranked root cause hypotheses
rca_reports          -- Generated PDF reports
user_feedback        -- User ratings for hypotheses
stdf_data_cache      -- Cached STDF parsing results
wafer_maps           -- Generated wafer map images
```

## 🐛 Debug Commands

```bash
# Check service health
docker-compose ps
curl http://localhost:8000/health

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Database access
docker-compose exec postgres psql -U rca_user -d rca_db

# Redis CLI
docker-compose exec redis redis-cli

# Clear cache
docker-compose exec redis redis-cli FLUSHALL

# Restart backend
docker-compose restart backend
```

## 📈 Monitoring URLs

- **API Docs**: http://localhost:8000/api/v1/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **MinIO Console**: http://localhost:9001
- **Frontend**: http://localhost:3000

## 🔧 Common Issues

| Issue | Solution |
|-------|----------|
| "Database connection failed" | `docker-compose restart postgres` |
| "Redis connection failed" | `docker-compose restart redis` |
| "LLM API error" | Check `OPENAI_API_KEY` in `.env` |
| "Import errors in Python" | `pip install -r requirements.txt` |
| "Agent execution timeout" | Increase `AGENT_TIMEOUT_SECONDS` in config |
| "Frontend won't start" | `cd frontend && npm install` |

## 📦 Key Dependencies

```bash
# Backend
fastapi==0.115.0          # Web framework
langgraph==0.2.28         # Multi-agent orchestration
langchain==0.2.16         # LLM framework
openai==1.45.0            # OpenAI GPT-4
anthropic==0.34.2         # Claude 3.5
sqlalchemy==2.0.35        # ORM
qdrant-client==1.11.2     # Vector DB
reportlab==4.2.0          # PDF generation
scipy==1.13.1             # Statistics
scikit-learn==1.5.1       # ML
opencv-python==4.10.0     # Computer vision

# Frontend
react@18.2.0              # UI framework
@tanstack/react-query@5   # Data fetching
axios@1.6.5               # HTTP client
recharts@2.10.0           # Charts
```

## 🎯 Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| RCA completion (p99) | <5 min | TBD |
| API response (p50) | <200ms | TBD |
| RAG search | <1s | TBD |
| Concurrent sessions | 50+ | TBD |
| Hypothesis accuracy | >85% | TBD |

## 📝 Code Structure

```
backend/
  agents/              # 6 AI agents
  api/v1/             # REST + WebSocket endpoints
  orchestration/      # LangGraph workflow
  database/           # SQLAlchemy models
  core/               # Config, logging, cache
  alembic/            # DB migrations
  
frontend/
  src/
    pages/            # React pages
    api/              # API client
    
docs/
  README.md           # Architecture overview
  MANUAL_TASKS.md     # Configuration guide
  TESTING_GUIDE.md    # Testing scenarios
  PROJECT_STATUS.md   # Implementation status
```

## 🎨 Agent Prompt Templates

```python
# Statistical Analyst
"You are an expert statistician analyzing semiconductor test data. 
Identify significant deviations (p<0.05) and provide actionable insights."

# Spatial Pattern Detector  
"You are a wafer map analysis expert. Classify patterns as edge, ring, 
cluster, or random. Focus on patterns with >0.8 confidence."

# Correlation Hunter
"You are a parametric test correlation expert. Find significant 
correlations (|r|>0.7, p<0.05) between test parameters."

# ConclusionEngine
"You are an expert failure analysis engineer with 20+ years experience.
Synthesize multi-agent findings into ranked hypotheses with evidence."
```

## 🚦 RCA Status Flow

```
queued → running → completed
                → failed
                → partially_completed
```

## 🎓 Learning Resources

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **FastAPI**: https://fastapi.tiangolo.com/
- **ReportLab**: https://www.reportlab.com/docs/
- **Qdrant**: https://qdrant.tech/documentation/
- **OpenAI API**: https://platform.openai.com/docs/

---

**Tip**: Keep this card handy while developing! 📌
