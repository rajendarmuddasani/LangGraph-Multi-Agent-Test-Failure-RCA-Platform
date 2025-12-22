# Testing Guide - Multi-Agent RCA Platform

## Overview
This guide covers testing the complete RCA workflow from STDF upload to PDF report generation.

---

## Prerequisites

### 1. Environment Setup
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

cd ../frontend
npm install

# Start infrastructure services
cd ..
docker-compose up -d
```

### 2. Configure Environment Variables
Update `.env` with your API keys:
```bash
# Required for LLM integration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database (default for Docker Compose)
DATABASE_URL=postgresql+asyncpg://rca_user:rca_password@localhost:5432/rca_db
REDIS_URL=redis://localhost:6379/0
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 3. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

---

## Test Scenarios

### Scenario 1: Basic RCA Workflow (End-to-End)

**Objective**: Test complete workflow from submission to report generation

**Steps**:

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Submit RCA Request** (using curl):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/rca/submit" \
     -H "Content-Type: application/json" \
     -d '{
       "lot_id": "LOT12345",
       "wafer_id": "W01",
       "bin": 5,
       "priority": "high",
       "user_id": "test@company.com"
     }'
   ```

3. **Expected Response**:
   ```json
   {
     "session_id": "550e8400-e29b-41d4-a716-446655440000",
     "status": "queued",
     "message": "RCA analysis queued successfully"
   }
   ```

4. **Check Status** (use session_id from above):
   ```bash
   curl "http://localhost:8000/api/v1/rca/status/550e8400-e29b-41d4-a716-446655440000"
   ```

5. **Expected Workflow**:
   - Status: `queued` → `running` → `completed`
   - Progress: 0% → 17% → 33% → 50% → 67% → 83% → 100%
   - Active agents cycle through: DataAnalyst → StatisticalAnalyst, SpatialAnalyst, CorrelationHunter (parallel) → ConclusionEngine → ReportGenerator

6. **Get Results**:
   ```bash
   curl "http://localhost:8000/api/v1/rca/results/550e8400-e29b-41d4-a716-446655440000"
   ```

7. **Expected Results**:
   ```json
   {
     "session_id": "...",
     "status": "completed",
     "hypotheses": [
       {
         "rank": 1,
         "hypothesis": "Package stress (thermal/mechanical) causing peripheral die failures",
         "confidence": 0.87,
         "evidence": [...]
       },
       {
         "rank": 2,
         "hypothesis": "Solder void under peripheral die causing electrical opens",
         "confidence": 0.78,
         "evidence": [...]
       }
     ],
     "wafer_map_path": "s3://wafer-maps/LOT12345_W01_all_bins.png",
     "report_path": "s3://rca-reports/550e8400-....pdf"
   }
   ```

**Success Criteria**:
- ✅ Session created successfully
- ✅ All 6 agents execute without errors
- ✅ At least 3 hypotheses generated
- ✅ Confidence scores between 0.7-0.95
- ✅ PDF report generated
- ✅ Execution time < 60 seconds

---

### Scenario 2: Real-time WebSocket Updates

**Objective**: Verify real-time status updates via WebSocket

**Steps**:

1. **Open WebSocket Connection** (using browser console or wscat):
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/api/v1/ws/rca/SESSION_ID');
   
   ws.onmessage = (event) => {
     console.log('Received:', JSON.parse(event.data));
   };
   
   ws.onopen = () => {
     console.log('Connected');
     ws.send('ping');  // Keep-alive
   };
   ```

2. **Submit RCA** (in another terminal):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/rca/submit" \
     -H "Content-Type: application/json" \
     -d '{"lot_id": "LOT99999", "wafer_id": "W02", "bin": 5, "priority": "normal", "user_id": "test@company.com"}'
   ```

3. **Expected WebSocket Messages**:
   ```json
   {"type": "connected", "session_id": "...", "message": "Connected to RCA session updates"}
   {"type": "agent_update", "agent": "DataAnalyst", "status": "active", ...}
   {"type": "agent_update", "agent": "DataAnalyst", "status": "completed", ...}
   {"type": "agent_update", "agent": "StatisticalAnalyst", "status": "active", ...}
   {"type": "hypothesis_update", "hypothesis": "...", "confidence": 0.87, ...}
   {"type": "status_change", "status": "completed", "progress": 100}
   ```

**Success Criteria**:
- ✅ WebSocket connection established
- ✅ Real-time agent updates received
- ✅ Hypothesis updates received
- ✅ Final status change to `completed`

---

### Scenario 3: RAG Knowledge Base Search

**Objective**: Test semantic search over historical RCAs

**Steps**:

1. **Search for Similar Cases**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/rag/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Edge effect pattern on wafer periphery with thermal stress",
       "top_k": 10,
       "similarity_threshold": 0.7,
       "filters": {"bin": 5}
     }'
   ```

2. **Expected Response**:
   ```json
   {
     "query": "Edge effect pattern on wafer periphery with thermal stress",
     "results": [
       {
         "id": "rca-2024-03-15-001",
         "score": 0.92,
         "text": "Package stress causing peripheral die failures...",
         "metadata": {
           "session_id": "...",
           "lot_id": "LOT98765",
           "confidence": 0.88,
           "date": "2024-03-15"
         }
       }
     ],
     "total_results": 8
   }
   ```

3. **Find Similar to Session**:
   ```bash
   curl "http://localhost:8000/api/v1/rag/similar/SESSION_ID?top_k=5"
   ```

**Success Criteria**:
- ✅ Search returns relevant results
- ✅ Results sorted by similarity score
- ✅ Filters applied correctly
- ✅ Response time < 1 second

---

### Scenario 4: Frontend Integration Test

**Objective**: Test complete user workflow through frontend

**Steps**:

1. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate to** http://localhost:3000

3. **Submit RCA Form**:
   - Fill in Lot ID: `LOT12345`
   - Fill in Wafer ID: `W01`
   - Select Bin: `5`
   - Select Priority: `High`
   - Click "Submit RCA Request"

4. **Verify Redirect** to `/status/SESSION_ID`

5. **Check Real-time Updates**:
   - Progress bar updates from 0% to 100%
   - Agent status cards show active/completed states
   - Agent messages appear in real-time

6. **View Results**:
   - Navigate to `/results/SESSION_ID`
   - Verify hypotheses displayed with confidence scores
   - Verify wafer map preview shown
   - Click "Download Report" to get PDF

**Success Criteria**:
- ✅ Form validation works
- ✅ Real-time progress updates
- ✅ Results displayed correctly
- ✅ PDF download link works

---

## Agent-Specific Tests

### Test 1: Data Analyst Agent

**Test STDF Parsing**:
```python
from agents.data_analyst import data_analyst_agent

state = {
    "session_id": "test-123",
    "lot_id": "LOT12345",
    "wafer_id": "W01",
    "bin": 5,
    "messages": [],
}

result = await data_analyst_agent.execute(state)

assert "stdf_data" in result
assert result["stdf_data"]["die_count"] > 0
assert 0 <= result["stdf_data"]["yield"] <= 1
assert "wafer_map_path" in result
```

### Test 2: Statistical Analyst Agent

**Test Statistical Analysis**:
```python
from agents.statistical_analyst import statistical_analyst_agent

state = {
    "session_id": "test-123",
    "lot_id": "LOT12345",
    "stdf_data": {"die_count": 5000, "yield": 0.84},
    "messages": [],
}

result = await statistical_analyst_agent.execute(state)

assert "statistical_findings" in result
assert len(result["statistical_findings"]) >= 3
assert all(0 <= f["confidence"] <= 1 for f in result["statistical_findings"])
```

### Test 3: Spatial Pattern Detector

**Test Edge Detection**:
```python
from agents.spatial_pattern_detector import spatial_pattern_detector_agent

state = {
    "session_id": "test-123",
    "wafer_map_path": "s3://wafer-maps/test.png",
    "messages": [],
}

result = await spatial_pattern_detector_agent.execute(state)

assert "spatial_patterns" in result
patterns = result["spatial_patterns"]
assert any(p["pattern"] in ["edge_effect", "ring", "cluster"] for p in patterns)
```

### Test 4: Correlation Hunter

**Test Parametric Correlation**:
```python
from agents.correlation_hunter import correlation_hunter_agent

state = {
    "session_id": "test-123",
    "stdf_data": {"die_count": 5000},
    "messages": [],
}

result = await correlation_hunter_agent.execute(state)

assert "correlations" in result
correlations = result["correlations"]
assert len(correlations) >= 3
assert any(c.get("p_value", 1) < 0.05 for c in correlations)  # At least one significant
```

### Test 5: ConclusionEngine

**Test Hypothesis Generation**:
```python
from agents.conclusion_engine import conclusion_engine_agent

state = {
    "session_id": "test-123",
    "statistical_findings": [...],
    "spatial_patterns": [...],
    "correlations": [...],
    "messages": [],
}

result = await conclusion_engine_agent.execute(state)

assert "root_causes" in result
hypotheses = result["root_causes"]
assert len(hypotheses) >= 3
assert all(h["rank"] > 0 for h in hypotheses)
assert all(0 <= h["confidence"] <= 1 for h in hypotheses)
assert hypotheses[0]["confidence"] >= hypotheses[-1]["confidence"]  # Sorted by confidence
```

### Test 6: Report Generator

**Test PDF Generation**:
```python
from agents.report_generator import report_generator_agent

state = {
    "session_id": "test-123",
    "root_causes": [...],
    "statistical_findings": [...],
    "spatial_patterns": [...],
    "messages": [],
}

result = await report_generator_agent.execute(state)

assert "report_path" in result
assert result["report_path"].startswith("s3://rca-reports/")
assert result["report_path"].endswith(".pdf")
```

---

## Performance Tests

### Load Test: Concurrent RCA Sessions

**Objective**: Test 50 concurrent RCA sessions

**Script** (using `locust`):
```python
from locust import HttpUser, task, between

class RCAUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def submit_rca(self):
        self.client.post("/api/v1/rca/submit", json={
            "lot_id": f"LOT{self.environment.runner.user_count}",
            "wafer_id": "W01",
            "bin": 5,
            "priority": "normal",
            "user_id": "loadtest@company.com",
        })
```

**Run**:
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=10
```

**Success Criteria**:
- ✅ 50 concurrent sessions complete successfully
- ✅ Average response time < 200ms (API)
- ✅ RCA completion time < 5 minutes (p99)
- ✅ No 5xx errors
- ✅ Database connection pool stable

---

## Monitoring & Observability Tests

### Test 1: Prometheus Metrics

**Access**: http://localhost:9090

**Verify Metrics**:
```promql
# Request rate
rate(http_requests_total[5m])

# Latency (p99)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Agent execution time
rate(agent_execution_duration_seconds_sum[5m])
```

### Test 2: Grafana Dashboards

**Access**: http://localhost:3001

**Verify Dashboards**:
- System Metrics (CPU, memory, disk)
- Application Metrics (requests, latency, errors)
- Agent Metrics (execution time, success rate)
- Database Metrics (connections, queries)

---

## Troubleshooting

### Issue: "Database connection failed"
**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection
psql -h localhost -U rca_user -d rca_db -c "SELECT 1"

# Recreate database
docker-compose down postgres
docker-compose up -d postgres
```

### Issue: "Redis connection failed"
**Solution**:
```bash
# Check Redis
docker-compose ps redis

# Test connection
redis-cli -h localhost ping
```

### Issue: "LLM API key invalid"
**Solution**:
- Check `.env` file has valid `OPENAI_API_KEY`
- Test key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### Issue: "Agent execution timeout"
**Solution**:
- Check agent logs: `docker-compose logs backend`
- Increase timeout in `core/config.py`: `AGENT_TIMEOUT_SECONDS = 300`

---

## CI/CD Testing

### GitHub Actions Workflow

```yaml
name: Test RCA Platform

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/ -v --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Coverage Goals

**Target**: >85% code coverage

**Priority Areas**:
- ✅ Agent execution logic (critical)
- ✅ API endpoints (critical)
- ✅ Database operations (high)
- ✅ LangGraph orchestration (high)
- ✅ Error handling (high)
- ✅ Utility functions (medium)

**Generate Coverage Report**:
```bash
cd backend
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Next Steps

1. ✅ Complete all test scenarios above
2. ✅ Fix any failing tests
3. ✅ Add unit tests for each agent
4. ✅ Set up CI/CD pipeline
5. ✅ Monitor performance metrics
6. ✅ Iterate based on test results
