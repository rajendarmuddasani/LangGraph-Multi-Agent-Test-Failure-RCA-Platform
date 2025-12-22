# Quick Start Guide - Testing the RCA Platform

## Prerequisites
- Backend running on http://localhost:8000
- Docker services operational (PostgreSQL, Redis, Qdrant, MinIO)
- Virtual environment activated

## 🚀 Quick Test Commands

### 1. Health Check (5 seconds)
```bash
curl http://localhost:8000/health | jq '.'
```

### 2. Submit RCA Analysis
```bash
curl -X POST http://localhost:8000/api/v1/rca/submit \
  -H "Content-Type: application/json" \
  -d '{
    "lot_id": "TEST_LOT_001",
    "wafer_id": "W05",
    "bin": 99,
    "priority": "high",
    "user_id": "your_name"
  }' | jq '.'
```
**Save the `session_id` from the response!**

### 3. Check Status (wait 60-90s for completion)
```bash
# Replace {session_id} with your actual session ID
curl http://localhost:8000/api/v1/rca/status/{session_id} | jq '.'
```

### 4. Get Results
```bash
curl http://localhost:8000/api/v1/rca/results/{session_id} | jq '.'
```

## 🧪 Run Automated Test Suite

### Simple Test
```bash
venv/bin/python test_platform.py
```

### Comprehensive Test (recommended)
```bash
venv/bin/python test_final.py
```

This will:
- ✅ Verify backend health
- ✅ Submit a test RCA request
- ✅ Monitor workflow execution (takes ~45-90 seconds)
- ✅ Retrieve and validate results
- ✅ Verify database persistence

## 📊 Expected Results

After 60-90 seconds, you should see:
- **Status:** `completed`
- **Progress:** `100%`
- **Hypotheses:** 3 ranked root causes
- **Confidence scores:** 0.72 - 0.87
- **Evidence:** 3-4 sources per hypothesis

## 🔍 Verify Database

```bash
# Check completed sessions
docker exec feature_store_postgres psql -U rca_user -d rca_platform -c \
  "SELECT session_id, status, created_at FROM rca_sessions ORDER BY created_at DESC LIMIT 5;"

# Check generated hypotheses
docker exec feature_store_postgres psql -U rca_user -d rca_platform -c \
  "SELECT hypothesis_id, LEFT(hypothesis_text, 60) as hypothesis, confidence, rank 
   FROM hypotheses ORDER BY hypothesis_id DESC LIMIT 5;"
```

## 🐛 Troubleshooting

### Backend not responding?
```bash
# Check if backend is running
ps aux | grep uvicorn

# Restart backend
venv/bin/python start_backend.py > backend.log 2>&1 &
```

### Workflow taking too long?
- Normal execution time: 45-90 seconds
- Check backend logs: `tail -f backend.log`
- Monitor OpenAI API calls in logs

### Status endpoint timing out?
- This is expected during workflow execution
- Wait 60-90 seconds and try again
- The workflow continues in the background

## 📝 Sample Session

```bash
# Full workflow example
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/v1/rca/submit \
  -H "Content-Type: application/json" \
  -d '{"lot_id":"LOT123","wafer_id":"W01","bin":5,"priority":"high","user_id":"test"}' \
  | jq -r '.session_id')

echo "Session ID: $SESSION_ID"
echo "Waiting 90 seconds for workflow..."
sleep 90

echo "Status:"
curl -s http://localhost:8000/api/v1/rca/status/$SESSION_ID | jq '{status,progress}'

echo "Results:"
curl -s http://localhost:8000/api/v1/rca/results/$SESSION_ID | jq '{status, hypothesis_count: (.hypotheses|length)}'
```

## 🎯 Success Criteria

✅ **All tests pass if:**
- Health endpoint returns 200 OK
- RCA submission returns 202 Accepted
- Status eventually shows "completed"
- Results contain 3 hypotheses with evidence
- Database shows persisted data

---

**Platform is ready for testing! 🚀**
