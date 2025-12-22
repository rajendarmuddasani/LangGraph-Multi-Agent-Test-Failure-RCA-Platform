# 🚀 How to Use the RCA Platform

## Quick Start Guide

Your platform is **LIVE** at: **http://localhost:3000**

---

## 📋 Step-by-Step: Submit an RCA Analysis

### 1. **Access the Application**
- Open your browser
- Navigate to: `http://localhost:3000`
- You'll see the Dashboard (currently empty)

### 2. **Click "New RCA" Button**
- Top right of the page
- Or click "Submit RCA" in the navigation bar
- Or go directly to: `http://localhost:3000/submit`

### 3. **Fill Out the Form**

The form has 5 fields you need to complete:

#### **Field 1: Lot ID**
- **What it is:** Manufacturing lot identifier
- **Example:** `LOT-2024-001` or `LOT123`
- **Purpose:** Identifies which manufacturing batch has the issue
- **Required:** Yes

#### **Field 2: Wafer ID**
- **What it is:** Specific wafer within the lot
- **Example:** `W123` or `WAFER-001`
- **Purpose:** Pinpoints the exact wafer with defects
- **Required:** Yes

#### **Field 3: Bin Number**
- **What it is:** Failure bin classification number
- **Example:** `5` (usually 1-20)
- **Purpose:** Categorizes the type of failure detected
- **Common Values:**
  - Bin 1: Pass
  - Bin 5-10: Electrical failures
  - Bin 11-15: Physical defects
- **Required:** Yes

#### **Field 4: Priority Level**
- **What it is:** Urgency of the analysis
- **Options:**
  - 🟢 **Low Priority:** Can wait, not urgent
  - 🟡 **Normal Priority:** Regular processing (default)
  - 🟠 **High Priority:** Needs faster attention
  - 🔴 **Critical Priority:** Immediate analysis required
- **Purpose:** Determines processing order
- **Required:** Yes (defaults to Normal)

#### **Field 5: User ID**
- **What it is:** Your email or username
- **Example:** `engineer@company.com` or `john.smith@fab.com`
- **Purpose:** Tracks who requested the analysis
- **Required:** Yes

### 4. **Example Form Submission**

Here's a complete example you can use right now:

```
Lot ID:       LOT-2024-DEC-001
Wafer ID:     W25
Bin Number:   7
Priority:     High Priority
User ID:      test.engineer@semiconductor.com
```

### 5. **Submit the Form**
- Review your inputs
- Click the **"Submit RCA Request"** button (purple gradient button)
- The button will show a spinner: "Submitting..."

### 6. **What Happens Next**

**Immediately after submission:**
- ✅ You're redirected to the **Status Page**
- ✅ You'll see a Session ID (unique identifier for your analysis)
- ✅ Overall progress bar shows 0% → 100%
- ✅ Agent status cards appear showing AI agents working

**During Analysis (45-90 seconds):**
- Watch the progress bar fill up
- See each agent's status:
  - **Data Retrieval Agent** → Fetches test data
  - **Pattern Recognition Agent** → Identifies failure patterns
  - **Hypothesis Generator** → Creates root cause theories
  - **Evidence Collector** → Gathers supporting evidence
  - **Hypothesis Ranker** → Ranks by confidence
  - **Report Generator** → Creates final report

**Status Updates Every 3 Seconds:**
- Page auto-refreshes
- Progress bars update
- Agent statuses change:
  - 🟡 **QUEUED** → Waiting to start
  - 🔵 **RUNNING** → Currently working
  - 🟢 **COMPLETED** → Finished successfully
  - 🔴 **FAILED** → Error occurred

### 7. **View Results**

**When analysis completes:**
- Status shows: **COMPLETED**
- Green "View Results" button appears
- Click it to see the analysis

**Results Page Shows:**
- **Ranked Hypotheses** (1, 2, 3, etc.)
  - Most likely root cause at #1
  - Confidence score (High/Medium/Low)
  - Percentage (e.g., 85%)
- **Supporting Evidence** for each hypothesis
  - Evidence type (Test Results, Historical Data, etc.)
  - Description
  - Individual confidence percentage
- **Recommended Actions**
  - Steps to fix the issue
  - Verification procedures

---

## 🎯 Real-World Use Case Example

**Scenario:** You're a semiconductor engineer who just discovered wafer defects.

### **The Problem:**
- Manufacturing Lot: `LOT-2024-Q4-078`
- Affected Wafer: `W42`
- Test Result: Failed electrical test, sorted to Bin 8
- Impact: High - affecting production yield

### **What You Do:**

1. **Go to:** http://localhost:3000/submit

2. **Fill the form:**
   ```
   Lot ID:       LOT-2024-Q4-078
   Wafer ID:     W42
   Bin:          8
   Priority:     High Priority (⚠️ affecting yield)
   User ID:      sarah.chen@fabplant.com
   ```

3. **Submit** → System analyzes for ~60 seconds

4. **Results might show:**
   - **Hypothesis #1 (92% confidence):** Photolithography misalignment
     - Evidence: Adjacent wafers show similar patterns
     - Evidence: Stepper tool maintenance log shows recent issues
     - Action: Inspect stepper tool alignment
   
   - **Hypothesis #2 (78% confidence):** Contamination in etching process
     - Evidence: Particulate count elevated in chamber logs
     - Action: Clean etching chamber, check filters

5. **You take action:**
   - Check the stepper tool (Hypothesis #1)
   - Find alignment issue
   - Fix and verify
   - Problem resolved! ✅

---

## 📊 Understanding the Dashboard

After submitting analyses, the Dashboard shows:

- **All RCA Sessions** in a list
- **Status badges:**
  - 🟢 Completed
  - 🔵 Running
  - 🟡 Queued
  - 🔴 Failed
- **Click any session** to view its status/results
- **Filters** to find specific analyses (coming soon)

---

## 🔧 Field Validation & Errors

### **Required Fields:**
All 5 fields must be filled. If you miss one:
- ❌ Browser will highlight the empty field
- ❌ Form won't submit

### **Common Errors:**

**Error:** "Failed to fetch"
- **Cause:** Backend not running
- **Fix:** 
  ```bash
  cd backend
  uvicorn main:app --reload --port 8000
  ```

**Error:** "Bin number must be numeric"
- **Cause:** Entered text instead of number
- **Fix:** Enter only numbers (e.g., 5, not "five")

**Error:** "Invalid session"
- **Cause:** Session not found in database
- **Fix:** Submit a new RCA request

---

## 🎨 Visual Guide

### **Form Layout:**
```
┌─────────────────────────────────────────────┐
│  Submit New RCA Request                     │
│  Initiate root cause analysis               │
├─────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Lot ID         │  │ Wafer ID        │ │
│  │ LOT-2024-001   │  │ W123            │ │
│  └─────────────────┘  └──────────────────┘ │
│                                              │
│  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Bin Number     │  │ Priority Level  │ │
│  │ 5              │  │ 🟠 High        ▼│ │
│  └─────────────────┘  └──────────────────┘ │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ User ID                              │  │
│  │ engineer@company.com                 │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  [Cancel]    [⚡ Submit RCA Request]       │
└─────────────────────────────────────────────┘
```

### **Status Page:**
```
┌─────────────────────────────────────────────┐
│  RCA Analysis Status                        │
│  Session: abc123...                         │
├─────────────────────────────────────────────┤
│  Status: RUNNING    Progress: ████████ 75% │
│                                              │
│  Agent Status:                              │
│  🟢 Data Retrieval Agent    [████████] 100% │
│  🔵 Pattern Recognition     [██████░░]  75% │
│  🟡 Hypothesis Generator    [░░░░░░░░]   0% │
└─────────────────────────────────────────────┘
```

### **Results Page:**
```
┌─────────────────────────────────────────────┐
│  RCA Analysis Results                       │
│  ✅ Completed                               │
├─────────────────────────────────────────────┤
│  [#1] Metal Layer Contamination             │
│       🟢 High (85%)                          │
│       ████████████████████░░ 85%            │
│                                              │
│       Supporting Evidence:                  │
│       ▌ HISTORICAL DATA            92%      │
│       ▌ Similar defects in adjacent wafers  │
│                                              │
│       ▌ TEST RESULTS               80%      │
│       ▌ Elevated metal particulates         │
│                                              │
│       Recommended Actions:                  │
│       ✓ Inspect deposition chamber          │
│       ✓ Review clean room protocols         │
└─────────────────────────────────────────────┘
```

---

## 💡 Pro Tips

1. **Priority Levels:**
   - Use **Critical** for production line stops
   - Use **High** for yield-impacting issues
   - Use **Normal** for routine investigations
   - Use **Low** for historical analysis

2. **Naming Conventions:**
   - Use consistent Lot ID format: `LOT-YYYY-QX-NNN`
   - Use clear Wafer IDs: `W001`, `W002`, etc.
   - This makes searching easier later

3. **Track Your Analyses:**
   - Save the Session ID for important analyses
   - Format: `abc123-def456-ghi789-...`
   - Use it to share results with team

4. **Multiple Wafers:**
   - Submit separate analyses for each wafer
   - Compare hypotheses across wafers
   - Identify systemic issues

---

## 🔄 Complete Workflow

```
1. Defect Detected
   ↓
2. Open Platform (http://localhost:3000)
   ↓
3. Click "New RCA" Button
   ↓
4. Fill Form (Lot, Wafer, Bin, Priority, User)
   ↓
5. Submit → Auto-redirect to Status Page
   ↓
6. Watch Progress (6 AI agents work in parallel)
   ↓
7. Analysis Completes (~60 seconds)
   ↓
8. Click "View Results"
   ↓
9. Review Hypotheses (ranked by confidence)
   ↓
10. Read Evidence & Recommendations
   ↓
11. Take Action to Fix Issue
   ↓
12. ✅ Problem Resolved!
```

---

## 🆘 Troubleshooting

### **Form Won't Submit**
- Check all fields are filled
- Ensure Bin is a number
- Check browser console for errors (F12)

### **Backend Not Responding**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
cd backend
uvicorn main:app --reload --port 8000
```

### **Frontend Not Loading**
```bash
# Restart frontend:
cd frontend
npm run dev
# Opens at http://localhost:3000
```

### **Analysis Stuck**
- Wait up to 2 minutes
- Refresh the page
- Check backend logs for errors

---

## 🎓 Next Steps

1. ✅ **Try a Test Submission**
   - Use the example data above
   - Watch the complete flow
   - See results generated

2. ✅ **Submit Real Data**
   - Use actual lot/wafer IDs
   - Set appropriate priority
   - Review real hypotheses

3. ✅ **Integrate with Systems**
   - Connect to test equipment
   - Link to manufacturing database
   - Automate submissions via API

4. ✅ **Train Your Team**
   - Share this guide
   - Demo the workflow
   - Establish best practices

---

## 📞 Support

For questions or issues:
- Check the USAGE_GUIDE.md for detailed setup
- Review backend logs in terminal
- Check browser console for frontend errors

---

**Ready to start? Go to http://localhost:3000 and submit your first RCA! 🚀**
