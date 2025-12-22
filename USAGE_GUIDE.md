# Multi-Agent RCA Platform - Usage Guide

## 🚀 Quick Start

This guide shows you how to use the complete RCA platform with both backend and frontend.

---

## Prerequisites

Before starting, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Node.js 18+ and npm installed
- ✅ PostgreSQL database running
- ✅ `.env` file configured in the backend directory

---

## Step 1: Start the Backend API

### 1.1 Navigate to Backend Directory
```bash
cd backend
```

### 1.2 Activate Virtual Environment (if using one)
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 1.3 Install Python Dependencies (first time only)
```bash
pip install -r requirements.txt
```

### 1.4 Start the FastAPI Server
```bash
uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Backend Status:** The API is now running at `http://localhost:8000`

**📚 API Documentation:** Open `http://localhost:8000/docs` to view the interactive Swagger UI

---

## Step 2: Start the Frontend

### 2.1 Open a New Terminal Window
Keep the backend terminal running, and open a second terminal.

### 2.2 Navigate to Frontend Directory
```bash
cd frontend
```

### 2.3 Install Node Dependencies (first time only)
```bash
npm install
```

### 2.4 Start the Development Server
```bash
npm run dev
```

**Expected Output:**
```
VITE v5.4.21  ready in 153 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**✅ Frontend Status:** The application is now running at `http://localhost:3000`

---

## Step 3: Using the Application

### 3.1 Access the Dashboard

1. Open your browser and navigate to: **`http://localhost:3000`**
2. You'll see the **RCA Analysis Dashboard** with a list of recent analyses
3. If no sessions exist yet, you'll see a prompt to create a new analysis

**Screenshot Preview:**
```
┌─────────────────────────────────────────────────────────┐
│ RCA Analysis Dashboard          [+ New RCA Analysis]   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   📋 No RCA sessions                                    │
│   Get started by creating a new RCA analysis.          │
│                                                          │
│              [New RCA Analysis]                         │
└─────────────────────────────────────────────────────────┘
```

---

### 3.2 Submit a New RCA Analysis

1. Click **"New RCA Analysis"** button
2. You'll be redirected to the **Submit RCA** page
3. Fill in the required fields:

   - **Lot ID:** Enter the manufacturing lot identifier (e.g., `LOT-2024-001`)
   - **Wafer ID:** Enter the wafer identifier (e.g., `W123`)
   - **Bin Number:** Enter the failure bin number (e.g., `5`)
   - **Priority:** Select one:
     - `Low` - Standard processing
     - `Normal` - Regular priority
     - `High` - Expedited analysis
     - `Critical` - Immediate attention required
   - **User ID:** Your identification (e.g., `user@company.com`)

4. Click **"Submit RCA Request"**

**Example Form:**
```
┌─────────────────────────────────────────┐
│ Submit RCA Analysis                     │
├─────────────────────────────────────────┤
│ Lot ID:      [LOT-2024-001        ]   │
│ Wafer ID:    [W123                ]   │
│ Bin:         [5                   ]   │
│ Priority:    [High ▼              ]   │
│ User ID:     [engineer@fab.com    ]   │
│                                         │
│         [Submit RCA Request]            │
└─────────────────────────────────────────┘
```

**✅ Expected Response:**
- You'll receive a **session ID** (e.g., `abc123-def456-...`)
- You'll be automatically redirected to the **Status** page

---

### 3.3 Monitor RCA Analysis Progress

After submission, you're taken to the **RCA Status** page which shows:

1. **Overall Progress Bar** - Shows completion percentage (0-100%)
2. **Session Status** - Current state:
   - `QUEUED` - Waiting to start
   - `RUNNING` - Analysis in progress
   - `COMPLETED` - Finished successfully
   - `FAILED` - Error occurred

3. **Agent Status Cards** - Shows each AI agent:
   - **Agent Name** (e.g., Data Retrieval Agent, Hypothesis Generator)
   - **Status** (Queued, Running, Completed, Failed)
   - **Progress** (0-100%)
   - **Current Task** (e.g., "Fetching electrical test data...")

**Status Page Preview:**
```
┌──────────────────────────────────────────────────────────┐
│ ← Back to Dashboard                                      │
│                                                           │
│ RCA Analysis Status                                      │
│ Session ID: abc123-def456-...                           │
├──────────────────────────────────────────────────────────┤
│ Status: RUNNING    Overall Progress: ████████░░ 75%    │
│                                                           │
│ Agent Status:                                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Data Retrieval Agent              ✓ COMPLETED      │ │
│ │ Fetching electrical test data     ████████████ 100% │ │
│ └─────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Hypothesis Generator              ⟳ RUNNING        │ │
│ │ Analyzing failure patterns        ████████░░░ 80%   │ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**⏱️ Typical Analysis Time:** 45-90 seconds

**🔄 Auto-Refresh:** The page automatically updates every 3 seconds

---

### 3.4 View Results

Once the status shows **COMPLETED**:

1. Click the **"View Results →"** button
2. Or navigate to: `http://localhost:3000/results/{session_id}`

The **Results** page displays:

#### **Metadata Section**
- Lot ID
- Wafer ID
- Defect Type

#### **Hypotheses (Ranked by Confidence)**
Each hypothesis card shows:
- **Rank Badge** (1, 2, 3, etc.)
- **Hypothesis Description** - Root cause explanation
- **Confidence Score** - Color-coded:
  - 🟢 **High** (80-100%) - Green
  - 🟡 **Medium** (60-79%) - Yellow
  - 🔴 **Low** (0-59%) - Red
- **Supporting Evidence** - List of evidence items with:
  - Evidence Type (e.g., Historical Data, Test Results)
  - Description
  - Individual confidence percentage
- **Recommended Actions** - Suggested next steps

**Results Page Preview:**
```
┌──────────────────────────────────────────────────────────┐
│ ← Back to Dashboard                                      │
│                                                           │
│ RCA Analysis Results                                     │
│ Session ID: abc123-def456-...                           │
│ Lot: LOT-2024-001 | Wafer: W123 | Defect: Short         │
├──────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐  │
│ │ [1] Metal Layer Contamination      🟢 High (85%)   │  │
│ │ ████████████████████░░ 85%                         │  │
│ │                                                     │  │
│ │ Supporting Evidence:                                │  │
│ │ ▌ HISTORICAL DATA                          92%     │  │
│ │ ▌ Similar defects in adjacent wafers                │  │
│ │                                                     │  │
│ │ ▌ TEST RESULTS                             80%     │  │
│ │ ▌ Elevated metal particulates detected              │  │
│ │                                                     │  │
│ │ Recommended Actions:                                │  │
│ │ • Inspect deposition chamber for contamination     │  │
│ │ • Review clean room protocols                       │  │
│ └────────────────────────────────────────────────────┘  │
│                                                           │
│ ┌────────────────────────────────────────────────────┐  │
│ │ [2] Photolithography Misalignment  🟡 Medium (72%) │  │
│ │ ██████████████░░░░░░ 72%                           │  │
│ │ ...                                                 │  │
│ └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Step 4: Navigate Between Pages

The application has 4 main pages:

1. **Dashboard (`/`)** - View all RCA sessions
2. **Submit RCA (`/submit`)** - Create new analysis
3. **Status (`/status/{session_id}`)** - Monitor progress
4. **Results (`/results/{session_id}`)** - View hypotheses

**Navigation Tips:**
- Use the **"← Back to Dashboard"** link on any page
- Click session entries on the Dashboard to view their status
- The **"View Results →"** button appears when analysis completes

---

## Step 5: Testing the Complete Workflow

### End-to-End Test Scenario

Follow these steps to verify everything works:

1. **Start Backend:**
   ```bash
   cd backend && uvicorn main:app --reload --port 8000
   ```
   Wait for: `Application startup complete.`

2. **Start Frontend:**
   ```bash
   cd frontend && npm run dev
   ```
   Wait for: `Local: http://localhost:3000/`

3. **Submit Test Analysis:**
   - Navigate to `http://localhost:3000`
   - Click "New RCA Analysis"
   - Fill form:
     - Lot ID: `TEST-LOT-001`
     - Wafer ID: `TEST-W1`
     - Bin: `5`
     - Priority: `High`
     - User ID: `test@example.com`
   - Click "Submit"

4. **Watch Status Page:**
   - Observe progress bar updating
   - Watch agent statuses change
   - Wait for "COMPLETED" status (~60 seconds)

5. **View Results:**
   - Click "View Results →"
   - Verify hypotheses are displayed
   - Check confidence scores and evidence
   - Verify rank ordering (1, 2, 3, etc.)

**✅ Success Criteria:**
- Backend responds without errors
- Frontend loads without console errors
- Submission creates a session
- Status page shows agent progress
- Results page displays ranked hypotheses

---

## Troubleshooting

### Issue: Backend Won't Start

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

---

### Issue: Frontend Build Fails

**Symptoms:**
```
Cannot find module './pages/Dashboard'
```

**Solution:**
All page components have been created. Run:
```bash
cd frontend
npm install
npm run build
```

---

### Issue: API Connection Error

**Symptoms:**
Frontend shows: `Failed to fetch status: Failed to fetch`

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check Vite proxy configuration in `vite.config.ts`
3. Ensure no CORS errors in browser console

---

### Issue: Port Already in Use

**Symptoms:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution:**
```bash
# Find and kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- --port 3001
```

---

## API Endpoints Reference

### Backend API (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/rca/submit` | Submit new RCA analysis |
| `GET` | `/api/v1/rca/status/{session_id}` | Get analysis status |
| `GET` | `/api/v1/rca/results/{session_id}` | Get analysis results |
| `GET` | `/health` | Health check endpoint |

### Example API Call

**Submit RCA:**
```bash
curl -X POST http://localhost:8000/api/v1/rca/submit \
  -H "Content-Type: application/json" \
  -d '{
    "lot_id": "LOT-2024-001",
    "wafer_id": "W123",
    "bin": 5,
    "priority": "high",
    "user_id": "engineer@fab.com"
  }'
```

**Response:**
```json
{
  "session_id": "abc123-def456-...",
  "status": "queued",
  "message": "RCA analysis queued successfully"
}
```

---

## Production Deployment

### Backend Deployment

1. **Use Production ASGI Server:**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

2. **Set Environment Variables:**
   ```bash
   export DATABASE_URL=postgresql://user:pass@host:5432/db
   export REDIS_URL=redis://localhost:6379
   export SECRET_KEY=your-secret-key
   ```

3. **Enable HTTPS:**
   Use a reverse proxy (Nginx/Apache) with SSL certificates

### Frontend Deployment

1. **Build for Production:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve Static Files:**
   ```bash
   npm install -g serve
   serve -s dist -l 3000
   ```

3. **Or Deploy to:**
   - Vercel: `vercel deploy`
   - Netlify: `netlify deploy --prod`
   - AWS S3 + CloudFront
   - Docker container

---

## Architecture Overview

```
┌──────────────────┐          ┌──────────────────┐
│   Frontend       │          │    Backend       │
│   (React + TS)   │◄────────►│   (FastAPI)      │
│   Port 3000      │   HTTP   │   Port 8000      │
└──────────────────┘          └────────┬─────────┘
                                       │
                              ┌────────┴─────────┐
                              │   PostgreSQL     │
                              │   Database       │
                              └──────────────────┘
                                       │
                              ┌────────┴─────────┐
                              │  6 AI Agents     │
                              │  (Multi-Agent    │
                              │   Orchestration) │
                              └──────────────────┘
```

### Tech Stack

**Frontend:**
- React 18
- TypeScript
- React Router
- TailwindCSS
- Vite

**Backend:**
- FastAPI
- SQLAlchemy
- PostgreSQL
- LangChain/CrewAI
- Redis (for caching)

---

## Support & Contact

For issues or questions:
- Check logs in backend terminal
- Check browser console for frontend errors
- Review API documentation: `http://localhost:8000/docs`
- Contact platform administrator

---

## Next Steps

Now that your platform is running:

1. ✅ **Integrate with Real Data Sources:**
   - Connect to manufacturing databases
   - Link electrical test systems
   - Import historical failure data

2. ✅ **Customize AI Agents:**
   - Adjust agent prompts in `backend/agents/`
   - Add domain-specific knowledge
   - Fine-tune confidence thresholds

3. ✅ **Enhance Frontend:**
   - Add data visualizations (charts, graphs)
   - Implement user authentication
   - Create admin dashboard

4. ✅ **Monitor Performance:**
   - Set up logging and monitoring
   - Track analysis times
   - Monitor agent success rates

---

## 🎉 Congratulations!

You now have a fully functional Multi-Agent RCA Platform running end-to-end. Happy analyzing! 🚀
