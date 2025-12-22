# Product Requirements Document (PRD)
# P03: Multi-Agent Test Failure RCA Platform

**Project ID**: P03_Multi_Agent_RCA_Platform  
**Category**: Semiconductor Post-Silicon Validation / Agentic AI / Multi-Agent Systems  
**Status**: Draft for Review  
**Version**: v1.0  
**Last Updated**: 2025-12-04  
**Product Family**: Automotive MCU (TC3x, TC4x families)  
**Test Platform**: Advantest V93000 SMT8, Teradyne testers  

---

## 1. Overview

### 1.1 Executive Summary

The Multi-Agent Test Failure RCA Platform is an advanced agentic AI system that orchestrates multiple specialized AI agents using LangGraph and CrewAI to autonomously perform comprehensive root cause analysis (RCA) of semiconductor test failures. Unlike single-LLM chatbots, this platform deploys 6 collaborative agents—Orchestrator, Data Analyst, Statistical Analyst, Spatial Pattern Detector, Correlation Hunter, and Report Generator—each with specialized capabilities, tools, and memory systems, working together to investigate complex failure modes across STDF test data, wafer maps, parametric trends, and historical knowledge bases.

The platform leverages cutting-edge multi-agent architectures: (1) **LangGraph State Machines** - conditional agent routing based on intermediate findings with cycle detection and recovery, (2) **CrewAI Hierarchical Teams** - manager agents coordinate worker agents with task delegation and result aggregation, (3) **Shared Memory** - agents communicate via blackboard architecture with vector database storage (Chroma/Qdrant), (4) **Tool Use** - agents dynamically invoke Python functions for STDF parsing, statistical tests, wafer map analysis, SQL queries, (5) **RAG Integration** - retrieval-augmented generation from 10+ years of RCA reports, datasheets, debug logs, and (6) **LLM Orchestration** - GPT-4/Claude APIs with streaming responses, function calling, and error handling.

**Key Value Proposition**: Reduce RCA time from 4-8 hours per failure (manual engineer analysis) to 20-30 minutes (autonomous agent collaboration), achieve >85% root cause accuracy on historical validation set, enable 24/7 automated RCA for all test failures (not just critical ones), and scale RCA expertise across all product lines without adding headcount.

### 1.2 Document Purpose

This PRD defines comprehensive requirements for designing, developing, testing, and deploying the Multi-Agent Test Failure RCA Platform. It covers:
- Functional and non-functional requirements for multi-agent orchestration, LLM integration, and tool use
- Agent architecture specifications: roles, capabilities, tools, memory systems, communication protocols
- Data ingestion pipelines for STDF files, wafer maps, historical RCA reports, knowledge base embeddings
- System architecture with LangGraph state machines, CrewAI hierarchical teams, vector database design
- UI/UX requirements for agent communication dashboards, RCA report visualization, human-in-the-loop feedback
- Security, performance, scalability, and testing strategies for LLM-based production systems
- Deployment phases (single-agent baseline → multi-agent orchestration → autonomous RCA → human feedback loop)
- Success metrics, KPIs, and business impact validation across multiple failure modes and product lines

The document serves as the single source of truth for cross-functional teams (AI/ML Engineering, Backend, Frontend, DevOps, Test Engineering, Yield Engineering, Failure Analysis, Product Engineering) throughout the development lifecycle.

### 1.3 Product Vision

**Vision Statement**: Establish the industry-leading multi-agent AI platform for semiconductor test failure root cause analysis, combining state-of-the-art agent orchestration frameworks (LangGraph, CrewAI) with domain-specific tools and knowledge bases, enabling autonomous 24/7 RCA at scale with human-expert-level accuracy and comprehensive reporting.

**Long-term Goals** (18-24 months):
- Deploy across 20+ product families (TC3x, TC4x, TC5x) and 100+ failure bins
- Achieve >85% autonomous RCA accuracy (validated against expert engineer analysis)
- Reduce average RCA time from 4-8 hours (manual) to 20-30 minutes (autonomous)
- Process 500+ test failures per day (vs. 10-20 manual RCAs today)
- Build comprehensive knowledge graph with 10+ years of RCA history (50,000+ reports embedded)
- Enable self-improving agents via human feedback reinforcement learning
- Integrate multi-modal data: STDF test data, wafer maps, shmoo plots, scan chain dumps, FA images

**Differentiation**:
- Multi-agent collaboration vs. single-LLM monolithic chatbots (parallel analysis, specialized expertise)
- LangGraph state machines for complex conditional reasoning (not just simple prompt chains)
- CrewAI hierarchical teams with manager/worker delegation and task decomposition
- Shared memory via vector database (agents learn from each other's findings)
- Dynamic tool creation (agents write Python functions for novel failure modes)
- Self-reflection and critique (agents validate their own hypotheses before reporting)
- Explainable agent reasoning (show agent thought process, tool invocations, data sources)
- Human-in-the-loop feedback (experts rate RCA quality → agents improve via RLHF)

---

## 2. Problem Statement

### 2.1 Current Challenges

**Challenge 1: Manual RCA is Bottlenecked by Expert Availability**
- Experienced yield/FA engineers spend 4-8 hours per complex RCA (data gathering, analysis, reporting)
- Only 10-20 RCAs performed per week due to headcount constraints (vs. 500+ failures occurring)
- Critical failures get priority; routine failures accumulate without investigation
- Tribal knowledge concentrated in 3-5 senior engineers (retirement risk, knowledge loss)
- After-hours failures wait until next business day for analysis (no 24/7 coverage)
- New engineers require 6-12 months training to perform competent RCAs

**Challenge 2: Fragmented Data Sources and Tools**
- STDF test data in binary files (requires specialized parsers)
- Wafer maps in PNG/TIFF formats (manual visual inspection)
- Parametric trends in Excel spreadsheets (manual statistical analysis)
- Historical RCA reports in PDF/Word (not searchable, no embeddings)
- Shmoo plots in proprietary formats (voltage-frequency sweeps)
- Each data source requires different tool, manual correlation needed
- No unified view combining: test data + spatial patterns + parametric trends + historical context

**Challenge 3: Inconsistent RCA Quality and Completeness**
- RCA depth varies by engineer skill level and time available
- Missing analyses: some engineers skip statistical tests, others skip spatial pattern checks
- Inconsistent root cause categorization (same failure classified differently by different engineers)
- Incomplete documentation: 40% of RCAs lack sufficient detail for future reference
- No systematic validation of RCA conclusions (hypotheses not tested against additional data)
- Lessons learned not propagated across product lines (TC41x RCA insights don't reach TC42x team)

**Challenge 4: Single-LLM Chatbots Lack Specialized Expertise**
- General-purpose LLMs (GPT-4, Claude) lack semiconductor domain knowledge
- Single LLM must handle all aspects: data parsing, statistics, spatial analysis, reporting
- No task specialization or parallel analysis capabilities
- Limited tool use (basic RAG retrieval, no complex data manipulations)
- Cannot perform multi-step reasoning with intermediate validation
- Hallucination risk when combining multiple data sources (no cross-validation)

**Challenge 5: Slow Iterative Analysis Process**
- Engineer hypothesis → data query → analysis → new hypothesis (serial loop, 30-60 min per iteration)
- No automatic exploration of alternative hypotheses in parallel
- Data gathering bottleneck (waiting for STDF extracts, wafer map generation)
- Manual correlation hunting (testing 100+ test pair correlations takes hours)
- No proactive anomaly detection (engineer must know what to look for)

### 2.2 Impact Analysis

**Business Impact**:
- **Engineering Time Waste**: 400+ engineer-hours/month on manual RCAs ($800K+/year fully loaded cost)
- **Delayed Time-to-Market**: NPI debug cycles extended 2-4 weeks due to RCA backlogs
- **Yield Loss Continuation**: Routine failures not investigated → same root causes repeat for weeks
- **Knowledge Attrition**: Senior engineer retirement/turnover loses 10+ years of domain expertise
- **Reactive vs. Proactive**: Only critical failures investigated → systemic issues remain hidden
- **Cost Impact**: $4M+/year in extended test time, yield loss, delayed product ramps due to slow RCA

**Technical Impact**:
- Data fragmentation across 8+ systems (STDF repositories, wafer map servers, Excel archives, PDF reports)
- No systematic knowledge capture (RCA insights lost after email reports sent)
- Inconsistent RCA methodology across different engineers/product lines
- Limited parallel processing (one engineer = one RCA at a time)
- No 24/7 availability for global manufacturing operations

**Operational Impact**:
- RCA backlog of 50+ unresolved failures at any given time
- 72-hour average turnaround time for routine RCAs (vs. 4-hour target)
- Ad-hoc reporting formats (inconsistent structure, missing key sections)
- Manual handoffs between test engineers (identify failure) → yield engineers (RCA) → FA engineers (physical analysis)

### 2.3 Opportunity

**Agentic AI Transformation**:
- Multi-agent systems enable parallel specialized analysis (6 agents working simultaneously vs. 1 engineer serially)
- LangGraph state machines model complex conditional reasoning (if spatial pattern detected → route to FA agent)
- CrewAI hierarchical teams decompose complex RCAs into manageable sub-tasks with automatic delegation
- Vector database shared memory allows agents to build on each other's findings (blackboard architecture)
- Tool use framework enables agents to invoke domain-specific functions (STDF parsers, statistical tests, wafer map analysis)

**Scalability Benefits**:
- Process 500+ failures/day autonomously (vs. 10-20 manual RCAs today)
- 24/7 availability (no after-hours delays, global manufacturing support)
- Consistent RCA quality (every analysis includes statistical tests, spatial checks, historical correlation)
- Automated knowledge capture (every RCA embedded into vector database, searchable by future agents)
- Self-improving system (human feedback on RCA quality → agent fine-tuning via RLHF)

**ROI Potential**:
- **Direct Savings**: $4M+/year from faster RCA, reduced engineering time, prevented yield loss
- **Indirect Benefits**: Faster NPI ramps (2-4 week acceleration), improved yield learning loops, reduced customer escapes
- **Strategic Value**: Scalable expertise across all product lines, immune to knowledge attrition, 24/7 global operations support

---

## 3. Goals and Objectives

### 3.1 Primary Goals

**Goal 1: Autonomous Multi-Agent RCA**
- Deploy 6 specialized agents with distinct roles, tools, and capabilities
- Orchestrate agent collaboration via LangGraph state machines (conditional routing, cycle handling)
- Enable CrewAI hierarchical teams (manager delegates tasks to worker agents)
- Achieve >85% autonomous RCA accuracy on historical validation set (1,000+ labeled failures)
- Reduce RCA time from 4-8 hours (manual) to 20-30 minutes (autonomous)

**Goal 2: Comprehensive Multi-Modal Analysis**
- Integrate STDF test data parsing (die-level bin results, parametric measurements)
- Analyze wafer map spatial patterns (edge effects, center hot spots, ring defects)
- Detect parametric trend anomalies (IDDQ drift, Vth shifts, Fmax degradation)
- Correlate historical RCA reports via RAG (vector database with 10+ years of reports)
- Generate multi-modal evidence chains (test data + spatial patterns + historical precedents)

**Goal 3: Explainable Agent Reasoning**
- Visualize agent communication graph (which agents communicated, what data exchanged)
- Log agent thought processes (reasoning steps, tool invocations, intermediate findings)
- Show data provenance (citations to STDF files, wafer maps, historical RCA reports)
- Explain confidence scores (why 85% confident vs. 60% confident in root cause hypothesis)
- Enable human critique and feedback (engineers rate RCA quality, suggest improvements)

**Goal 4: Scalable Knowledge Management**
- Embed 10+ years of RCA reports into vector database (50,000+ documents, 10M+ chunks)
- Auto-extract failure patterns, root cause categories, recommended actions
- Enable semantic search across knowledge base ("show all edge effect failures on TC41x")
- Update knowledge base continuously (new RCAs automatically embedded and indexed)
- Support cross-product learning (TC41x RCA insights inform TC42x agent reasoning)

### 3.2 Business Objectives

**Objective 1: Engineering Efficiency**
- Reduce RCA engineering time by 80% (from 400 hrs/month to 80 hrs/month)
- Process 500+ failures/day autonomously (vs. 10-20 manual RCAs today)
- Enable 24/7 RCA coverage for global manufacturing operations
- Free senior engineers for strategic work (design reviews, yield roadmaps vs. routine RCAs)

**Objective 2: Yield Improvement**
- Reduce time-to-root-cause from 72 hours (current backlog) to <1 hour (autonomous)
- Enable proactive failure investigation (all failures analyzed, not just critical ones)
- Detect systemic issues faster (pattern recognition across 500 failures vs. 10 manual samples)
- Reduce yield loss continuation by 30% (faster RCA → faster corrective action)

**Objective 3: Knowledge Preservation**
- Capture 100% of RCA insights in searchable vector database (vs. 40% today in unsearchable PDFs)
- Eliminate knowledge attrition risk (expertise embedded in agent tools and knowledge base)
- Enable instant knowledge transfer to new product lines (agents trained on historical RCAs)
- Support new engineer onboarding (agents explain reasoning, cite historical precedents)

**Objective 4: Cost Savings**
- **Direct**: $3M/year in reduced engineering time (320 hrs/month × $150/hr fully loaded × 12 months)
- **Indirect**: $1M/year from prevented yield loss (30% faster RCA → 30% faster corrective actions)
- **Strategic**: NPI cycle time reduction (2-4 week acceleration worth $5M+ in earlier revenue)
- **Total ROI**: $4M+/year cost savings, 6-month payback period

### 3.3 Success Metrics

**ML Model Metrics**:
- **RCA Accuracy**: >85% match with expert engineer root cause conclusions (validation set: 1,000 historical failures)
- **Agent Agreement**: >80% consensus among agents on root cause ranking (top-3 hypotheses)
- **Confidence Calibration**: Predicted confidence scores align with actual accuracy (80% confidence → 80% correct)
- **False Positive Rate**: <10% incorrect root cause hypotheses (reduce wild goose chases)

**System Performance Metrics**:
- **RCA Latency**: <30 minutes p95 from failure ingestion to final report generation
- **Agent Parallelism**: 6 agents running simultaneously with <20% idle time
- **LLM API Latency**: <5 seconds p95 per agent reasoning step (GPT-4/Claude API calls)
- **Tool Execution**: <10 seconds p95 for STDF parsing, statistical tests, wafer map analysis
- **Throughput**: 500+ RCAs processed per day with <99.9% uptime

**Business Metrics**:
- **Engineering Time Savings**: 320+ hours/month reduction in manual RCA time
- **RCA Backlog**: <10 unresolved failures at any time (vs. 50+ today)
- **Time-to-Root-Cause**: <1 hour p95 (vs. 72 hours today)
- **Knowledge Base Growth**: 500+ new RCA reports embedded per month
- **User Adoption**: 50+ engineers using platform weekly, >4.0/5.0 satisfaction rating

**ROI Metrics**:
- **Cost Savings**: $4M+/year from reduced engineering time and prevented yield loss
- **Payback Period**: <6 months
- **Yield Impact**: 30% reduction in yield loss continuation due to faster RCA

---

## 4. Target Users/Audience

### 4.1 Primary Users

**Test Engineers** (150+ users):
- Identify test failures on ATE (Advantest V93000, Teradyne)
- Submit failure lots/wafers for automated RCA
- Review agent-generated root cause hypotheses
- Validate RCA conclusions against actual wafer behavior
- Use RCA insights to adjust test limits, skip unnecessary tests

**Yield Engineers** (50+ users):
- Investigate systematic yield losses across product lines
- Analyze wafer-level spatial patterns (edge effects, center hot spots)
- Validate agent RCA conclusions with additional data
- Provide human feedback to improve agent accuracy
- Generate executive reports for management reviews

**Failure Analysis (FA) Engineers** (30+ users):
- Use RCA hypotheses to guide physical FA (SEM, TEM, decap analysis)
- Validate electrical failure modes with structural defect findings
- Close the loop: FA results confirm/refute agent root cause hypotheses
- Contribute FA images and findings to knowledge base

### 4.2 Secondary Users

**Product Engineers** (100+ users):
- Review RCA trends for design-related failure modes
- Use RCA insights for next-generation product improvements
- Validate agent hypotheses against circuit simulations, layout reviews
- Contribute design documentation to knowledge base (datasheets, app notes)

**Operations/Management** (20+ users):
- Monitor RCA metrics dashboards (backlog, accuracy, time-to-resolution)
- Review executive summaries of critical failures
- Track ROI and cost savings from automated RCA
- Allocate engineering resources based on RCA insights

### 4.3 User Personas

**Persona 1: Sarah - Senior Yield Engineer**
- **Background**: 12 years in semiconductor yield analysis, expert in statistical methods and spatial pattern recognition
- **Pain Points**:
  - Spends 6-8 hours per complex RCA manually correlating STDF data, wafer maps, historical reports
  - Backlog of 20+ routine failures she can't investigate due to time constraints
  - Concerned about knowledge loss when she retires in 5 years
  - Frustrated by inconsistent RCA quality from junior engineers
- **Goals**:
  - Automate routine RCAs to focus on novel/complex failure modes
  - Ensure her 12 years of expertise is captured in the agent knowledge base
  - Reduce RCA time from 6 hours to 30 minutes for 80% of failures
  - Maintain RCA quality standards across all investigations
- **Success Criteria**:
  - Agent RCA accuracy >85% matches her manual conclusions
  - Can review and approve agent RCAs in <30 minutes vs. performing full manual analysis
  - Knowledge base answers "why" questions she would normally field from junior engineers
  - Freed time reallocated to strategic yield roadmap planning

**Persona 2: Mike - Test Engineer (5 years experience)**
- **Background**: Mid-level test engineer responsible for production test on Advantest V93000, handles 500+ lots/month
- **Pain Points**:
  - Identifies 50+ test failures per week but can only submit 5 for formal RCA (due to yield engineering backlog)
  - Routine failures repeat weekly because no RCA performed (no headcount for investigation)
  - Waits 72 hours for RCA results, delaying corrective actions (test limit changes, lot disposition)
  - Lacks expertise to perform own RCAs (needs statistical analysis, historical context)
- **Goals**:
  - Get RCA results within 1 hour for all failures (not just critical ones)
  - Understand root causes without requiring deep yield engineering expertise
  - Implement corrective actions faster (test limits, skip tests, change test flow)
  - Learn from agent explanations to improve his own troubleshooting skills
- **Success Criteria**:
  - All 50 failures/week receive automated RCA (vs. 5 manual RCAs today)
  - RCA turnaround time <1 hour (vs. 72 hours today)
  - Agent explanations clear enough for him to implement corrective actions
  - Learns patterns over time ("edge effect → package stress → reduce test temperature")

**Persona 3: Jennifer - Failure Analysis Engineer**
- **Background**: PhD in materials science, expert in physical failure analysis (SEM, TEM, decap), 8 years semiconductor FA experience
- **Pain Points**:
  - Receives vague FA requests ("check lot X123 for defects") without clear electrical root cause hypothesis
  - Spends hours reviewing STDF data herself to understand electrical failure mode before starting FA
  - Physical FA findings (crack, void, particle) don't always align with electrical symptoms (test bin, parameters)
  - FA results documented in PDFs/PowerPoint, not searchable or reusable by future investigations
- **Goals**:
  - Receive agent RCA hypotheses to guide FA (e.g., "suspected package crack due to edge effect pattern")
  - Validate electrical root cause before expensive FA ($5K-$20K per sample)
  - Close the loop: FA findings confirm agent RCA, update knowledge base
  - Searchable FA image database (past cracks, voids, particles for comparison)
- **Success Criteria**:
  - Agent RCA provides clear FA hypothesis 90% of the time
  - FA confirmation rate >70% (agent hypothesis matches physical findings)
  - FA results embedded into knowledge base with image search (find similar defects)
  - FA time reduced 30% (clearer hypotheses → fewer exploratory samples)

**Persona 4: David - New Test Engineer (1 year experience)**
- **Background**: Recent college graduate (BSEE), learning semiconductor test engineering, limited RCA experience
- **Pain Points**:
  - Overwhelmed by complexity of RCA (STDF formats, statistical tests, historical knowledge)
  - Relies on senior engineers for guidance (takes weeks to get their time)
  - Makes mistakes in root cause hypotheses due to lack of domain knowledge
  - No systematic training materials (learns via osmosis, trial-and-error)
- **Goals**:
  - Learn RCA methodology from agent explanations and reasoning steps
  - Get immediate answers to "why did this fail?" questions (vs. waiting for senior engineer)
  - Build confidence in root cause analysis skills over time
  - Access historical RCA precedents to inform current investigations
- **Success Criteria**:
  - Agent explanations teach him RCA methodology (statistical tests, spatial patterns, historical correlation)
  - Reduces reliance on senior engineers by 70% (self-service via agent)
  - RCA skill level improves over 6 months (measured by RCA quality peer reviews)
  - Can independently perform basic RCAs after 3 months (vs. 12 months traditional training)

---

## 5. User Stories

**US-01: Autonomous RCA Initiation**
- **As a** test engineer
- **I want to** submit a failed lot/wafer/bin to the platform and receive automated RCA
- **So that** I don't have to wait 72 hours for yield engineering availability
- **Acceptance Criteria**:
  - Upload STDF file or specify lot ID, wafer ID, bin number via web UI
  - System automatically ingests STDF data, generates wafer maps, initiates multi-agent RCA
  - RCA status dashboard shows agent progress in real-time (Data Agent parsing → Statistical Agent analyzing → etc.)
  - Final RCA report delivered in <30 minutes with root cause hypotheses ranked by confidence
  - Email/Slack notification when RCA complete

**US-02: Multi-Agent Collaboration Visualization**
- **As a** yield engineer
- **I want to** visualize which agents communicated and what findings they shared
- **So that** I can understand the agent reasoning process and validate conclusions
- **Acceptance Criteria**:
  - Agent communication graph shows nodes (agents) and edges (data exchanges)
  - Each agent node displays: role, tools invoked, key findings, confidence score
  - Timeline view shows agent activity sequence (Data Agent finished at T+2min → Statistical Agent started)
  - Click on agent to see detailed reasoning logs (LLM prompts, tool outputs, intermediate conclusions)
  - Export agent reasoning trace for auditing or training purposes

**US-03: RAG-Powered Historical Context**
- **As a** yield engineer
- **I want to** see similar historical failures and their root causes
- **So that** I can validate agent hypotheses against proven precedents
- **Acceptance Criteria**:
  - Agent retrieves top-10 similar failures from vector database (based on: product, bin, spatial pattern, parametric trends)
  - Each historical RCA shows: date, lot, root cause, corrective action, resolution outcome
  - Similarity scores explain why matches are relevant (e.g., "85% similar: same edge effect pattern on TC41x BGA436")
  - Click on historical RCA to view full report (PDF) or embedded summary
  - Agent cites historical RCAs in final report ("This failure resembles RCA-2023-0456 which was traced to package stress")

**US-04: Interactive Agent Feedback**
- **As a** failure analysis engineer
- **I want to** provide feedback on agent RCA quality (correct/incorrect/incomplete)
- **So that** agents improve over time and learn from expert domain knowledge
- **Acceptance Criteria**:
  - RCA report includes feedback form: "Was this root cause correct? (Yes/No/Partial)"
  - Free-text field for expert comments ("Agent missed correlation with Test_XYZ")
  - Rating scale 1-5 for RCA completeness, accuracy, actionability
  - Feedback stored in database, used for agent fine-tuning via RLHF
  - Agent performance dashboard shows accuracy trends over time (before/after feedback incorporation)

**US-05: Spatial Pattern Detection**
- **As a** yield engineer
- **I want to** automatically detect spatial patterns on wafer maps (edge, center, ring, quadrant)
- **So that** I don't have to manually inspect 50+ wafer maps per week
- **Acceptance Criteria**:
  - Spatial Agent analyzes wafer map PNG and classifies pattern type (edge effect, center cluster, ring, quadrant, random, scratch, mixed)
  - Pattern detection confidence score (e.g., "95% confident: edge effect")
  - Wafer map overlay highlights detected pattern region (colored mask on original image)
  - Pattern type correlates with root cause hypothesis (edge effect → package stress, center cluster → lithography)
  - Export pattern classification for all wafers in lot (CSV: wafer_id, pattern, confidence)

**US-06: Statistical Correlation Hunting**
- **As a** yield engineer
- **I want to** automatically discover hidden correlations between test failures
- **So that** I can identify root causes not obvious from single-test analysis
- **Acceptance Criteria**:
  - Statistical Agent computes Pearson correlation matrix for all test pairs (1,000+ tests → 500K+ pairs)
  - Flags high correlations (|r| > 0.7) with statistical significance (p < 0.01)
  - Visualizes correlation network graph (nodes = tests, edges = correlations)
  - Identifies test clusters (groups of tests failing together → common root cause)
  - Agent hypothesis incorporates correlations ("IDDQ and Vth both elevated → junction leakage")

**US-07: Automated Report Generation**
- **As a** test engineer
- **I want to** receive a comprehensive RCA report in standard format (PDF)
- **So that** I can share findings with management and implement corrective actions
- **Acceptance Criteria**:
  - Report Generator Agent produces 10-page PDF with sections: Executive Summary, Data Overview, Spatial Analysis, Statistical Findings, Parametric Trends, Historical Context, Root Cause Hypotheses (ranked), Recommended Actions, Appendices (plots, tables)
  - Report includes: wafer maps, Pareto charts, correlation matrices, parametric trend plots, citations to historical RCAs
  - Executive summary (1 page) suitable for management review (non-technical stakeholders)
  - Technical details (9 pages) for engineers to implement corrective actions
  - Report downloadable from web UI, emailed automatically, archived in document management system

**US-08: 24/7 Continuous RCA Processing**
- **As an** operations manager
- **I want to** run RCA platform 24/7 across all global manufacturing sites
- **So that** failures occurring after-hours are analyzed immediately (no wait until next business day)
- **Acceptance Criteria**:
  - Platform runs continuously with <99.9% uptime (max 8 hours downtime/year)
  - Automatic failover if LLM API down (fallback to alternative provider: GPT-4 → Claude)
  - Queue management: process up to 500 RCAs/day with priority ranking (critical failures first)
  - Email/Slack alerts for critical failures (Bin 99 Scrap) within 15 minutes of detection
  - Metrics dashboard shows: RCAs processed (hourly), backlog depth, average latency, agent utilization

---

## 6. Functional Requirements

### 6.1 Core Features

**FR-001: Multi-Agent Orchestration (LangGraph)**
- Deploy LangGraph state machine for orchestrating 6 agents with conditional routing
- Define agent states: START → DataIngestion → ParallelAnalysis [Statistical, Spatial, Correlation] → Synthesis → ReportGeneration → END
- Implement conditional edges: if spatial pattern detected → route to FA hypothesis generation
- Support cycles with max iteration limits (prevent infinite loops, max 3 cycles)
- Handle agent failures gracefully (if Statistical Agent crashes → log error, continue with partial results)
- Persist state machine execution trace for debugging and auditing

**FR-002: Hierarchical Agent Teams (CrewAI)**
- Deploy CrewAI manager-worker hierarchy: Orchestrator manages 5 specialist workers
- Manager agent capabilities: task decomposition, delegation, result aggregation, consensus building
- Worker agent capabilities: specialized tools, domain expertise, parallel execution
- Task queue management: manager assigns tasks to workers based on current state and findings
- Result synthesis: manager aggregates worker findings, resolves conflicts, ranks hypotheses

**FR-003: Shared Memory and Blackboard Architecture**
- Implement blackboard memory system where all agents read/write intermediate findings
- PostgreSQL database stores: agent messages, tool outputs, intermediate hypotheses, confidence scores
- Vector database (Chroma/Qdrant) stores: STDF data embeddings, wafer map feature vectors, RCA report embeddings
- Memory retrieval: agents query blackboard for relevant findings from other agents
- Memory persistence: all agent interactions logged for replay, auditing, fine-tuning

**FR-004: Dynamic Tool Use Framework**
- Define tool library: STDF parser, wafer map generator, statistical tests (t-test, ANOVA, correlation), SQL queries, parametric trend analysis
- Tool execution engine: agents invoke tools via function calling API (OpenAI/Anthropic function calling)
- Tool input validation: ensure agent-provided parameters match tool schema (prevent errors)
- Tool output parsing: convert tool results to natural language summaries for agent consumption
- Custom tool creation: agents write Python functions for novel analyses, validated and added to library

**FR-005: Specialized Agent: Data Analyst**
- **Role**: Ingest and parse STDF files, extract test results, generate wafer maps
- **Tools**: STDF parser (pystdf), Parquet writer, wafer map generator (300x300 PNG), SQL query builder
- **Inputs**: STDF file path or lot/wafer ID
- **Outputs**: Parsed test data (Parquet), wafer map PNG, data summary statistics (die count, bin distribution, yield)
- **Error Handling**: Invalid STDF format → log error, request alternative data source

**FR-006: Specialized Agent: Statistical Analyst**
- **Role**: Perform statistical tests, correlation analysis, anomaly detection
- **Tools**: scipy.stats (t-test, ANOVA, chi-square), Pearson/Spearman correlation, outlier detection (Z-score, IQR)
- **Inputs**: Test data from Data Analyst (Parquet), historical baseline statistics
- **Outputs**: Statistical test results (p-values, effect sizes), correlation matrix, anomaly flags
- **Hypotheses Tested**: Is bin rate significantly different from baseline? Are any test pairs highly correlated? Are there parametric outliers?

**FR-007: Specialized Agent: Spatial Pattern Detector**
- **Role**: Analyze wafer map spatial patterns, classify defect types
- **Tools**: OpenCV (image processing), scikit-image (region detection), ResNet-based classifier (trained on 10,000 wafer maps)
- **Inputs**: Wafer map PNG from Data Analyst
- **Outputs**: Pattern classification (edge, center, ring, quadrant, random, scratch, mixed), confidence score, annotated wafer map (overlay)
- **Defect Types**: Edge effect (peripheral die failures), center cluster (lithography hot spot), ring pattern (process non-uniformity), quadrant (reticle issue), scratch (handling damage)

**FR-008: Specialized Agent: Correlation Hunter**
- **Role**: Discover hidden test correlations, identify test clusters indicating common root cause
- **Tools**: Correlation matrix computation (1,000 tests → 500K pairs), network graph analysis (networkx), community detection
- **Inputs**: Test data from Data Analyst (all parametric measurements)
- **Outputs**: High-correlation test pairs (|r| > 0.7, p < 0.01), test clusters (groups failing together), correlation network graph
- **Hypotheses Generated**: "Tests A, B, C fail together → common circuit block → localized defect"

**FR-009: Specialized Agent: Report Generator**
- **Role**: Synthesize findings from all agents, rank root cause hypotheses, generate comprehensive PDF report
- **Tools**: ReportLab (PDF generation), Plotly (charts/graphs), Jinja2 (report templates)
- **Inputs**: Findings from Data, Statistical, Spatial, Correlation agents; RAG-retrieved historical RCAs
- **Outputs**: 10-page PDF report with: Executive Summary, Data Overview, Spatial Analysis, Statistical Findings, Correlations, Historical Context, Root Cause Hypotheses (ranked top-5 by confidence), Recommended Actions, Appendices
- **Report Sections**: Configurable template, customizable for different failure modes

**FR-010: RAG Integration with Vector Database**
- Embed 10+ years of RCA reports (50,000 documents, 10M chunks) into Chroma/Qdrant vector database
- Embedding model: OpenAI text-embedding-3-large (3072-dim vectors) or open-source alternatives (sentence-transformers)
- Retrieval: semantic search for similar failures based on: product, bin, spatial pattern, parametric trends, keywords
- Re-ranking: re-rank retrieval results using cross-encoder for relevance (top-10 retrieved → top-3 re-ranked)
- Citation: agents cite retrieved RCAs in final report with document IDs and relevance scores

**FR-011: LLM Integration (GPT-4/Claude)**
- Primary LLM: GPT-4-turbo (128K context) or Claude 3.5 Sonnet (200K context)
- Function calling: agents invoke tools via OpenAI/Anthropic function calling API
- Streaming responses: real-time agent reasoning updates in UI (not just final response)
- Error handling: LLM API timeouts → retry with exponential backoff, fallback to alternative provider
- Token management: track token usage per RCA (target: <50K tokens per RCA = $0.50 cost)

**FR-012: Human-in-the-Loop Feedback**
- RCA report includes feedback form: rating (1-5), correctness (Yes/No/Partial), free-text comments
- Feedback stored in PostgreSQL with RCA ID, user ID, timestamp, ratings, comments
- Feedback analytics dashboard: accuracy trends over time, common failure modes, agent performance by product line
- RLHF (Reinforcement Learning from Human Feedback): use feedback to fine-tune agent LLM prompts, tool selection, hypothesis ranking
- Feedback loop closure: when engineer confirms root cause → update knowledge base with validated finding

### 6.2 Advanced Features

**FR-013: Self-Reflection and Critique**
- Agents self-evaluate their hypotheses before reporting: "Am I confident in this conclusion? What evidence is missing?"
- Critique prompts: "What are alternative explanations? What data would refute my hypothesis? What is my confidence score (0-100)?"
- Agent revision: if self-critique identifies gaps → request additional analysis from other agents (e.g., "Need FA images to confirm crack hypothesis")
- Reflection logs: persist agent self-critique reasoning for transparency and debugging

**FR-014: Dynamic Tool Creation**
- Agents write Python functions for novel failure modes not covered by existing tool library
- Example: Statistical Agent creates custom correlation metric for shmoo plot analysis
- Tool validation: sandbox execution (Docker container), code review (automated static analysis), test on sample data
- Tool approval: human engineer reviews generated code → approve/reject → add to tool library if approved
- Tool reuse: approved custom tools available to all agents in future RCAs

**FR-015: Planning Algorithms (MCTS, A*)**
- Orchestrator Agent uses Monte Carlo Tree Search (MCTS) to explore different RCA strategies
- MCTS nodes: analysis steps (parse STDF, run stats, check spatial, retrieve RAG), MCTS edges: transitions between steps
- Reward function: estimated RCA quality (confidence × completeness), penalty for redundant analyses
- A* search: find optimal path through analysis steps to reach root cause conclusion with minimum time/cost
- Fallback: if MCTS takes >2 minutes → use default heuristic-based plan

**FR-016: Multi-Modal Data Integration**
- Integrate STDF test data + wafer maps + parametric trends + shmoo plots + scan chain dumps + FA images
- Multi-modal embeddings: combine text (RCA reports), images (wafer maps, FA photos), tabular data (test results) into unified vector space
- Cross-modal retrieval: "Find wafer maps similar to this FA image" or "Find test data matching this parametric trend"
- Unified view: dashboard shows all data types side-by-side with cross-highlighting (click wafer map region → show tests failing in that region)

**FR-017: Incremental Learning and Knowledge Base Updates**
- Every completed RCA automatically embedded into vector database (no manual knowledge base curation)
- New RCA indexed within 5 minutes (real-time embedding pipeline)
- Knowledge base versioning: track which RCAs were available when past agent reasoning occurred (for reproducibility)
- Knowledge pruning: archive outdated RCAs (product EOL, superseded root causes) to reduce noise

**FR-018: Agent Performance Monitoring and A/B Testing**
- Track agent performance metrics: accuracy, latency, tool invocation frequency, hypothesis diversity
- A/B testing: deploy two agent versions (different LLM prompts, tool sets) → compare RCA quality on same failure set
- Champion/challenger: production agent (champion) vs. experimental agent (challenger), promote challenger if accuracy improves >5%
- Canary deployments: new agent version processes 10% of RCAs → gradual rollout if metrics acceptable

---

## 7. Non-Functional Requirements

### 7.1 Performance

**NFR-P1: RCA Latency**
- **Target**: <30 minutes p95 end-to-end RCA latency (from STDF ingestion to final report)
- **Breakdown**: Data parsing (2 min), agent reasoning (15 min), RAG retrieval (3 min), report generation (5 min), overhead (5 min)
- **LLM API Latency**: <5 seconds p95 per agent reasoning step (GPT-4/Claude API call)
- **Tool Execution**: <10 seconds p95 for STDF parsing, statistical tests, wafer map generation
- **Parallel Agents**: Run Statistical, Spatial, Correlation agents in parallel (not serially) to reduce latency by 40%

**NFR-P2: Throughput**
- **Target**: Process 500+ RCAs per day (20-25 RCAs per hour)
- **Concurrency**: Support 10+ simultaneous RCA sessions (different failures analyzed in parallel)
- **Queue Management**: FIFO queue with priority override for critical failures (Bin 99 Scrap)
- **Scalability**: Horizontal scaling (add more agent worker pods) to increase throughput linearly

**NFR-P3: Resource Efficiency**
- **LLM Token Usage**: <50K tokens per RCA average (target: $0.50 LLM cost per RCA at GPT-4-turbo pricing)
- **CPU**: <2 vCPU per RCA session average (agent orchestration, tool execution)
- **Memory**: <8GB RAM per RCA session average (STDF data, wafer maps, agent state)
- **GPU**: No GPU required for inference (LLM APIs external, wafer map analysis uses CPU ResNet-ONNX)

### 7.2 Reliability

**NFR-R1: System Uptime**
- **Target**: >99.9% uptime (max 8 hours downtime per year)
- **Failover**: If primary LLM API down (OpenAI GPT-4) → automatic fallback to secondary (Anthropic Claude)
- **Retry Logic**: Exponential backoff for transient LLM API errors (timeout, rate limit), max 3 retries
- **Graceful Degradation**: If one agent crashes → continue RCA with partial results, flag incomplete analysis

**NFR-R2: Data Durability**
- All RCA results persisted to PostgreSQL with replication (2 replicas, sync writes)
- Vector database (Chroma/Qdrant) backed up daily, point-in-time recovery (7-day retention)
- STDF files archived to object storage (MinIO/S3) with 3-year retention
- Disaster recovery: restore full system state from backups within 4 hours

**NFR-R3: Error Handling**
- Comprehensive error logging for all agent actions, tool invocations, LLM API calls
- Agent failures categorized: transient (retry), permanent (log and continue), critical (abort RCA)
- User notifications: if RCA fails → email/Slack alert with error details, retry option
- Error analytics dashboard: track error rates by agent, tool, failure mode

### 7.3 Usability

**NFR-U1: User Interface**
- Web-based UI (React/Next.js) accessible from any browser (Chrome, Firefox, Safari, Edge)
- Mobile-responsive design (view RCA reports on tablets, phones)
- Real-time RCA status updates (websockets show agent progress: "Statistical Agent analyzing...")
- One-click RCA initiation (upload STDF or enter lot ID → submit)
- Download RCA report as PDF (one-click download button)

**NFR-U2: Accessibility**
- WCAG 2.1 AA compliance (screen reader support, keyboard navigation, color contrast)
- Multi-language support (English primary, German/Chinese for global sites - future)
- Tooltips and help text for all technical terms (hover over "edge effect" → see definition)
- User onboarding: interactive tutorial (first-time users guided through RCA submission)

**NFR-U3: Explainability**
- All agent reasoning steps visible in UI (expand/collapse agent activity logs)
- Citations to data sources (click "edge effect detected" → see wafer map evidence)
- Confidence scores with explanations ("85% confident because 3 historical precedents + statistical significance")
- Glossary of technical terms (semiconductor jargon explained for non-experts)

### 7.4 Maintainability

**NFR-M1: Code Quality**
- Python backend: type hints (mypy), linting (ruff), formatting (black), test coverage >85%
- Agent LLM prompts version-controlled (Git), prompt engineering best practices (clear instructions, examples, constraints)
- Modular architecture: agents, tools, memory, orchestration in separate modules (low coupling)
- Documentation: agent role definitions, tool specifications, architecture diagrams (Mermaid/PlantUML)

**NFR-M2: Observability**
- Structured logging (JSON) with correlation IDs (trace RCA session across all agent logs)
- Metrics instrumentation: Prometheus metrics for agent latency, LLM token usage, tool execution time
- Distributed tracing: OpenTelemetry traces for LangGraph state machine execution
- Grafana dashboards: RCA throughput, latency, accuracy, cost, error rates

**NFR-M3: Agent Versioning**
- Agent LLM prompts, tool sets, models versioned (semantic versioning: v1.0.0, v1.1.0, v2.0.0)
- Prompt registry: all prompt versions stored in database, rollback to previous version if new version degrades quality
- A/B testing framework: compare agent versions on same failure set
- Deployment: blue-green deployment for agents (zero-downtime version upgrades)

---

## 8. Technical Requirements

### 8.1 Technical Stack

**Backend**:
- Python 3.11+, FastAPI 0.115+, Pydantic 2.8+ (data validation)
- LangGraph 0.2+ (multi-agent state machines with conditional routing and cycles)
- CrewAI 0.51+ (hierarchical agent teams with manager/worker delegation)
- LangChain 0.2+ (LLM framework, tool use, memory, RAG components)
- OpenAI Python SDK 1.35+ (GPT-4-turbo API, function calling, embeddings)
- Anthropic Python SDK 0.32+ (Claude 3.5 Sonnet API, fallback LLM)

**Multi-Agent Frameworks**:
- LangGraph: State machines, conditional edges, cycles, checkpointing, human-in-the-loop
- CrewAI: Hierarchical teams, task delegation, result aggregation, agent roles
- LangChain Tools: Tool decorator, StructuredTool, OpenAI function calling integration
- LangChain Memory: ConversationBufferMemory, VectorStoreRetrieverMemory, PostgresChatMessageHistory

**LLM Integration**:
- Primary LLM: GPT-4-turbo (gpt-4-turbo-2024-04-09, 128K context, function calling, JSON mode)
- Fallback LLM: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022, 200K context, tool use)
- Streaming: OpenAI/Anthropic streaming APIs for real-time agent responses
- Embeddings: OpenAI text-embedding-3-large (3072-dim, $0.13/1M tokens) or sentence-transformers (free, local)

**Vector Database & RAG**:
- Chroma 0.5+ or Qdrant 1.11+ (vector database for RCA report embeddings, STDF data embeddings)
- LangChain VectorStoreRetriever: semantic search, similarity thresholds, metadata filtering
- Re-ranking: Cross-encoder models (ms-marco-MiniLM) for retrieval result re-ranking
- Chunking: RecursiveCharacterTextSplitter (chunk size 1000, overlap 200) for RCA report processing

**Tool Library**:
- STDF Parsing: pystdf 1.4+, custom parsers for TDF/ATDF formats
- Statistical Analysis: scipy 1.13+, statsmodels 0.14+, scikit-learn 1.5+
- Wafer Map Analysis: OpenCV 4.10+, scikit-image 0.24+, ResNet-ONNX (trained classifier)
- Data Processing: Pandas 2.2+, NumPy 1.26+, Polars 1.2+ (for large STDF files)
- Visualization: Plotly 5.20+, Matplotlib 3.8+, Seaborn 0.13+

**Database & Storage**:
- PostgreSQL 16+ (agent state, RCA results, user feedback, chat history)
- Vector Database: Chroma (embedded) or Qdrant (distributed) for 50K+ RCA embeddings
- Object Storage: MinIO (S3-compatible) for STDF files, wafer maps, PDFs (3-year retention)
- Redis 7.2+ (task queue for agent job scheduling, caching for LLM responses)

**Report Generation**:
- ReportLab 4.2+ (PDF generation with custom templates)
- Jinja2 3.1+ (report templating engine)
- Plotly 5.20+ (interactive charts for PDF embedding: Pareto, wafer maps, correlation matrices)
- WeasyPrint 62+ (HTML to PDF conversion, alternative to ReportLab)

**Deployment & Infrastructure**:
- Docker 27+, Kubernetes 1.30+ (container orchestration)
- Helm 3.15+ (Kubernetes package management)
- GitHub Actions (CI/CD pipeline: lint → test → build → deploy)
- Prometheus 2.53+ (metrics), Grafana 11.1+ (dashboards), OpenTelemetry 1.25+ (tracing)

**Frontend**:
- React 18+ with TypeScript 5.5+, Next.js 14+ (SSR, API routes)
- TanStack Query 5.50+ (data fetching, caching)
- Plotly.js 2.34+ (interactive wafer maps, Pareto charts)
- TailwindCSS 3.4+ (styling), shadcn/ui (component library)
- WebSockets (Socket.IO) for real-time agent status updates

### 8.2 AI/ML Components

**LangGraph Multi-Agent State Machine**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
import operator

class AgentState(TypedDict):
    """Shared state across all agents"""
    lot_id: str
    wafer_id: str
    bin: int
    stdf_data: dict
    wafer_map_path: str
    statistical_findings: list
    spatial_patterns: list
    correlations: list
    rag_results: list
    root_causes: list  # Ranked hypotheses
    confidence_scores: dict
    messages: Annotated[Sequence[dict], operator.add]  # Agent communication log

# Define agents as nodes
def data_analyst_agent(state: AgentState) -> AgentState:
    """Parse STDF, generate wafer maps"""
    from tools import parse_stdf, generate_wafer_map
    state["stdf_data"] = parse_stdf(state["lot_id"], state["wafer_id"])
    state["wafer_map_path"] = generate_wafer_map(state["stdf_data"])
    state["messages"].append({"agent": "DataAnalyst", "finding": "STDF parsed, wafer map generated"})
    return state

def statistical_analyst_agent(state: AgentState) -> AgentState:
    """Run statistical tests"""
    from tools import run_ttest, compute_correlations
    bin_rate_pvalue = run_ttest(state["stdf_data"], baseline_rate=0.05)
    state["statistical_findings"].append({"test": "t-test", "p_value": bin_rate_pvalue})
    state["messages"].append({"agent": "StatisticalAnalyst", "finding": f"Bin rate significantly different (p={bin_rate_pvalue:.4f})"})
    return state

def spatial_analyst_agent(state: AgentState) -> AgentState:
    """Detect wafer map patterns"""
    from tools import classify_wafer_map
    pattern, confidence = classify_wafer_map(state["wafer_map_path"])
    state["spatial_patterns"].append({"pattern": pattern, "confidence": confidence})
    state["messages"].append({"agent": "SpatialAnalyst", "finding": f"Detected {pattern} pattern (confidence={confidence:.2f})"})
    return state

def correlation_hunter_agent(state: AgentState) -> AgentState:
    """Find test correlations"""
    from tools import find_correlations
    high_corr_pairs = find_correlations(state["stdf_data"], threshold=0.7)
    state["correlations"].extend(high_corr_pairs)
    state["messages"].append({"agent": "CorrelationHunter", "finding": f"Found {len(high_corr_pairs)} high-correlation test pairs"})
    return state

def conclusion_engine_agent(state: AgentState) -> AgentState:
    """LLM synthesizes all findings, ranks root causes"""
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    prompt = f"""
    Analyze the following test failure data and agent findings:
    - Lot: {state["lot_id"]}, Wafer: {state["wafer_id"]}, Bin: {state["bin"]}
    - Statistical Findings: {state["statistical_findings"]}
    - Spatial Patterns: {state["spatial_patterns"]}
    - Correlations: {state["correlations"]}
    - Historical RCAs: {state["rag_results"]}
    
    Provide top-3 root cause hypotheses ranked by confidence (0-100).
    Format: [{"root_cause": "...", "confidence": 85, "evidence": "..."}]
    """
    response = llm.invoke(prompt)
    state["root_causes"] = parse_llm_response(response.content)
    state["messages"].append({"agent": "ConclusionEngine", "finding": "Root causes ranked"})
    return state

# Build LangGraph state machine
workflow = StateGraph(AgentState)

# Add agent nodes
workflow.add_node("data_analyst", data_analyst_agent)
workflow.add_node("statistical_analyst", statistical_analyst_agent)
workflow.add_node("spatial_analyst", spatial_analyst_agent)
workflow.add_node("correlation_hunter", correlation_hunter_agent)
workflow.add_node("conclusion_engine", conclusion_engine_agent)

# Define edges (agent flow)
workflow.set_entry_point("data_analyst")
workflow.add_edge("data_analyst", "statistical_analyst")
workflow.add_edge("data_analyst", "spatial_analyst")  # Parallel
workflow.add_edge("data_analyst", "correlation_hunter")  # Parallel
workflow.add_edge("statistical_analyst", "conclusion_engine")
workflow.add_edge("spatial_analyst", "conclusion_engine")
workflow.add_edge("correlation_hunter", "conclusion_engine")
workflow.add_edge("conclusion_engine", END)

# Compile and run
app = workflow.compile()
result = app.invoke({
    "lot_id": "TC41x_LOT123",
    "wafer_id": "W05",
    "bin": 5,
    "stdf_data": {},
    "wafer_map_path": "",
    "statistical_findings": [],
    "spatial_patterns": [],
    "correlations": [],
    "rag_results": [],
    "root_causes": [],
    "confidence_scores": {},
    "messages": []
})

print(f"Root Causes: {result['root_causes']}")
print(f"Agent Messages: {result['messages']}")
```

**CrewAI Hierarchical Agent Teams**:
```python
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Define LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

# Manager Agent (Orchestrator)
orchestrator = Agent(
    role="RCA Orchestrator",
    goal="Coordinate specialist agents to determine root cause of test failure",
    backstory="Experienced yield engineer with 15 years managing RCA investigations",
    llm=llm,
    verbose=True,
    allow_delegation=True  # Can delegate tasks to workers
)

# Worker Agents
data_analyst = Agent(
    role="Data Analyst",
    goal="Parse STDF files and generate wafer maps",
    backstory="Expert in semiconductor test data formats and visualization",
    llm=llm,
    tools=[parse_stdf_tool, generate_wafer_map_tool]
)

statistical_analyst = Agent(
    role="Statistical Analyst",
    goal="Perform statistical tests and anomaly detection",
    backstory="PhD statistician specialized in semiconductor yield analysis",
    llm=llm,
    tools=[ttest_tool, anova_tool, correlation_tool]
)

spatial_analyst = Agent(
    role="Spatial Pattern Detector",
    goal="Classify wafer map spatial patterns",
    backstory="Computer vision expert trained on 10,000+ wafer maps",
    llm=llm,
    tools=[classify_wafer_map_tool, detect_clusters_tool]
)

# Define Tasks
task1 = Task(
    description="Parse STDF for lot TC41x_LOT123, wafer W05, bin 5",
    agent=data_analyst,
    expected_output="STDF data summary and wafer map PNG"
)

task2 = Task(
    description="Run statistical tests on bin 5 rate vs. baseline",
    agent=statistical_analyst,
    expected_output="T-test p-value and effect size"
)

task3 = Task(
    description="Classify spatial pattern on wafer map",
    agent=spatial_analyst,
    expected_output="Pattern type (edge/center/ring) and confidence score"
)

task4 = Task(
    description="Synthesize findings and rank root cause hypotheses",
    agent=orchestrator,
    expected_output="Top-3 root causes with confidence scores",
    context=[task1, task2, task3]  # Depends on worker outputs
)

# Create Crew (hierarchical process: manager delegates to workers)
crew = Crew(
    agents=[orchestrator, data_analyst, statistical_analyst, spatial_analyst],
    tasks=[task1, task2, task3, task4],
    process=Process.hierarchical,  # Manager delegates tasks
    manager_llm=llm,
    verbose=True
)

# Execute
result = crew.kickoff()
print(result)
```

**RAG with Vector Database (Chroma)**:
```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = Chroma(
    collection_name="rca_reports",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Ingest RCA reports (one-time setup)
def ingest_rca_reports(report_paths: list[str]):
    """Embed 10+ years of RCA PDFs into vector database"""
    documents = []
    for path in report_paths:
        text = extract_text_from_pdf(path)  # Use PyPDF2 or pdfplumber
        metadata = {"source": path, "year": extract_year(path), "product": extract_product(path)}
        documents.append(Document(page_content=text, metadata=metadata))
    
    # Chunk documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # Embed and store
    vectorstore.add_documents(chunks)
    print(f"Ingested {len(chunks)} chunks from {len(report_paths)} RCA reports")

# Retrieval during RCA
def retrieve_similar_rcas(query: str, top_k: int = 5) -> list[Document]:
    """Semantic search for similar historical failures"""
    results = vectorstore.similarity_search(
        query=query,
        k=top_k,
        filter={"product": "TC41x"}  # Optional metadata filtering
    )
    return results

# Example usage in agent
query = "Edge effect pattern on TC41x BGA436 with IDDQ failures"
similar_rcas = retrieve_similar_rcas(query, top_k=5)
for doc in similar_rcas:
    print(f"Source: {doc.metadata['source']}, Similarity: {doc.metadata.get('score', 'N/A')}")
    print(f"Excerpt: {doc.page_content[:200]}...")
```

**Tool Use Framework**:
```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# Define tool input schema
class STDFParserInput(BaseModel):
    lot_id: str = Field(description="Lot identifier (e.g., TC41x_LOT123)")
    wafer_id: str = Field(description="Wafer identifier (e.g., W05)")

# Define tool function
def parse_stdf(lot_id: str, wafer_id: str) -> dict:
    """Parse STDF file and return test data summary"""
    # Real implementation would use pystdf library
    stdf_path = f"/data/stdf/{lot_id}_{wafer_id}.stdf"
    # ... parsing logic ...
    return {
        "die_count": 5000,
        "bin_distribution": {"bin1": 4200, "bin5": 600, "bin99": 200},
        "yield": 0.84,
        "top_failing_tests": ["IDDQ_25C", "Vth_nom", "Fmax_100C"]
    }

# Create LangChain tool
parse_stdf_tool = StructuredTool.from_function(
    func=parse_stdf,
    name="parse_stdf",
    description="Parse STDF file for given lot and wafer, return test data summary",
    args_schema=STDFParserInput
)

# Agent uses tool via function calling
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm_with_tools = llm.bind_tools([parse_stdf_tool])

messages = [{"role": "user", "content": "Parse STDF for lot TC41x_LOT123, wafer W05"}]
response = llm_with_tools.invoke(messages)

# Execute tool if LLM requested it
if response.tool_calls:
    tool_call = response.tool_calls[0]
    tool_output = parse_stdf(**tool_call["args"])
    print(f"Tool Output: {tool_output}")
```

---

## 9. System Architecture

### 9.1 High-Level Architecture

**Multi-Agent RCA Platform Architecture** (ASCII Diagram):

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Web UI       │  │ API Gateway  │  │ WebSocket    │  │ Mobile App   │       │
│  │ (React)      │  │ (FastAPI)    │  │ (Real-time)  │  │ (Future)     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────────────┘       │
└─────────┼──────────────────┼──────────────────┼──────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATION LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    LANGGRAPH STATE MACHINE                               │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐             │  │
│  │  │  START   │──▶│ DataAgent│──▶│ Parallel │──▶│Synthesize│──▶ END      │  │
│  │  └──────────┘   └──────────┘   │Analysis  │   └──────────┘             │  │
│  │                                 │  ┌───┐   │                             │  │
│  │                                 │  │Stat│  │                             │  │
│  │                                 │  ├───┤  │                             │  │
│  │                                 │  │Sptl│  │   Conditional Routing      │  │
│  │                                 │  ├───┤  │   (if edge_effect →        │  │
│  │                                 │  │Corr│  │    route to FA agent)      │  │
│  │                                 │  └───┘   │                             │  │
│  │                                 └──────────┘                             │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    CREWAI HIERARCHICAL TEAMS                             │  │
│  │         ┌──────────────────────────────────────┐                         │  │
│  │         │  ORCHESTRATOR (Manager Agent)        │                         │  │
│  │         │  - Task Decomposition                │                         │  │
│  │         │  - Delegation & Consensus            │                         │  │
│  │         └────────┬────────┬────────┬────────┬──┘                         │  │
│  │                  │        │        │        │                            │  │
│  │         ┌────────▼──┐  ┌──▼─────┐ ┌▼───────┐ ┌▼──────────┐              │  │
│  │         │Data Agent │  │Stat    │ │Spatial │ │Correlation│              │  │
│  │         │(Worker)   │  │Agent   │ │Agent   │ │Agent      │              │  │
│  │         └───────────┘  └────────┘ └────────┘ └───────────┘              │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER (6 Specialized Agents)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │Orchestrator │  │Data Analyst │  │ Statistical │  │  Spatial    │          │
│  │   Agent     │  │   Agent     │  │   Analyst   │  │  Pattern    │          │
│  │             │  │             │  │             │  │  Detector   │          │
│  │- Manages    │  │- STDF Parse │  │- t-test     │  │- Wafer Map  │          │
│  │  workflow   │  │- Wafer Map  │  │- ANOVA      │  │  Classify   │          │
│  │- Delegates  │  │  Generation │  │- Correlation│  │- Pattern    │          │
│  │- Aggregates │  │- SQL Query  │  │- Outliers   │  │  Detection  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                                 │
│  ┌─────────────┐  ┌─────────────┐                                             │
│  │Correlation  │  │   Report    │                                             │
│  │   Hunter    │  │  Generator  │                                             │
│  │             │  │             │                                             │
│  │- Test Pairs │  │- PDF Gen    │                                             │
│  │- Network    │  │- Charts     │                                             │
│  │  Graph      │  │- Templates  │                                             │
│  │- Clustering │  │- Citations  │                                             │
│  └─────────────┘  └─────────────┘                                             │
└────────────────────────────────────────────────────────────────────────────────┘
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                       TOOL & MEMORY LAYER                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │
│  │  TOOL LIBRARY        │  │  SHARED MEMORY       │  │  RAG RETRIEVAL       │ │
│  │                      │  │  (Blackboard)        │  │                      │ │
│  │- STDF Parser         │  │                      │  │- Vector DB           │ │
│  │- Wafer Map Gen       │  │- Agent Messages      │  │  (Chroma/Qdrant)     │ │
│  │- Statistical Tests   │  │- Intermediate        │  │- Embeddings          │ │
│  │- Correlation Matrix  │  │  Findings            │  │  (OpenAI/Local)      │ │
│  │- SQL Queries         │  │- Hypotheses          │  │- Semantic Search     │ │
│  │- PDF Generation      │  │- Confidence Scores   │  │- Re-ranking          │ │
│  │- Custom Tools        │  │                      │  │- 50K+ RCA Reports    │ │
│  │  (Agent-created)     │  │- PostgreSQL Storage  │  │                      │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                          LLM INTEGRATION LAYER                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │
│  │  GPT-4 Turbo API     │  │  Claude 3.5 Sonnet   │  │  Local LLM (Future)  │ │
│  │  (Primary)           │  │  (Fallback)          │  │  (Llama 3.1)         │ │
│  │                      │  │                      │  │                      │ │
│  │- 128K Context        │  │- 200K Context        │  │- On-premise          │ │
│  │- Function Calling    │  │- Tool Use            │  │- Cost Optimization   │ │
│  │- JSON Mode           │  │- Streaming           │  │- Data Privacy        │ │
│  │- Streaming           │  │- Multi-turn Dialog   │  │                      │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐ │
│  │  PostgreSQL 16       │  │  Vector Database     │  │  Object Storage      │ │
│  │                      │  │  (Chroma/Qdrant)     │  │  (MinIO/S3)          │ │
│  │- Agent State         │  │                      │  │                      │ │
│  │- RCA Results         │  │- RCA Embeddings      │  │- STDF Files          │ │
│  │- User Feedback       │  │  (10M+ chunks)       │  │- Wafer Maps (PNG)    │ │
│  │- Chat History        │  │- Test Data           │  │- PDF Reports         │ │
│  │- Tool Outputs        │  │  Embeddings          │  │- 3-Year Retention    │ │
│  │- Audit Logs          │  │- Semantic Index      │  │                      │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘ │
│                                                                                 │
│  ┌──────────────────────┐                                                      │
│  │  Redis 7.2           │                                                      │
│  │                      │                                                      │
│  │- Task Queue          │                                                      │
│  │- Agent Job Scheduler │                                                      │
│  │- LLM Response Cache  │                                                      │
│  │- Session State       │                                                      │
│  └──────────────────────┘                                                      │
└────────────────────────────────────────────────────────────────────────────────┘
```

**Data Flow**: User submits failure → API Gateway → LangGraph routes to Data Agent → STDF parsed, wafer map generated → Parallel analysis (Statistical, Spatial, Correlation agents) → RAG retrieves historical RCAs → ConclusionEngine ranks hypotheses → Report Generator creates PDF → User receives report

### 9.2 Component Details

**Component 1: LangGraph State Machine Orchestrator**
- **Purpose**: Manage agent workflow with conditional routing, cycles, and error handling
- **Technology**: LangGraph 0.2+, Python StateGraph, conditional edges
- **Key Features**:
  - State persistence (checkpoint agent execution for resume/replay)
  - Conditional routing (if spatial pattern = edge_effect → route to FA hypothesis agent)
  - Cycle detection (prevent infinite loops, max 3 iterations)
  - Human-in-the-loop breakpoints (pause for engineer review before high-risk actions)
- **Scalability**: Stateless execution (each RCA session independent, horizontally scalable)

**Component 2: CrewAI Hierarchical Teams**
- **Purpose**: Enable manager-worker agent hierarchy with task delegation
- **Technology**: CrewAI 0.51+, hierarchical Process, task decomposition
- **Key Features**:
  - Orchestrator (manager) delegates tasks to 5 specialist workers
  - Result aggregation (manager synthesizes worker findings)
  - Consensus building (vote on top root cause hypotheses)
  - Dynamic task prioritization (critical findings processed first)
- **Team Structure**: 1 manager + 5 workers (Data, Statistical, Spatial, Correlation, Report)

**Component 3: Shared Memory (Blackboard Architecture)**
- **Purpose**: Enable inter-agent communication and data sharing
- **Technology**: PostgreSQL (structured messages), Vector DB (embeddings), Redis (ephemeral state)
- **Schema**:
  - `agent_messages`: (rca_session_id, agent_name, timestamp, message_type, content, metadata)
  - `intermediate_findings`: (rca_session_id, finding_type, confidence, evidence, source_agent)
  - `hypotheses`: (rca_session_id, hypothesis_text, confidence_score, supporting_evidence, refuting_evidence)
- **Access Patterns**: Agents write findings → Blackboard stores → Other agents read → ConclusionEngine aggregates

**Component 4: Tool Library and Execution Engine**
- **Purpose**: Provide reusable functions for agents to invoke (STDF parsing, stats, wafer maps)
- **Technology**: LangChain StructuredTool, Pydantic schemas, sandboxed execution
- **Tools**:
  - `parse_stdf(lot_id, wafer_id)`: Parse STDF file, return test data summary
  - `generate_wafer_map(stdf_data)`: Create 300x300 PNG wafer map
  - `run_ttest(data, baseline)`: Perform t-test, return p-value
  - `compute_correlation_matrix(data)`: Calculate Pearson correlations for all test pairs
  - `classify_wafer_pattern(image_path)`: CNN classify spatial pattern (edge/center/ring)
  - `query_sql(sql_string)`: Execute SQL query on test data warehouse
  - `generate_pdf_report(findings)`: Create 10-page PDF with charts, tables, citations
- **Execution**: Tool inputs validated via Pydantic, executed in Docker sandbox, outputs logged

**Component 5: RAG Retrieval System**
- **Purpose**: Semantic search over 10+ years of historical RCA reports
- **Technology**: Chroma/Qdrant vector DB, OpenAI embeddings (text-embedding-3-large), LangChain retrievers
- **Pipeline**:
  1. User query → Embed query vector (3072-dim)
  2. Similarity search in vector DB (cosine similarity, top-k=20)
  3. Metadata filtering (product family, bin, year range)
  4. Re-rank with cross-encoder (ms-marco-MiniLM, top-k=5)
  5. Return top-5 RCA reports with citations and similarity scores
- **Knowledge Base**: 50,000 RCA PDFs → 10M chunks (avg 1000 chars/chunk, 200 overlap)

**Component 6: LLM Integration Layer**
- **Purpose**: Provide agent reasoning via GPT-4/Claude APIs with fallback and error handling
- **Primary LLM**: GPT-4-turbo (gpt-4-turbo-2024-04-09, 128K context, $0.01/1K input tokens, $0.03/1K output tokens)
- **Fallback LLM**: Claude 3.5 Sonnet (200K context, if OpenAI API down)
- **Features**:
  - Function calling (agents invoke tools via OpenAI function calling API)
  - Streaming responses (real-time agent reasoning in UI via websockets)
  - JSON mode (structured outputs for hypothesis ranking)
  - Error handling (exponential backoff for rate limits, retry on timeouts)
- **Token Management**: Track usage per RCA (target <50K tokens = $0.50 cost)

### 9.3 Data Flow

**RCA Execution Flow** (Detailed):

```
1. USER INPUT
   └─▶ Web UI: User uploads STDF or specifies lot/wafer/bin
       └─▶ POST /api/v1/rca/submit
           └─▶ RCA Session Created (ID: rca_20251204_001)

2. DATA INGESTION (Data Agent)
   └─▶ Retrieve STDF file from object storage (MinIO)
   └─▶ Parse STDF with pystdf → Extract: die coordinates, bins, parametric data
   └─▶ Generate wafer map (300x300 PNG) from die (x,y,bin) data
   └─▶ Store parsed data in Parquet format (PostgreSQL + S3)
   └─▶ Write to Blackboard: "STDF parsed, 5000 die, 12% bin5 rate, wafer map ready"

3. PARALLEL ANALYSIS (3 Agents Run Simultaneously)
   
   3a. STATISTICAL AGENT
       └─▶ Load test data from Blackboard
       └─▶ Run t-test: bin5 rate (12%) vs. baseline (5%) → p=0.001 (significant)
       └─▶ Compute correlation matrix: 1000 tests → 500K pairs → 15 pairs |r|>0.7
       └─▶ Detect outliers: Z-score >3 for IDDQ_25C (50 die)
       └─▶ Write to Blackboard: "Bin5 rate statistically elevated, IDDQ/Vth correlated (r=0.82)"
   
   3b. SPATIAL AGENT
       └─▶ Load wafer map PNG from Blackboard
       └─▶ Classify pattern with ResNet-ONNX: edge_effect (confidence=0.92)
       └─▶ Detect clusters with DBSCAN: 3 clusters at wafer periphery
       └─▶ Annotate wafer map with pattern overlay (red mask on edge region)
       └─▶ Write to Blackboard: "Edge effect detected (92% confidence), peripheral cluster failures"
   
   3c. CORRELATION AGENT
       └─▶ Load parametric data from Blackboard
       └─▶ Build correlation network graph: nodes=tests, edges=|r|>0.7
       └─▶ Community detection: Tests {IDDQ_25C, Vth_nom, Ileak_hot} cluster together
       └─▶ Hypothesis: "Leakage-related failures (IDDQ/Vth/Ileak correlated)"
       └─▶ Write to Blackboard: "Test cluster identified: leakage block failures"

4. RAG RETRIEVAL (Parallel with Analysis)
   └─▶ Query: "Edge effect pattern TC41x BGA436 IDDQ failures"
   └─▶ Embed query → Vector search → Top-20 similar RCAs
   └─▶ Metadata filter: product=TC41x, year>=2022
   └─▶ Re-rank with cross-encoder → Top-5 RCAs
   └─▶ Retrieved RCAs:
       - RCA-2023-0456: TC41x edge effect → package stress → recommend stress test
       - RCA-2023-1022: BGA436 peripheral failures → solder void → FA confirmed
       - RCA-2024-0123: IDDQ edge correlation → junction leakage → temperature sensitivity
   └─▶ Write to Blackboard: "5 historical precedents retrieved, 3 match edge+IDDQ pattern"

5. SYNTHESIS (ConclusionEngine Agent)
   └─▶ Read all findings from Blackboard:
       - Statistical: bin5 rate elevated (p<0.001), IDDQ/Vth correlated
       - Spatial: edge effect (92% confidence)
       - Correlation: leakage test cluster
       - RAG: 3 historical RCAs match pattern (package stress, solder void, junction leakage)
   └─▶ LLM prompt:
       """
       Synthesize findings and rank root cause hypotheses.
       Statistical: bin5 rate 12% vs 5% baseline (p<0.001), IDDQ/Vth r=0.82
       Spatial: edge effect 92% confidence
       Correlation: IDDQ/Vth/Ileak cluster
       Historical: RCA-2023-0456 (package stress), RCA-2023-1022 (solder void), RCA-2024-0123 (junction leakage)
       Rank top-3 hypotheses by confidence.
       """
   └─▶ LLM response:
       [
         {"hypothesis": "Package stress (thermal/mechanical) causing peripheral die failures", 
          "confidence": 85, 
          "evidence": ["edge effect pattern", "historical RCA-2023-0456", "BGA436 package type"]},
         {"hypothesis": "Solder void under peripheral die causing electrical opens", 
          "confidence": 75, 
          "evidence": ["edge failures", "RCA-2023-1022 precedent", "IDDQ elevated"]},
         {"hypothesis": "Junction leakage due to edge process variation", 
          "confidence": 65, 
          "evidence": ["IDDQ/Vth correlation", "RCA-2024-0123", "leakage test cluster"]}
       ]
   └─▶ Write to Blackboard: "Top-3 hypotheses ranked"

6. REPORT GENERATION (Report Generator Agent)
   └─▶ Read all findings from Blackboard
   └─▶ Generate PDF report using ReportLab template:
       - Executive Summary (1 page): Top root cause, confidence, recommended actions
       - Data Overview (2 pages): Lot info, wafer map, bin distribution Pareto
       - Spatial Analysis (2 pages): Wafer map with pattern overlay, cluster analysis
       - Statistical Findings (2 pages): t-test results, correlation matrix heatmap
       - Historical Context (1 page): Top-3 similar RCAs with citations
       - Root Cause Hypotheses (1 page): Ranked top-3 with evidence
       - Recommended Actions (1 page): Next steps (FA, stress test, limit changes)
   └─▶ Upload PDF to S3: s3://rca-reports/rca_20251204_001.pdf
   └─▶ Send email notification to user with PDF link

7. USER FEEDBACK (Human-in-the-Loop)
   └─▶ User reviews RCA report
   └─▶ Rates accuracy: 4/5 stars
   └─▶ Confirms root cause: "Package stress confirmed by FA (crack observed)"
   └─▶ Feedback stored in PostgreSQL (rca_session_id, rating, correctness, comments)
   └─▶ RLHF pipeline: Use feedback to fine-tune agent prompts (future)

8. KNOWLEDGE BASE UPDATE
   └─▶ Embed completed RCA report into vector database
   └─▶ Chunk report (1000 chars/chunk, 200 overlap) → 50 chunks
   └─▶ Generate embeddings (OpenAI text-embedding-3-large) → 50 vectors (3072-dim each)
   └─▶ Store in Chroma/Qdrant with metadata: {product: TC41x, bin: 5, pattern: edge_effect, root_cause: package_stress, year: 2025}
   └─▶ Future RCAs can retrieve this report via RAG
```

**Agent Communication Protocol**:
- Agents write to shared Blackboard (PostgreSQL table: `agent_messages`)
- Message format: `{"agent": "StatisticalAgent", "timestamp": "2025-12-04T10:30:00Z", "finding": "Bin rate elevated (p<0.001)", "confidence": 0.95}`
- ConclusionEngine reads all messages, aggregates findings, ranks hypotheses
- UI displays agent communication graph (websockets push real-time updates)

---

## 10. Data Model

### 10.1 Entity Relationships

**Core Entities**:
1. **RCA Session**: Represents one RCA investigation (lot, wafer, bin, status, findings, results)
2. **Agent**: Represents one specialized AI agent (name, role, tools, LLM config)
3. **Agent Message**: Communication between agents (session, sender, receiver, content, timestamp)
4. **Tool Execution**: Record of tool invocations (session, tool name, inputs, outputs, duration)
5. **Hypothesis**: Root cause hypothesis (session, hypothesis text, confidence, evidence, rank)
6. **User Feedback**: Human ratings and corrections (session, user, rating, correctness, comments)
7. **RCA Report**: Final PDF report (session, file path, created timestamp, metadata)
8. **Knowledge Base Entry**: Embedded RCA report chunk (text, embedding vector, metadata)

**Entity Relationships** (ERD):

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  RCA Session    │1      N │  Agent Message  │N      1 │     Agent       │
│─────────────────│◄────────┤─────────────────├────────►│─────────────────│
│PK session_id    │         │PK message_id    │         │PK agent_id      │
│   lot_id        │         │FK session_id    │         │   name          │
│   wafer_id      │         │FK sender_agent  │         │   role          │
│   bin           │         │FK receiver_agent│         │   tools[]       │
│   status        │         │   content       │         │   llm_config    │
│   created_at    │         │   timestamp     │         │   version       │
│   completed_at  │         │   message_type  │         └─────────────────┘
└────────┬────────┘         └─────────────────┘
         │                                              
         │1                                             
         │                                              
         │N                                             
┌────────▼────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Hypothesis     │         │ Tool Execution  │         │ User Feedback   │
│─────────────────│         │─────────────────│         │─────────────────│
│PK hypothesis_id │         │PK execution_id  │         │PK feedback_id   │
│FK session_id    │         │FK session_id    │         │FK session_id    │
│   hypothesis    │         │   tool_name     │         │FK user_id       │
│   confidence    │         │   inputs        │         │   rating (1-5)  │
│   evidence[]    │         │   outputs       │         │   correctness   │
│   rank          │         │   duration_ms   │         │   comments      │
│   created_at    │         │   success       │         │   timestamp     │
└─────────────────┘         │   error_msg     │         └─────────────────┘
                            │   timestamp     │
                            └─────────────────┘
         │1                                             
         │                                              
         │N                                             
┌────────▼────────┐         ┌─────────────────┐
│   RCA Report    │         │ KB Entry (Vec)  │
│─────────────────│         │─────────────────│
│PK report_id     │         │PK entry_id      │
│FK session_id    │         │   chunk_text    │
│   file_path     │         │   embedding[]   │
│   file_size     │         │   metadata      │
│   created_at    │         │   source_doc    │
│   metadata      │         │   chunk_index   │
└─────────────────┘         └─────────────────┘
```

**Relationships**:
- RCA Session 1:N Agent Messages (one session has many agent communications)
- RCA Session 1:N Tool Executions (one session has many tool invocations)
- RCA Session 1:N Hypotheses (one session produces multiple root cause hypotheses)
- RCA Session 1:1 RCA Report (one session generates one final PDF report)
- RCA Session 1:N User Feedback (one session can have feedback from multiple engineers)
- Agent 1:N Agent Messages (one agent sends many messages across sessions)

### 10.2 Database Schema

**PostgreSQL Schema** (Relational Data):

```sql
-- RCA Sessions Table
CREATE TABLE rca_sessions (
    session_id VARCHAR(50) PRIMARY KEY,  -- e.g., "rca_20251204_001"
    lot_id VARCHAR(50) NOT NULL,
    wafer_id VARCHAR(20),
    bin INTEGER,
    product_family VARCHAR(50),  -- TC3x, TC4x
    package_type VARCHAR(50),    -- BGA436, BGA292
    status VARCHAR(20) NOT NULL,  -- queued, running, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_duration_sec INTEGER,
    error_message TEXT,
    metadata JSONB,  -- flexible metadata (tester, operator, etc.)
    INDEX idx_lot_wafer (lot_id, wafer_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
);

-- Agents Table
CREATE TABLE agents (
    agent_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- "DataAnalyst", "StatisticalAnalyst"
    role VARCHAR(200),  -- "Parse STDF and generate wafer maps"
    tools TEXT[],  -- ["parse_stdf", "generate_wafer_map"]
    llm_model VARCHAR(50),  -- "gpt-4-turbo", "claude-3.5-sonnet"
    llm_temperature FLOAT DEFAULT 0.0,
    prompt_template TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent Messages (Blackboard)
CREATE TABLE agent_messages (
    message_id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES rca_sessions(session_id) ON DELETE CASCADE,
    sender_agent_id INTEGER REFERENCES agents(agent_id),
    receiver_agent_id INTEGER REFERENCES agents(agent_id),  -- NULL for broadcast
    message_type VARCHAR(50),  -- "finding", "hypothesis", "question", "answer"
    content JSONB NOT NULL,  -- flexible content structure
    confidence FLOAT,  -- 0.0 to 1.0
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_session (session_id, timestamp),
    INDEX idx_sender (sender_agent_id)
);

-- Tool Executions
CREATE TABLE tool_executions (
    execution_id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES rca_sessions(session_id) ON DELETE CASCADE,
    agent_id INTEGER REFERENCES agents(agent_id),
    tool_name VARCHAR(100) NOT NULL,
    inputs JSONB,
    outputs JSONB,
    duration_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_session_tool (session_id, tool_name),
    INDEX idx_duration (duration_ms DESC)
);

-- Hypotheses
CREATE TABLE hypotheses (
    hypothesis_id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES rca_sessions(session_id) ON DELETE CASCADE,
    hypothesis_text TEXT NOT NULL,
    confidence FLOAT NOT NULL,  -- 0.0 to 1.0
    evidence JSONB,  -- [{type: "statistical", detail: "p<0.001"}, ...]
    refuting_evidence JSONB,
    rank INTEGER,  -- 1 = most likely
    created_by_agent_id INTEGER REFERENCES agents(agent_id),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_session_rank (session_id, rank)
);

-- User Feedback
CREATE TABLE user_feedback (
    feedback_id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES rca_sessions(session_id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,  -- engineer email or ID
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    correctness VARCHAR(20),  -- "correct", "incorrect", "partial"
    comments TEXT,
    confirmed_root_cause TEXT,  -- engineer's actual root cause (for training)
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_session (session_id),
    INDEX idx_user (user_id)
);

-- RCA Reports
CREATE TABLE rca_reports (
    report_id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE REFERENCES rca_sessions(session_id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,  -- S3: s3://rca-reports/rca_20251204_001.pdf
    file_size_bytes INTEGER,
    page_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB  -- {top_hypothesis: "package stress", confidence: 0.85}
);

-- STDF Data Cache (Parsed Test Data)
CREATE TABLE stdf_data_cache (
    cache_id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50) NOT NULL,
    wafer_id VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),  -- S3 path to original STDF
    parquet_path VARCHAR(500),  -- S3 path to parsed Parquet
    die_count INTEGER,
    bin_distribution JSONB,  -- {"bin1": 4200, "bin5": 600}
    yield FLOAT,
    parsed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (lot_id, wafer_id),
    INDEX idx_lot (lot_id)
);

-- Wafer Maps
CREATE TABLE wafer_maps (
    map_id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50) NOT NULL,
    wafer_id VARCHAR(20) NOT NULL,
    bin INTEGER,
    image_path VARCHAR(500),  -- S3: s3://wafer-maps/TC41x_LOT123_W05_bin5.png
    pattern_type VARCHAR(50),  -- "edge_effect", "center_cluster", "ring"
    pattern_confidence FLOAT,
    generated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_lot_wafer (lot_id, wafer_id)
);
```

**Vector Database Schema** (Chroma/Qdrant):

```python
# Chroma Collection Schema
collection_name = "rca_knowledge_base"

# Document structure
{
    "id": "rca_2023_0456_chunk_001",  # Unique chunk ID
    "embedding": [0.123, -0.456, ..., 0.789],  # 3072-dim vector (OpenAI embedding)
    "metadata": {
        "source_report_id": "rca_2023_0456",
        "source_file": "s3://rca-archive/2023/RCA-2023-0456.pdf",
        "lot_id": "TC41x_LOT456",
        "wafer_id": "W12",
        "bin": 5,
        "product_family": "TC41x",
        "package_type": "BGA436",
        "root_cause": "package_stress",
        "spatial_pattern": "edge_effect",
        "year": 2023,
        "chunk_index": 1,  # 1 of 50 chunks
        "page_number": 3,
        "section": "Statistical Analysis"
    },
    "document": "Statistical analysis revealed bin 5 failures concentrated at wafer periphery (p<0.001 vs. center die). T-test confirmed significant difference in IDDQ distribution between edge and center die (edge mean: 125μA, center mean: 85μA, p=0.0003). Correlation analysis identified high correlation between IDDQ_25C and Vth_nom (r=0.82), suggesting leakage-related failure mode. Historical precedent: RCA-2022-0789 observed similar edge effect on TC41x attributed to package-induced stress."
}

# Indexing
- HNSW index (Hierarchical Navigable Small World) for fast approximate nearest neighbor search
- Distance metric: Cosine similarity
- Index parameters: M=16, ef_construction=200, ef_search=50
- Estimated QPS: 1000+ queries/sec for 10M vectors
```

### 10.3 Data Flow Diagrams

**STDF Ingestion Pipeline**:

```
┌──────────────┐
│ Test Station │  (Advantest V93000)
│  (ATE)       │
└──────┬───────┘
       │ STDF File Generated
       ▼
┌──────────────────┐
│ Object Storage   │  (MinIO/S3)
│ /stdf/raw/       │  TC41x_LOT123_W05.stdf (binary)
└──────┬───────────┘
       │ RCA Session Created
       ▼
┌──────────────────┐
│ Data Agent       │  1. Download STDF from S3
│ (parse_stdf tool)│  2. Parse with pystdf library
└──────┬───────────┘  3. Extract: lot, wafer, die (x,y), bin, parametric data
       │
       ▼
┌──────────────────┐
│ Parquet Writer   │  Convert to columnar format
│                  │  Schema: [die_id, x, y, bin, test_1, test_2, ..., test_1000]
└──────┬───────────┘
       │
       ├──────────────────────┬─────────────────────┐
       ▼                      ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ PostgreSQL   │    │ Object Store │    │ Redis Cache  │
│ (Metadata)   │    │ (Parquet)    │    │ (Hot Data)   │
│              │    │              │    │              │
│ stdf_data_   │    │ s3://stdf/   │    │ Key: lot_123 │
│  cache       │    │  parsed/     │    │ Val: summary │
│ - lot_id     │    │ TC41x_LOT123 │    │ TTL: 24hr    │
│ - die_count  │    │  _W05.parquet│    └──────────────┘
│ - yield      │    └──────────────┘
│ - bin_dist   │
└──────────────┘
       │
       ▼
┌──────────────────┐
│ Wafer Map Gen    │  generate_wafer_map(parquet_data)
│ (OpenCV)         │  - Read die (x,y,bin)
└──────┬───────────┘  - Create 300x300 RGB image
       │              - Color code by bin (bin1=green, bin5=red)
       ▼
┌──────────────────┐
│ Object Storage   │  s3://wafer-maps/TC41x_LOT123_W05_bin5.png
│ /wafer-maps/     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Blackboard       │  Data Agent writes:
│ (PostgreSQL)     │  "STDF parsed: 5000 die, 12% bin5, wafer map ready"
└──────────────────┘
```

**RAG Retrieval Pipeline**:

```
┌──────────────────┐
│ User Query /     │  "Why did lot TC41x_LOT123 fail bin 5?"
│ Agent Query      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Query Processor  │  1. Extract entities: product=TC41x, bin=5
│                  │  2. Formulate semantic query: "TC41x bin 5 failures"
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Embedding Model  │  OpenAI text-embedding-3-large
│                  │  query → 3072-dim vector
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Vector Database  │  Chroma/Qdrant HNSW index
│ (Chroma/Qdrant)  │  1. Cosine similarity search
└──────┬───────────┘  2. Return top-k=20 similar chunks
       │
       │  [20 chunks with similarity scores 0.95, 0.92, 0.88, ...]
       ▼
┌──────────────────┐
│ Metadata Filter  │  Filter by:
│                  │  - product_family = "TC41x"
└──────┬───────────┘  - year >= 2022 (recent RCAs only)
       │              - bin = 5 or bin = 99 (similar failure bins)
       │
       │  [15 chunks after filtering]
       ▼
┌──────────────────┐
│ Re-ranker        │  Cross-encoder model (ms-marco-MiniLM)
│ (Cross-Encoder)  │  1. Score each (query, chunk) pair
└──────┬───────────┘  2. Re-rank by relevance (not just embedding similarity)
       │
       │  [Top-5 chunks after re-ranking]
       ▼
┌──────────────────┐
│ Context Builder  │  1. Retrieve full RCA reports for top-5 chunks
│                  │  2. Extract: root cause, corrective action, FA findings
└──────┬───────────┘  3. Format citations (report ID, page, section)
       │
       ▼
┌──────────────────┐
│ LLM Context      │  Augment agent prompt with retrieved RCAs:
│ Augmentation     │  """
└──────────────────┘  Similar historical failures:
                      - RCA-2023-0456: TC41x bin5 edge effect → package stress
                      - RCA-2024-0123: TC41x bin5 IDDQ → junction leakage
                      ...
                      """
       │
       ▼
┌──────────────────┐
│ Agent Reasoning  │  LLM generates hypothesis using RAG context
│ (GPT-4/Claude)   │
└──────────────────┘
```

### 10.4 Input Data & Dataset Requirements

**STDF Files**:
- **Format**: Binary (IEEE 1445-1999 Standard Test Data Format)
- **Size**: 50MB - 2GB per wafer (depends on test count, die count)
- **Structure**: Records (MIR, WIR, PIR, PTR, FTR, WRR, MRR)
  - MIR: Master Information Record (lot, product, tester)
  - WIR: Wafer Information Record (wafer ID, die count)
  - PIR: Part Information Record (die x, y coordinates)
  - PTR: Parametric Test Record (test number, result, limits)
  - FTR: Functional Test Record (bin number, pass/fail flags)
  - WRR: Wafer Results Record (bin summary, yield)
- **Retention**: 3 years minimum (compliance requirement)
- **Volume**: 1000+ STDF files/month (20 lots/day × 50 wafers/lot)

**Historical RCA Reports** (Knowledge Base):
- **Format**: PDF (10-20 pages each), Word (DOCX), Plain Text
- **Count**: 50,000+ reports (10 years of RCA history)
- **Content**: Executive summary, data plots, statistical analysis, root cause conclusion, corrective actions, FA images
- **Chunking**: 1000 characters/chunk, 200 character overlap → 10M chunks
- **Embeddings**: OpenAI text-embedding-3-large (3072-dim) → 10M vectors × 12KB/vector = 120GB vector storage
- **Metadata**: Product, bin, year, root cause category, spatial pattern, engineer name

**Wafer Maps**:
- **Format**: PNG (300×300 RGB), TIFF (high-res 1024×1024 for FA)
- **Generation**: From STDF die (x,y,bin) data using OpenCV/PIL
- **Color Coding**: Bin1=green (pass), Bin5=red (fail), Bin99=black (scrap)
- **Storage**: S3/MinIO, ~100KB/image, 50K images/year = 5GB/year

**Test Data Warehouse** (Parametric Trends):
- **Format**: Parquet (columnar storage for efficient querying)
- **Schema**: [lot_id, wafer_id, die_id, x, y, bin, test_1, test_2, ..., test_1000]
- **Row Count**: 5000 die/wafer × 50 wafers/lot × 1000 lots/year = 250M rows/year
- **Column Count**: 1000 parametric tests + metadata = ~1010 columns
- **Storage**: Parquet compression → 50GB/year (vs. 500GB uncompressed CSV)

---

## 11. API Specifications

### 11.1 REST Endpoints

**Base URL**: `https://rca-platform.internal/api/v1`

**Authentication**: OAuth2 Bearer Token (JWT)

**API Endpoints**:

**1. Submit RCA Request**
```http
POST /api/v1/rca/submit
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "lot_id": "TC41x_LOT123",
  "wafer_id": "W05",
  "bin": 5,
  "priority": "normal",  // "low", "normal", "high", "critical"
  "requester": "mike.engineer@company.com",
  "notes": "High bin 5 rate observed, edge failures suspected"
}

Response 201 Created:
{
  "session_id": "rca_20251204_001",
  "status": "queued",
  "estimated_completion_min": 25,
  "created_at": "2025-12-04T10:00:00Z",
  "websocket_url": "wss://rca-platform.internal/ws/rca_20251204_001"
}
```

**2. Get RCA Status**
```http
GET /api/v1/rca/{session_id}/status
Authorization: Bearer <JWT_TOKEN>

Response 200 OK:
{
  "session_id": "rca_20251204_001",
  "status": "running",  // queued, running, completed, failed
  "progress_percent": 65,
  "current_agent": "SpatialAnalyst",
  "elapsed_sec": 780,
  "estimated_remaining_sec": 420,
  "agents_completed": ["DataAnalyst", "StatisticalAnalyst"],
  "agents_running": ["SpatialAnalyst", "CorrelationHunter"],
  "agents_pending": ["ConclusionEngine", "ReportGenerator"]
}
```

**3. Get RCA Results**
```http
GET /api/v1/rca/{session_id}/results
Authorization: Bearer <JWT_TOKEN>

Response 200 OK:
{
  "session_id": "rca_20251204_001",
  "status": "completed",
  "lot_id": "TC41x_LOT123",
  "wafer_id": "W05",
  "bin": 5,
  "hypotheses": [
    {
      "rank": 1,
      "hypothesis": "Package stress (thermal/mechanical) causing peripheral die failures",
      "confidence": 0.85,
      "evidence": [
        {"type": "spatial", "detail": "Edge effect pattern detected (92% confidence)"},
        {"type": "historical", "detail": "RCA-2023-0456: Similar TC41x edge failures → package stress"},
        {"type": "product", "detail": "BGA436 package known for stress sensitivity"}
      ]
    },
    {
      "rank": 2,
      "hypothesis": "Solder void under peripheral die causing electrical opens",
      "confidence": 0.75,
      "evidence": [
        {"type": "spatial", "detail": "Peripheral die failures concentrated"},
        {"type": "historical", "detail": "RCA-2023-1022: BGA436 solder voids → edge failures"},
        {"type": "parametric", "detail": "IDDQ elevated (junction leakage or open)"}
      ]
    }
  ],
  "report_url": "https://rca-platform.internal/api/v1/reports/rca_20251204_001.pdf",
  "wafer_map_url": "https://minio.internal/wafer-maps/TC41x_LOT123_W05_bin5.png",
  "completed_at": "2025-12-04T10:20:15Z",
  "total_duration_sec": 1215
}
```

**4. Download RCA Report PDF**
```http
GET /api/v1/reports/{session_id}.pdf
Authorization: Bearer <JWT_TOKEN>

Response 200 OK:
Content-Type: application/pdf
Content-Disposition: attachment; filename="rca_20251204_001.pdf"

<PDF binary data>
```

**5. Submit User Feedback**
```http
POST /api/v1/rca/{session_id}/feedback
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "rating": 4,  // 1-5
  "correctness": "correct",  // "correct", "incorrect", "partial"
  "comments": "Package stress confirmed by FA (crack observed at die edge)",
  "confirmed_root_cause": "Package-induced mechanical stress causing junction damage"
}

Response 201 Created:
{
  "feedback_id": 12345,
  "session_id": "rca_20251204_001",
  "thank_you": "Feedback received. This will improve future RCA accuracy."
}
```

**6. List RCA Sessions** (with pagination and filtering)
```http
GET /api/v1/rca/sessions?page=1&page_size=20&status=completed&product=TC41x&from_date=2025-12-01
Authorization: Bearer <JWT_TOKEN>

Response 200 OK:
{
  "total_count": 150,
  "page": 1,
  "page_size": 20,
  "sessions": [
    {
      "session_id": "rca_20251204_001",
      "lot_id": "TC41x_LOT123",
      "wafer_id": "W05",
      "bin": 5,
      "status": "completed",
      "top_hypothesis": "Package stress",
      "confidence": 0.85,
      "created_at": "2025-12-04T10:00:00Z",
      "completed_at": "2025-12-04T10:20:15Z"
    },
    // ... 19 more sessions
  ]
}
```

**7. Get Agent Communication Log**
```http
GET /api/v1/rca/{session_id}/agent_messages
Authorization: Bearer <JWT_TOKEN>

Response 200 OK:
{
  "session_id": "rca_20251204_001",
  "messages": [
    {
      "timestamp": "2025-12-04T10:02:30Z",
      "sender": "DataAnalyst",
      "receiver": null,  // broadcast to all
      "message_type": "finding",
      "content": "STDF parsed: 5000 die, 12% bin5 rate (baseline 5%), wafer map generated",
      "confidence": null
    },
    {
      "timestamp": "2025-12-04T10:08:45Z",
      "sender": "StatisticalAnalyst",
      "receiver": "ConclusionEngine",
      "message_type": "finding",
      "content": "Bin5 rate statistically elevated (p<0.001), IDDQ/Vth correlation r=0.82 (p<0.0001)",
      "confidence": 0.95
    },
    {
      "timestamp": "2025-12-04T10:10:20Z",
      "sender": "SpatialAnalyst",
      "receiver": "ConclusionEngine",
      "message_type": "finding",
      "content": "Edge effect pattern detected (confidence=0.92), peripheral cluster at wafer edge",
      "confidence": 0.92
    }
    // ... more messages
  ]
}
```

**8. Retrieve Similar Historical RCAs** (RAG endpoint)
```http
POST /api/v1/rag/search
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "query": "Edge effect pattern TC41x BGA436 IDDQ failures",
  "filters": {
    "product_family": "TC41x",
    "year_from": 2022
  },
  "top_k": 5
}

Response 200 OK:
{
  "query": "Edge effect pattern TC41x BGA436 IDDQ failures",
  "results": [
    {
      "report_id": "rca_2023_0456",
      "similarity_score": 0.92,
      "lot_id": "TC41x_LOT456",
      "bin": 5,
      "root_cause": "Package stress (thermal/mechanical)",
      "summary": "Edge effect observed on BGA436 package. IDDQ failures concentrated at wafer periphery. FA confirmed package-induced crack at die edge. Corrective action: Reduce assembly temperature from 260°C to 245°C.",
      "report_url": "https://rca-platform.internal/api/v1/reports/rca_2023_0456.pdf",
      "year": 2023
    },
    // ... 4 more results
  ]
}
```

### 11.2 Request/Response Examples

**Example 1: Submit RCA via curl**

```bash
curl -X POST "https://rca-platform.internal/api/v1/rca/submit" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "lot_id": "TC41x_LOT123",
    "wafer_id": "W05",
    "bin": 5,
    "priority": "high",
    "requester": "mike.engineer@company.com",
    "notes": "Suspected edge effect based on manual wafer map review"
  }'

# Response
{
  "session_id": "rca_20251204_001",
  "status": "queued",
  "estimated_completion_min": 25,
  "created_at": "2025-12-04T10:00:00Z",
  "websocket_url": "wss://rca-platform.internal/ws/rca_20251204_001"
}
```

**Example 2: Poll RCA Status via Python**

```python
import requests
import time

API_BASE = "https://rca-platform.internal/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {"Authorization": f"Bearer {TOKEN}"}

session_id = "rca_20251204_001"

while True:
    response = requests.get(f"{API_BASE}/rca/{session_id}/status", headers=headers)
    data = response.json()
    
    print(f"Status: {data['status']}, Progress: {data['progress_percent']}%, Current Agent: {data['current_agent']}")
    
    if data['status'] in ['completed', 'failed']:
        break
    
    time.sleep(10)  # Poll every 10 seconds

# Retrieve results
results = requests.get(f"{API_BASE}/rca/{session_id}/results", headers=headers).json()
print(f"Top Hypothesis: {results['hypotheses'][0]['hypothesis']}")
print(f"Confidence: {results['hypotheses'][0]['confidence']}")
print(f"Report: {results['report_url']}")
```

**Example 3: WebSocket Real-Time Updates (JavaScript)**

```javascript
const ws = new WebSocket('wss://rca-platform.internal/ws/rca_20251204_001?token=eyJhbGci...');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  if (update.type === 'agent_progress') {
    console.log(`${update.agent} (${update.progress}%): ${update.message}`);
    // Example: "DataAnalyst (100%): STDF parsed, 5000 die, wafer map ready"
  } else if (update.type === 'agent_finding') {
    console.log(`Finding from ${update.agent}: ${update.finding} (confidence: ${update.confidence})`);
  } else if (update.type === 'status_change') {
    console.log(`RCA Status: ${update.status}`);
    if (update.status === 'completed') {
      console.log(`Report ready: ${update.report_url}`);
      ws.close();
    }
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### 11.3 Authentication

**OAuth2 with JWT (JSON Web Tokens)**:

**Authentication Flow**:
1. User logs in via company SSO (Azure AD, Okta)
2. Identity provider issues JWT token (valid 8 hours)
3. User includes token in `Authorization: Bearer <token>` header for all API requests
4. API Gateway validates token signature, expiration, claims
5. If valid → request proceeds, if invalid → 401 Unauthorized

**JWT Token Structure**:
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "mike.engineer@company.com",
    "name": "Mike Engineer",
    "roles": ["test_engineer", "rca_user"],
    "iat": 1733312400,  // Issued at
    "exp": 1733341200,  // Expires (8 hours later)
    "iss": "https://auth.company.com",
    "aud": "rca-platform"
  },
  "signature": "..."
}
```

**Role-Based Access Control (RBAC)**:

| Role               | Permissions                                                           |
|--------------------|-----------------------------------------------------------------------|
| `rca_user`         | Submit RCA, view own RCAs, download reports                           |
| `rca_reviewer`     | View all RCAs, submit feedback, access agent communication logs       |
| `rca_admin`        | All above + manage agents, configure LLM settings, view cost metrics |
| `knowledge_curator`| Upload historical RCAs, manage vector database, review embeddings     |

**API Rate Limiting**:
- **Per User**: 100 requests/minute (prevents abuse)
- **Per Organization**: 10,000 requests/hour
- **RCA Submission**: 50 RCAs/day per user (prevents queue overload)
- **WebSocket Connections**: 10 concurrent connections/user

**Security Headers**:
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

---

## 12. UI/UX Requirements

### 12.1 User Interface

**UI-01: RCA Submission Form**
- **Layout**: Single-page form with 4 sections (Failure Info, Priority, Optional Context, Submit)
- **Fields**:
  - Lot ID (required, autocomplete from recent lots)
  - Wafer ID (optional, dropdown populated after lot selected)
  - Bin Number (required, dropdown: 1-99 or "All bins")
  - Priority (required, radio buttons: Low/Normal/High/Critical)
  - Notes (optional, 500 char max, textarea)
  - STDF File Upload (optional, alternative to lot/wafer ID input)
- **Validation**:
  - Lot ID format: `[A-Z0-9]{2,5}_LOT[0-9]{3,6}` (e.g., TC41x_LOT123)
  - STDF file: max 2GB, .stdf or .std extension
  - Show inline validation errors (red border + message below field)
- **Submit Button**: Disabled until required fields valid, green when ready, shows "Submitting..." spinner on click
- **Response**: Success → redirect to RCA status page, Error → show error message banner

**UI-02: RCA Dashboard (List View)**
- **Layout**: Data table with filters, search, pagination
- **Columns**: Session ID, Lot ID, Wafer, Bin, Status (badge), Priority, Top Hypothesis, Confidence, Submitted By, Created, Duration
- **Filters**:
  - Status: All / Queued / Running / Completed / Failed (checkbox multi-select)
  - Product Family: TC3x / TC4x / TC5x (dropdown)
  - Date Range: Last 7 days / Last 30 days / Custom (date picker)
  - Priority: All / Low / Normal / High / Critical
  - My RCAs Only (toggle switch)
- **Search**: Full-text search across lot ID, wafer ID, hypothesis text
- **Pagination**: 20 rows/page, prev/next buttons + page number selector
- **Row Actions**: Click row → navigate to RCA details, Hover → show quick preview tooltip
- **Bulk Actions**: Select multiple rows → Download reports (ZIP), Export to Excel

**UI-03: RCA Status Page (Real-Time)**
- **Header**: Session ID, Lot/Wafer/Bin, Status badge, Progress bar (0-100%)
- **Agent Activity Timeline** (vertical timeline with websocket updates):
  ```
  ✅ DataAnalyst (100%) - Completed at 10:02:30
     └─ STDF parsed: 5000 die, 12% bin5 rate, wafer map generated
  
  🔄 StatisticalAnalyst (85%) - Running (30s elapsed)
     └─ Running t-tests and correlation analysis...
  
  ⏳ SpatialAnalyst (0%) - Queued
  
  ⏳ CorrelationHunter (0%) - Queued
  
  ⏳ ConclusionEngine (0%) - Pending (waiting for parallel agents)
  ```
- **Real-Time Updates**: WebSocket pushes agent progress updates every 5 seconds
- **Agent Communication Graph** (interactive):
  - Nodes: Agent icons (colored by status: green=done, blue=running, gray=pending)
  - Edges: Data flow arrows (hover to see message content)
  - Click node → expand agent details (tools invoked, findings, confidence)
- **Estimated Time Remaining**: Countdown timer (e.g., "~12 minutes remaining")
- **Cancel Button**: Visible if status=queued or running, confirmation dialog before abort

**UI-04: RCA Results Page**
- **Section 1: Executive Summary**
  - Top root cause hypothesis (large font, highlighted box)
  - Confidence score (85%) with visual indicator (progress bar or gauge)
  - Recommended actions (bullet list, actionable items)
  - Quick stats: Duration, Die count, Bin rate, Yield
- **Section 2: Hypotheses Ranking**
  - Accordion list: Rank 1, Rank 2, Rank 3 (expand to see details)
  - Each hypothesis shows:
    - Hypothesis text (bold)
    - Confidence score (percentage + bar)
    - Evidence list (icons: 📊 statistical, 🗺️ spatial, 📚 historical, 🔧 parametric)
    - Expand evidence → show details (e.g., "p<0.001 for bin rate difference")
- **Section 3: Data Visualizations**
  - Wafer map (300×300 PNG) with spatial pattern overlay (red mask on edge failures)
  - Bin distribution Pareto chart (interactive Plotly: hover to see bin%, click to filter)
  - Correlation matrix heatmap (1000×1000 tests, zoom/pan enabled)
  - Parametric trend plots (IDDQ vs. time, Vth distribution histogram)
- **Section 4: Historical Context**
  - Similar RCAs (cards with: report ID, lot, bin, root cause, similarity score)
  - Click card → open historical RCA report in new tab (PDF viewer)
- **Section 5: Agent Activity Log**
  - Collapsible tree view: Agent → Tool Executions → Outputs
  - Example: "StatisticalAnalyst → run_ttest(data, baseline) → p=0.001 (significant)"
- **Download Report Button**: Downloads PDF (10-page comprehensive report)
- **Feedback Section**: Rating stars (1-5), correctness radio (Correct/Incorrect/Partial), comments textarea

**UI-05: Agent Communication Dashboard (Advanced Users)**
- **Purpose**: Deep dive into agent reasoning for debugging, validation, or learning
- **Layout**: 3-column layout (Agent List | Message Timeline | Detail Panel)
- **Column 1: Agent List**
  - 6 agents with status indicators (✅ done, 🔄 running, ⏳ pending, ❌ error)
  - Show key metrics: Messages sent, Tools invoked, Avg confidence
  - Click agent → filter message timeline to that agent's activity
- **Column 2: Message Timeline**
  - Chronological list of all agent messages (scrollable)
  - Color-coded by agent (Data=blue, Statistical=green, Spatial=orange, etc.)
  - Message types: 📢 broadcast, 💬 direct message, 🔍 finding, 💡 hypothesis
  - Hover → show full message content in tooltip
  - Click → show in detail panel (Column 3)
- **Column 3: Detail Panel**
  - Selected message details:
    - Timestamp, sender, receiver
    - Full message content (formatted JSON or natural language)
    - Confidence score (if applicable)
    - Tool outputs (if message contains tool results)
  - Show linked messages (replies, references)
- **Filters**: Agent (multi-select), Message type, Confidence threshold (slider 0-100%)
- **Export**: Download full communication log as JSON or CSV

**UI-06: Knowledge Base Search (RAG Interface)**
- **Search Bar**: Prominent text input, placeholder: "Search 50,000+ historical RCAs..."
- **Filters**: Product (TC3x/TC4x), Year range, Bin number, Root cause category
- **Results List**:
  - Cards showing: Report ID, Lot, Bin, Root cause (bold), Similarity score (if semantic search)
  - Snippet: First 200 chars of matched text (highlighted keywords)
  - Metadata: Year, Product, Submitter
- **Click Result**: Open PDF in embedded viewer (left side) + metadata panel (right side)
- **Semantic Search**: Toggle "Keyword search" vs. "Semantic search (AI-powered)"
- **Related RCAs**: Sidebar showing "Similar to this RCA" (automatic recommendations)

### 12.2 User Experience

**UX-01: Onboarding & First-Time User Experience**
- **Welcome Tour**: Interactive walkthrough on first login (Intro.js or similar)
  - Step 1: "Submit your first RCA here"
  - Step 2: "Monitor real-time agent progress"
  - Step 3: "Review results and provide feedback"
  - Step 4: "Search historical RCAs"
- **Sample RCA**: Pre-loaded demo RCA (lot=DEMO_LOT001) users can explore without submitting real data
- **Help Icons**: Question mark icons next to complex fields (hover → tooltip with explanation)
- **Video Tutorials**: Embedded 2-minute videos for key workflows (Submit RCA, Interpret Results, Use RAG)

**UX-02: Real-Time Feedback & Progress Visibility**
- **WebSocket Live Updates**: Agent progress updates push to UI every 5 seconds (no manual refresh)
- **Progress Bar**: Global progress (0-100%) at top of status page, smooth animations
- **Agent Status Icons**: Animated spinner for running agents, checkmark for completed, hourglass for queued
- **Estimated Time**: Countdown timer updates in real-time (e.g., "~8 minutes remaining" → "~7 minutes 45 seconds")
- **Notifications**: Browser notifications when RCA completes (if user granted permission)

**UX-03: Responsive Design & Mobile Support**
- **Breakpoints**: Desktop (>1200px), Tablet (768-1199px), Mobile (320-767px)
- **Mobile Optimizations**:
  - RCA submission form: Single-column layout, larger touch targets (48×48px min)
  - Dashboard: Card view instead of table (stack columns vertically)
  - Status page: Collapse agent timeline into accordion (expand to see details)
  - Results page: Stack visualizations vertically, pinch-to-zoom for wafer maps
- **Touch Gestures**: Swipe to navigate between sections, pull-to-refresh on dashboard
- **Offline Indicators**: Show banner if websocket connection lost ("Live updates paused, reconnecting...")

**UX-04: Accessibility (WCAG 2.1 AA Compliance)**
- **Keyboard Navigation**: All actions accessible via keyboard (Tab, Enter, Arrow keys)
  - Focus indicators: 3px blue outline on focused elements
  - Skip links: "Skip to main content" at top of page
  - Keyboard shortcuts: ? (help), S (submit RCA), / (search)
- **Screen Reader Support**:
  - ARIA labels on all interactive elements
  - Live regions for real-time updates (agent progress, status changes)
  - Semantic HTML (nav, main, section, article, aside)
- **Color Contrast**: 4.5:1 minimum for text, 3:1 for large text (18pt+)
  - Status badges: Green (completed), Blue (running), Red (failed) with icons (not color-only)
  - Charts: Colorblind-friendly palettes (viridis, cividis)
- **Text Resizing**: Support up to 200% zoom without horizontal scroll
- **Alt Text**: All images/charts have descriptive alt attributes

**UX-05: Error Handling & Recovery**
- **Inline Validation**: Real-time field validation (show errors as user types, not just on submit)
- **Error Messages**: Clear, actionable (❌ "Lot ID must start with product code (TC3x, TC4x)" not "Invalid input")
- **Retry Mechanisms**:
  - If RCA fails → show "Retry" button (resubmit with same parameters)
  - If websocket disconnects → auto-reconnect with exponential backoff, show reconnection status
- **Graceful Degradation**:
  - If websocket unavailable → fall back to polling every 10 seconds
  - If chart library fails → show tabular data instead of visualization
- **Session Recovery**: If browser crashes → restore RCA submission form data from localStorage

**UX-06: Performance Optimization**
- **Lazy Loading**: Load visualizations (charts, wafer maps) only when scrolled into viewport
- **Code Splitting**: Load agent communication dashboard code only when user navigates to that page
- **Image Optimization**: Serve wafer maps as WebP (60% smaller than PNG), fallback to PNG for unsupported browsers
- **Caching**: Cache static assets (CSS, JS, fonts) for 1 year, API responses for 5 minutes (stale-while-revalidate)
- **Pagination**: Load 20 RCAs at a time, infinite scroll or "Load more" button
- **Debouncing**: Search inputs debounced (300ms delay before API call)

### 12.3 Accessibility

**A11Y-01: WCAG 2.1 Level AA Compliance**
- **Perceivable**:
  - Text alternatives for non-text content (alt text for wafer maps, ARIA labels for icons)
  - Captions for video tutorials (auto-generated + manual review)
  - Color contrast ratio >4.5:1 for normal text, >3:1 for large text
  - Text resizable up to 200% without assistive technology
- **Operable**:
  - All functionality available via keyboard (no mouse-only interactions)
  - No keyboard traps (users can navigate in/out of all components)
  - Timing adjustable (extend session timeout, pause auto-refresh)
  - Seizure prevention: No content flashing >3 times/second
- **Understandable**:
  - Consistent navigation (same menu structure on all pages)
  - Error suggestions (not just "Invalid" but "Did you mean TC41x?")
  - Help available (? icon, help text, documentation links)
- **Robust**:
  - Valid HTML5 (passes W3C validator)
  - Compatible with assistive technologies (screen readers, voice control)
  - ARIA landmarks (role="main", role="navigation", role="search")

**A11Y-02: Screen Reader Optimization**
- **ARIA Live Regions**: Announce real-time updates without interrupting user flow
  ```html
  <div role="status" aria-live="polite" aria-atomic="true">
    StatisticalAnalyst completed analysis (confidence: 85%)
  </div>
  ```
- **ARIA Labels**: Descriptive labels for all interactive elements
  ```html
  <button aria-label="Download RCA report as PDF">Download</button>
  <input type="text" aria-label="Search RCAs by lot ID, wafer, or hypothesis" />
  ```
- **Skip Links**: Allow users to skip repetitive navigation
  ```html
  <a href="#main-content" class="skip-link">Skip to main content</a>
  ```

**A11Y-03: Keyboard Navigation**
- **Tab Order**: Logical tab order (top-to-bottom, left-to-right)
- **Focus Management**: After modal closes, return focus to triggering element
- **Keyboard Shortcuts**:
  - `/` - Focus search bar
  - `S` - Open RCA submission form
  - `?` - Show keyboard shortcuts help
  - `Esc` - Close modal/dialog
  - `Arrow keys` - Navigate agent timeline

**A11Y-04: Multi-Language Support (Future)**
- **i18n Framework**: React-i18next for internationalization
- **Supported Languages**: English (primary), German, Chinese (Simplified), Japanese
- **Right-to-Left (RTL)**: Support for Arabic, Hebrew (future)
- **Date/Number Formatting**: Locale-aware (US: 12/04/2025, DE: 04.12.2025)

---

## 13. Security Requirements

### 13.1 Authentication

**AUTH-01: Single Sign-On (SSO) Integration**
- **Supported Providers**: Azure AD (primary), Okta (secondary), Google Workspace (future)
- **Protocol**: OAuth 2.0 / OpenID Connect (OIDC)
- **Flow**:
  1. User clicks "Login" → redirect to SSO provider
  2. User authenticates (username/password + MFA if required)
  3. SSO provider returns authorization code
  4. Backend exchanges code for access token + refresh token
  5. Backend validates token, creates session, issues JWT
  6. Frontend stores JWT in httpOnly cookie (not localStorage, XSS protection)
- **Token Lifetime**:
  - Access token (JWT): 8 hours (short-lived, reduces risk if leaked)
  - Refresh token: 30 days (allows silent renewal without re-login)
  - Session cookie: 8 hours (auto-logout after inactivity)
- **Multi-Factor Authentication (MFA)**: Enforced for admin/reviewer roles, optional for users

**AUTH-02: JWT (JSON Web Token) Management**
- **Signing Algorithm**: RS256 (asymmetric, public key verification)
- **Claims**:
  ```json
  {
    "sub": "mike.engineer@company.com",  // Subject (user ID)
    "name": "Mike Engineer",
    "email": "mike.engineer@company.com",
    "roles": ["test_engineer", "rca_user"],
    "org": "company",
    "iat": 1733312400,  // Issued at
    "exp": 1733341200,  // Expires (8 hours)
    "iss": "https://auth.company.com",  // Issuer
    "aud": "rca-platform"  // Audience
  }
  ```
- **Token Validation** (on every API request):
  - Verify signature with public key (cached from JWKS endpoint)
  - Check expiration (exp > current time)
  - Validate issuer and audience
  - Check token revocation list (Redis cache, 5-min TTL)
- **Token Refresh**: Before expiration, frontend requests new token using refresh token (silent renewal)

**AUTH-03: Session Management**
- **Session Store**: Redis (distributed sessions for multi-pod deployment)
- **Session ID**: Cryptographically random (128-bit, base64-encoded)
- **Session Data**: User ID, roles, preferences, last activity timestamp
- **Timeout**: 8 hours absolute, 30 minutes idle (configurable per role)
- **Concurrent Sessions**: Max 5 sessions per user (prevent credential sharing)
- **Session Termination**:
  - User logout → invalidate session, add JWT to revocation list
  - Password change → invalidate all sessions (force re-login)
  - Admin action → terminate specific user's sessions

### 13.2 Authorization

**AUTHZ-01: Role-Based Access Control (RBAC)**
- **Roles & Permissions**:

| Role               | Submit RCA | View Own RCAs | View All RCAs | Manage Agents | Admin Dashboard | Knowledge Curator |
|--------------------|------------|---------------|---------------|---------------|-----------------|-------------------|
| `rca_user`         | ✅         | ✅            | ❌            | ❌            | ❌              | ❌                |
| `rca_reviewer`     | ✅         | ✅            | ✅            | ❌            | ❌              | ❌                |
| `rca_admin`        | ✅         | ✅            | ✅            | ✅            | ✅              | ✅                |
| `knowledge_curator`| ❌         | ❌            | ✅            | ❌            | ❌              | ✅                |

- **Permission Checks**:
  - Backend: Middleware validates roles before controller execution
  - Frontend: UI elements hidden/disabled if user lacks permission (defense in depth, not primary security)
- **Default Role**: `rca_user` (assigned to all authenticated users)
- **Role Assignment**: Via SSO groups (Azure AD group membership → RCA platform roles)

**AUTHZ-02: Resource-Level Access Control**
- **RCA Sessions**: Users can view only their own RCAs (created_by=user_id) unless role=reviewer/admin
- **Agent Configuration**: Only `rca_admin` can modify agent prompts, tools, LLM settings
- **Knowledge Base**: `knowledge_curator` can upload/delete RCA reports, all roles can search/read
- **User Feedback**: Users can submit feedback only on RCAs they have access to

**AUTHZ-03: API Authorization**
- **Endpoint-Level**:
  ```python
  @app.post("/api/v1/rca/submit")
  @requires_role("rca_user")  # Minimum role required
  def submit_rca(request, current_user):
      # current_user injected by auth middleware
      ...
  
  @app.put("/api/v1/agents/{agent_id}")
  @requires_role("rca_admin")
  def update_agent(agent_id, request, current_user):
      ...
  ```
- **Row-Level Security** (PostgreSQL RLS):
  ```sql
  -- Users can only see their own RCAs
  ALTER TABLE rca_sessions ENABLE ROW LEVEL SECURITY;
  
  CREATE POLICY rca_user_policy ON rca_sessions
    FOR SELECT
    USING (
      created_by = current_user 
      OR current_user IN (SELECT email FROM users WHERE 'rca_reviewer' = ANY(roles))
    );
  ```

### 13.3 Data Protection

**DATA-01: Encryption at Rest**
- **Database**: PostgreSQL Transparent Data Encryption (TDE) with AES-256
  - Master key stored in AWS KMS / Azure Key Vault (hardware security module)
  - Key rotation: Every 90 days (automated)
- **Object Storage**: MinIO/S3 server-side encryption (SSE-S3 or SSE-KMS)
  - STDF files, wafer maps, PDF reports encrypted at rest
  - Bucket policies enforce encryption (reject unencrypted uploads)
- **Vector Database**: Chroma/Qdrant encryption via filesystem encryption (LUKS/dm-crypt on Linux)
- **Backups**: All backups encrypted with separate encryption key (not same as production key)

**DATA-02: Encryption in Transit**
- **TLS 1.3**: All HTTP traffic (API, WebSocket, UI) over TLS 1.3
  - Certificate: Wildcard cert for `*.rca-platform.internal` (auto-renewed via cert-manager)
  - Cipher suites: TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256 (no TLS 1.0/1.1, no weak ciphers)
- **Internal Services**: mTLS (mutual TLS) for service-to-service communication
  - API Gateway ↔ Agent Orchestrator
  - Agent Orchestrator ↔ LLM APIs (if on-premise LLM deployed)
  - Backend ↔ Database (PostgreSQL SSL mode=require)

**DATA-03: Data Masking & Anonymization**
- **PII Redaction**: Sensitive data (engineer names, emails) masked in logs
  - Before: `User mike.engineer@company.com submitted RCA`
  - After: `User user_12345 submitted RCA`
- **Test Data Sanitization**: Production STDF files sanitized before use in dev/staging environments
  - Remove product serial numbers, wafer IDs replaced with synthetic IDs
- **Differential Privacy** (future): Add noise to aggregated statistics to prevent individual die identification

**DATA-04: Data Retention & Deletion**
- **RCA Sessions**: Retain for 3 years (compliance requirement), then auto-archive or delete
- **STDF Files**: Retain for 3 years in object storage, then move to cold storage (S3 Glacier)
- **Agent Logs**: Retain for 90 days (debugging), then delete
- **User Feedback**: Retain indefinitely (model training data), anonymize after 1 year
- **Right to Deletion**: Support GDPR-style deletion requests (delete user's RCAs, feedback, logs within 30 days)

### 13.4 Compliance

**COMP-01: Audit Logging**
- **Events Logged**:
  - Authentication: Login, logout, failed login attempts, MFA challenges
  - Authorization: Role changes, permission denials
  - Data Access: RCA views, report downloads, STDF file access
  - Data Modification: RCA submissions, agent config changes, feedback submissions
  - Administrative: User creation, role assignment, agent deployment
- **Log Format**: Structured JSON with fields (timestamp, user_id, event_type, resource_id, action, result, ip_address, user_agent)
- **Log Storage**: OpenSearch (Elasticsearch) with 1-year retention, daily indices for efficient querying
- **Log Integrity**: Write-once (append-only), cryptographic checksums to detect tampering
- **Access Controls**: Only `rca_admin` can view audit logs

**COMP-02: GDPR Compliance** (if applicable)
- **Data Subject Rights**:
  - Right to Access: Users can export all their RCA data (JSON/CSV download)
  - Right to Rectification: Users can update their profile, correct RCA submissions
  - Right to Erasure: Users can request deletion of their data (30-day SLA)
  - Right to Portability: Export data in machine-readable format (JSON)
- **Consent Management**: Users consent to data processing on first login (checkbox + privacy policy link)
- **Data Processing Agreement**: DPA with LLM providers (OpenAI, Anthropic) for data processing outside EU

**COMP-03: SOC 2 Type II Compliance** (future)
- **Security Controls**: Documented policies for access control, encryption, incident response
- **Availability**: 99.9% uptime SLA, redundant infrastructure, automated failover
- **Confidentiality**: Data classification (public, internal, confidential), access restrictions
- **Annual Audit**: Independent auditor reviews controls, issues SOC 2 report

**COMP-04: Industry Standards**
- **ISO 27001**: Information security management system (ISMS) aligned with ISO 27001 controls
- **NIST Cybersecurity Framework**: Map security controls to NIST CSF categories (Identify, Protect, Detect, Respond, Recover)
- **Semiconductor Industry Standards**: Compliance with JEDEC, SEMI data security guidelines (if applicable)

---

## 14. Performance Requirements

### 14.1 Response Times

**PERF-RT-01: API Latency**
- **RCA Submission** (`POST /api/v1/rca/submit`):
  - **Target**: <500ms p95 (from request to session created response)
  - **Breakdown**: Request validation (50ms), database insert (100ms), queue enqueue (50ms), response serialization (50ms), network (250ms)
- **RCA Status** (`GET /api/v1/rca/{id}/status`):
  - **Target**: <200ms p95
  - **Caching**: Status cached in Redis (5-second TTL), fresh data fetched only if cache miss
- **RCA Results** (`GET /api/v1/rca/{id}/results`):
  - **Target**: <300ms p95
  - **Optimization**: Results cached after RCA completion, served from cache on subsequent requests
- **RAG Search** (`POST /api/v1/rag/search`):
  - **Target**: <1 second p95 (vector search + re-ranking)
  - **Breakdown**: Query embedding (100ms), vector search (300ms), re-ranking (400ms), serialization (200ms)

**PERF-RT-02: End-to-End RCA Latency**
- **Total RCA Duration** (submission to report ready):
  - **Target**: <30 minutes p95 (median: 20 minutes)
  - **Breakdown by Phase**:
    - Data Ingestion (Data Agent): 2 minutes (STDF parse, wafer map gen)
    - Parallel Analysis (Statistical, Spatial, Correlation): 15 minutes (overlapping, run concurrently)
    - RAG Retrieval: 3 minutes (vector search + embedding historical RCAs)
    - Synthesis (LLM reasoning): 5 minutes (GPT-4 API calls, prompt engineering)
    - Report Generation: 5 minutes (PDF creation with charts, tables, plots)
- **Fast Path** (simple failures): <10 minutes (if pattern matches known failure mode, skip deep analysis)
- **Complex Path** (novel failures): <45 minutes (if no historical precedent, agents iterate multiple times)

**PERF-RT-03: LLM API Latency**
- **Agent Reasoning Step** (single LLM API call):
  - **Target**: <5 seconds p95 per call
  - **GPT-4 Turbo**: Typically 2-4 seconds for 1000-token input, 500-token output
  - **Claude 3.5 Sonnet**: Typically 3-5 seconds (slightly slower but higher quality)
- **Streaming Responses**: Use streaming API to show partial responses in real-time (reduce perceived latency)
- **Timeout**: 30-second timeout per LLM call (if exceeded → retry with fallback LLM)

**PERF-RT-04: WebSocket Update Latency**
- **Agent Progress Updates**: Push to UI within 2 seconds of agent state change
- **WebSocket Ping/Pong**: 30-second interval (detect disconnected clients)
- **Reconnection**: Auto-reconnect within 5 seconds if connection drops (exponential backoff: 1s, 2s, 4s, 8s)

### 14.2 Throughput

**PERF-TP-01: RCA Processing Throughput**
- **Target**: 500+ RCAs per day (20-25 RCAs per hour, 24/7 operation)
- **Peak Load**: 50 RCAs per hour (during shift changes when multiple engineers submit backlog)
- **Concurrency**: Support 10 simultaneous RCA sessions (agents running in parallel)
- **Queue Management**: FIFO queue with priority override (critical failures jump to front)

**PERF-TP-02: API Request Throughput**
- **RCA Submission**: 100 requests/minute (5-10 concurrent users submitting)
- **Status Polling**: 1000 requests/minute (50 users polling every 3 seconds)
- **RAG Search**: 50 queries/minute (engineers searching knowledge base)
- **Report Downloads**: 200 downloads/hour (PDF report retrieval)

**PERF-TP-03: Vector Database Throughput**
- **Embedding Insertion**: 1000 chunks/minute (new RCA reports embedded after completion)
- **Similarity Search**: 100 queries/second (RAG retrieval during RCA synthesis)
- **Index Updates**: Support real-time indexing (no batch delays, new RCAs searchable within 5 minutes)

**PERF-TP-04: Data Ingestion Throughput**
- **STDF Parsing**: 50 files/hour (2GB STDF files parsed in <2 minutes each)
- **Wafer Map Generation**: 100 wafer maps/hour (300×300 PNG images generated in <1 minute each)
- **Parquet Conversion**: 1GB/minute (STDF binary → Parquet columnar format)

### 14.3 Resource Usage

**PERF-RU-01: Compute Resources (per RCA session)**
- **CPU**: 2 vCPU average (agent orchestration, tool execution, data parsing)
  - Peak: 4 vCPU during parallel agent analysis (Statistical, Spatial, Correlation running concurrently)
- **Memory**: 8GB RAM average
  - Breakdown: STDF data (2GB), wafer maps (500MB), agent state (1GB), LangGraph checkpoints (500MB), tool outputs (4GB)
- **Disk I/O**: 500MB read/write per RCA
  - Read: STDF files from S3 (200MB), historical RCAs from vector DB (100MB)
  - Write: Parsed Parquet (100MB), wafer maps (10MB), PDF report (5MB), logs (50MB)

**PERF-RU-02: LLM Token Usage (Cost Management)**
- **Target**: <50,000 tokens per RCA average
  - Breakdown: Data Agent (5K tokens), Statistical Agent (10K tokens), Spatial Agent (8K tokens), Correlation Agent (7K tokens), ConclusionEngine (15K tokens), Report Generator (5K tokens)
- **Cost**: ~$0.50 per RCA at GPT-4 Turbo pricing ($0.01/1K input, $0.03/1K output)
  - Input tokens: 30K × $0.01/1K = $0.30
  - Output tokens: 10K × $0.03/1K = $0.30
- **Optimization**:
  - Prompt caching (OpenAI prompt caching reduces repeat tokens by 50%)
  - Structured outputs (JSON mode reduces token waste from unstructured text)
  - Smaller models for simple tasks (use GPT-3.5 for data parsing, GPT-4 only for synthesis)

**PERF-RU-03: Database Resource Usage**
- **PostgreSQL**:
  - Connections: 50 concurrent (connection pooling with PgBouncer)
  - Storage: 100GB (RCA sessions, agent messages, tool executions, feedback)
  - IOPS: 1000 read IOPS, 500 write IOPS (sufficient for 500 RCAs/day)
- **Vector Database** (Chroma/Qdrant):
  - Memory: 32GB RAM (HNSW index for 10M vectors in memory for fast search)
  - Storage: 150GB (10M chunks × 3072-dim embeddings × 4 bytes/float = 120GB + metadata)
  - IOPS: 5000 read IOPS (vector similarity search)
- **Redis**:
  - Memory: 4GB (session data, LLM response cache, task queue)
  - Eviction: LRU (least recently used) when memory full

**PERF-RU-04: Network Bandwidth**
- **LLM API Calls**: 10 Mbps average (50K tokens/RCA × 4 bytes/token × 20 RCAs/hour ≈ 10 Mbps)
- **Object Storage**: 50 Mbps (STDF file downloads, wafer map uploads, PDF uploads)
- **WebSocket**: 1 Mbps (real-time agent updates to 50 concurrent users)
- **Total**: 100 Mbps sustained, 200 Mbps peak

**PERF-RU-05: Cost Estimates (Monthly)**
- **LLM API**: $7,500/month (500 RCAs/day × 30 days × $0.50/RCA)
- **Compute** (Kubernetes): $2,000/month (10 pods × 4 vCPU × 16GB RAM × $0.05/hr × 730 hrs)
- **Database**: $1,500/month (PostgreSQL RDS, Vector DB instance)
- **Storage**: $500/month (1TB object storage for STDF/wafer maps/PDFs)
- **Network**: $300/month (outbound data transfer)
- **Total**: ~$12,000/month infrastructure + LLM costs

---

## 15. Scalability Requirements

### 15.1 Horizontal Scaling

**SCALE-H-01: Agent Orchestration Layer Scaling**
- **Stateless Agents**: Each agent execution is independent (no shared state between RCA sessions)
- **Kubernetes Horizontal Pod Autoscaler (HPA)**:
  ```yaml
  apiVersion: autoscaling/v2
  kind: HorizontalPodAutoscaler
  metadata:
    name: agent-orchestrator-hpa
  spec:
    scaleTargetRef:
      apiVersion: apps/v1
      kind: Deployment
      name: agent-orchestrator
    minReplicas: 3
    maxReplicas: 20
    metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # Scale up if CPU >70%
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80  # Scale up if memory >80%
    - type: Pods
      pods:
        metric:
          name: active_rca_sessions
        target:
          type: AverageValue
          averageValue: "2"  # Max 2 RCA sessions per pod
  ```
- **Load Balancing**: Kubernetes Service with round-robin load balancing across pods
- **Session Affinity**: None required (stateless), any pod can handle any RCA session

**SCALE-H-02: API Gateway Scaling**
- **FastAPI Pods**: 5-15 replicas (auto-scale based on request rate)
- **Metrics**:
  - CPU >70% → scale up
  - Request rate >500 req/min per pod → scale up
  - Response latency p95 >500ms → scale up
- **Max Replicas**: 15 pods (sufficient for 1500 req/min = 90K req/hour)
- **Connection Pooling**: Each pod maintains 10 PostgreSQL connections (via PgBouncer)

**SCALE-H-03: Vector Database Scaling (Qdrant)**
- **Distributed Qdrant Cluster**: 3-node cluster (1 leader + 2 replicas)
- **Sharding**: Collection partitioned across nodes (3.3M vectors/node for 10M total)
- **Replication**: 2× replication factor (every shard replicated to 2 nodes for availability)
- **Read Scaling**: Distribute search queries across replicas (3× read throughput vs single node)
- **Write Scaling**: Leader handles writes, async replication to followers

**SCALE-H-04: LLM API Scaling (External)**
- **Rate Limits**: OpenAI GPT-4 Turbo (10,000 requests/min, 2M tokens/min for enterprise)
- **Fallback Provider**: If OpenAI rate limited → automatic failover to Anthropic Claude
- **Request Queueing**: If both providers rate limited → queue requests in Redis (FIFO), process when capacity available
- **Cost Optimization**: Use smaller models (GPT-3.5) for simple tasks (data parsing), reserve GPT-4 for synthesis

### 15.2 Vertical Scaling

**SCALE-V-01: Database Vertical Scaling**
- **PostgreSQL**: Start with 4 vCPU, 16GB RAM → scale to 16 vCPU, 64GB RAM (AWS RDS db.r6g.4xlarge)
- **Triggers**:
  - Connection count >80% of max connections (800/1000) → increase instance size
  - CPU >80% sustained for 10 minutes → increase vCPU
  - Query latency p95 >200ms → add read replicas or increase RAM (more cache)
- **Max Instance**: 64 vCPU, 256GB RAM (db.r6g.16xlarge, $7,000/month)

**SCALE-V-02: Vector Database Vertical Scaling**
- **Memory-Intensive**: HNSW index loaded in RAM for fast search
- **Start**: 32GB RAM per node (fits 10M vectors + OS overhead)
- **Scale**: 64GB RAM per node (if embedding dimension increases to 4096 or vector count grows to 20M)
- **CPU**: 8 vCPU per node (sufficient for 100 queries/sec, scale to 16 vCPU if needed)

**SCALE-V-03: Redis Vertical Scaling**
- **Start**: 4GB memory (session data, cache, task queue)
- **Scale**: 16GB memory if:
  - Concurrent users >200 (session data grows)
  - LLM response cache hit rate >50% (more cached responses)
  - Task queue depth >1000 (backlog of RCA jobs)
- **Cluster Mode**: If single-node Redis exceeds 64GB, switch to Redis Cluster (sharded)

### 15.3 Load Handling

**SCALE-LH-01: Peak Load Handling**
- **Expected Peak**: 50 RCAs/hour (during shift changes, 8am-9am, 5pm-6pm)
- **Sustained Load**: 20-25 RCAs/hour (24/7 average)
- **Burst Capacity**: Support 100 RCA submissions in 10 minutes (600/hour burst)
- **Strategy**:
  - Auto-scale agent orchestrator to 20 pods (2 RCAs per pod = 40 concurrent RCAs)
  - Queue overflow in Redis (FIFO), process when capacity available
  - Priority queue: Critical failures bypass queue, processed immediately

**SCALE-LH-02: Queueing and Backlog Management**
- **Queue Implementation**: Redis List (LPUSH to enqueue, BRPOP to dequeue)
- **Queue Metrics**:
  - Queue depth (current items waiting)
  - Average wait time (time from submission to processing start)
  - Throughput (RCAs processed/hour)
- **Backlog Alerts**:
  - Queue depth >50 → alert ops team (may need to scale up)
  - Average wait time >30 minutes → alert (users expect <30 min total duration)
- **Queue TTL**: RCAs in queue for >2 hours are failed (prevent stale data processing)

**SCALE-LH-03: Rate Limiting (Per User)**
- **Submission Limit**: 50 RCAs/day per user (prevent queue flooding)
- **API Limit**: 100 requests/minute per user (prevent DoS)
- **Exceeded Behavior**: Return 429 Too Many Requests with Retry-After header
- **Admin Override**: `rca_admin` role can submit unlimited RCAs (for batch imports)

**SCALE-LH-04: Caching Strategy**
- **LLM Response Cache** (Redis):
  - Cache key: hash of (agent prompt + STDF data summary)
  - TTL: 7 days (if same failure pattern recurs, reuse LLM response)
  - Hit rate target: 30% (30% of RCAs match cached patterns)
  - Savings: 30% × 50K tokens/RCA × $0.50 = $0.15 saved per cache hit
- **Vector Search Cache**:
  - Cache RAG retrieval results for common queries
  - TTL: 1 hour (knowledge base updates infrequently)
  - Hit rate: 20%
- **API Response Cache**:
  - Cache RCA status for 5 seconds (reduce database queries)
  - Cache completed RCA results indefinitely (immutable after completion)

---

## 16. Testing Strategy

### 16.1 Unit Testing

**TEST-U-01: Agent Unit Tests**
- **Framework**: pytest 8.2+, pytest-asyncio (for async agent functions)
- **Coverage Target**: >90% for agent code, >85% for tool library
- **Test Scenarios**:
  - **Data Agent**:
    - Parse valid STDF file → assert correct die count, bin distribution, yield
    - Parse invalid STDF (corrupted) → assert error handling, graceful failure
    - Generate wafer map from die data → assert PNG image created, correct dimensions
  - **Statistical Agent**:
    - Run t-test with significantly different data → assert p-value <0.05
    - Run correlation on independent data → assert |r| <0.3
    - Detect outliers with Z-score >3 → assert correct die flagged
  - **Spatial Agent**:
    - Classify edge effect wafer map → assert pattern="edge_effect", confidence >0.8
    - Classify random failure wafer map → assert pattern="random"
  - **ConclusionEngine Agent**:
    - Mock LLM responses → assert hypothesis ranking correct
    - Test consensus building → assert top hypothesis has highest confidence

**Example Unit Test**:
```python
import pytest
from agents.statistical_analyst import StatisticalAnalyst

def test_ttest_significant_difference():
    """Test t-test detects significant bin rate difference"""
    agent = StatisticalAnalyst()
    
    # Mock data: bin5 rate 12% vs baseline 5%
    test_data = {"bin5_rate": 0.12, "sample_size": 5000}
    baseline = {"bin5_rate": 0.05, "sample_size": 10000}
    
    result = agent.run_ttest(test_data, baseline)
    
    assert result["p_value"] < 0.01, "Should detect significant difference"
    assert result["effect_size"] > 0.5, "Effect size should be medium-large"
    assert result["conclusion"] == "significant", "Should conclude significant"

def test_ttest_no_difference():
    """Test t-test does not false-positive when no difference"""
    agent = StatisticalAnalyst()
    
    # Mock data: bin5 rate 5.1% vs baseline 5% (noise)
    test_data = {"bin5_rate": 0.051, "sample_size": 5000}
    baseline = {"bin5_rate": 0.050, "sample_size": 10000}
    
    result = agent.run_ttest(test_data, baseline)
    
    assert result["p_value"] > 0.05, "Should not detect false difference"
    assert result["conclusion"] == "not_significant"
```

**TEST-U-02: Tool Unit Tests**
- **STDF Parser**:
  - Parse sample STDF files (valid, corrupted, empty)
  - Assert correct extraction of MIR, WIR, PTR, FTR records
  - Benchmark: 2GB STDF parsed in <2 minutes
- **Wafer Map Generator**:
  - Generate wafer maps for various patterns (edge, center, ring, random)
  - Assert PNG dimensions (300×300), color coding (bin1=green, bin5=red)
- **PDF Report Generator**:
  - Generate report with mock data
  - Assert PDF page count (10 pages), sections present (Executive Summary, Data Overview, etc.)

**TEST-U-03: LangGraph State Machine Tests**
- **State Transitions**:
  - Test START → DataAgent → ParallelAnalysis → ConclusionEngine → END flow
  - Test conditional routing: if edge_effect detected → route to FA hypothesis agent
  - Test cycle detection: max 3 iterations, then terminate
- **Error Handling**:
  - Simulate agent crash → assert state machine continues with partial results
  - Simulate LLM timeout → assert retry logic kicks in, fallback to Claude

### 16.2 Integration Testing

**TEST-I-01: End-to-End RCA Flow**
- **Framework**: pytest with Docker Compose (spin up PostgreSQL, Redis, Chroma locally)
- **Test Scenario**:
  1. Submit RCA via API (`POST /api/v1/rca/submit` with mock STDF)
  2. Wait for completion (poll status endpoint every 5 seconds, max 5 minutes)
  3. Retrieve results (`GET /api/v1/rca/{id}/results`)
  4. Assert:
     - Status = "completed"
     - Hypotheses list has 3 entries (ranked)
     - Top hypothesis confidence >0.7
     - Report PDF exists at expected S3 path
- **Data**: Use synthetic STDF files with known failure patterns (edge effect, center cluster)

**TEST-I-02: Agent Communication**
- **Test Scenario**: Verify agents write to blackboard and read from it correctly
  1. Data Agent writes "STDF parsed, 5000 die"
  2. Assert message appears in `agent_messages` table
  3. Statistical Agent reads blackboard
  4. Assert Statistical Agent retrieves Data Agent's message
  5. ConclusionEngine reads all agent findings
  6. Assert ConclusionEngine has messages from all agents

**TEST-I-03: RAG Retrieval Integration**
- **Setup**: Seed Chroma with 100 sample RCA reports (known content)
- **Test Scenario**:
  1. Query: "Edge effect TC41x BGA436"
  2. Assert top-5 results returned
  3. Assert results contain known RCA report with "edge_effect" in metadata
  4. Assert similarity scores >0.7 for top result
- **Negative Test**: Query for non-existent pattern → assert graceful handling (empty results or low similarity scores)

**TEST-I-04: LLM API Integration**
- **Test Scenario**: Call GPT-4 API with sample prompt, verify response
  - Prompt: "Rank these root cause hypotheses: [hypothesis1, hypothesis2, hypothesis3]"
  - Assert: Response is valid JSON with 3 hypotheses ranked
  - Assert: Each hypothesis has confidence score (0-1)
- **Fallback Test**: Simulate OpenAI API down (mock 503 error) → assert system falls back to Claude

**TEST-I-05: Database Transactions**
- **Test Scenario**: Concurrent RCA submissions (10 simultaneous)
  - Submit 10 RCAs concurrently (asyncio.gather)
  - Assert all 10 sessions created in database (no race conditions)
  - Assert no duplicate session IDs
  - Assert database connection pool handles load (no connection exhaustion)

### 16.3 Performance Testing

**TEST-P-01: Load Testing (Locust)**
- **Tool**: Locust (Python load testing framework)
- **Scenario**: Simulate 100 concurrent users submitting RCAs
  ```python
  from locust import HttpUser, task, between
  
  class RCAUser(HttpUser):
      wait_time = between(1, 5)  # Wait 1-5 seconds between requests
      
      @task
      def submit_rca(self):
          self.client.post("/api/v1/rca/submit", json={
              "lot_id": "TC41x_LOT123",
              "wafer_id": "W05",
              "bin": 5,
              "priority": "normal"
          }, headers={"Authorization": f"Bearer {self.token}"})
      
      @task(3)  # 3× more frequent than submit
      def get_status(self):
          session_id = self.get_random_session_id()
          self.client.get(f"/api/v1/rca/{session_id}/status")
  ```
- **Metrics**:
  - Request rate: Target 1000 req/min sustained
  - Response time p95: <500ms for API calls
  - Error rate: <1%
- **Pass Criteria**: System handles 100 concurrent users with <1% error rate, <500ms p95 latency

**TEST-P-02: Stress Testing**
- **Scenario**: Push system beyond normal load to find breaking point
  - Start with 50 concurrent users, increase by 50 every 5 minutes
  - Monitor: CPU, memory, database connections, LLM API rate limits
  - Identify: At what point do errors start (database connections exhausted, LLM rate limited)?
- **Expected Breaking Point**: ~200 concurrent users (400 RCAs/hour, 8× normal load)
- **Recovery**: After stress test, verify system recovers gracefully (no stuck processes, queues drain)

**TEST-P-03: Latency Testing**
- **RCA End-to-End Latency**: Measure time from submission to report ready
  - Simple RCA (known pattern): Target <10 minutes
  - Complex RCA (novel pattern): Target <30 minutes
- **Component Latency Breakdown**:
  - STDF parsing: <2 minutes
  - Vector search: <1 second
  - LLM reasoning: <5 seconds per call
  - PDF generation: <5 minutes
- **Pass Criteria**: 95% of RCAs complete in <30 minutes

**TEST-P-04: Throughput Testing**
- **Scenario**: Submit 500 RCAs over 24 hours (sustained load)
  - Batch submit 500 RCAs with 3-minute intervals (simulate 24/7 operation)
  - Monitor queue depth, completion rate, system resource usage
- **Metrics**:
  - Throughput: 500 RCAs/day = 20.8 RCAs/hour average
  - Queue depth: Should remain <10 (system processes faster than submission rate)
  - Completion rate: >95% (less than 25 failures out of 500)

### 16.4 Security Testing

**TEST-S-01: Authentication Testing**
- **JWT Validation**:
  - Test expired token → assert 401 Unauthorized
  - Test invalid signature → assert 401 Unauthorized
  - Test tampered payload (modify user_id) → assert 401 Unauthorized
- **Session Hijacking**:
  - Steal session cookie, use from different IP → assert session invalidated or MFA required
- **Brute Force Protection**:
  - Attempt 10 failed logins → assert account locked for 15 minutes

**TEST-S-02: Authorization Testing**
- **RBAC Enforcement**:
  - `rca_user` attempts to access admin endpoint (`PUT /api/v1/agents/{id}`) → assert 403 Forbidden
  - `rca_user` attempts to view another user's RCA → assert 403 Forbidden
  - `rca_admin` accesses admin endpoint → assert 200 OK
- **Row-Level Security**:
  - User A submits RCA, User B (different user, same role) tries to access → assert 403
  - User A accesses own RCA → assert 200 OK

**TEST-S-03: Input Validation & Injection Testing**
- **SQL Injection**:
  - Submit RCA with malicious lot_id: `' OR '1'='1` → assert input sanitized, no SQL error
  - Use parameterized queries (prevents SQLi)
- **XSS (Cross-Site Scripting)**:
  - Submit RCA with notes: `<script>alert('XSS')</script>` → assert HTML escaped in UI
- **Command Injection**:
  - Attempt to inject shell commands in STDF file path → assert path validation rejects

**TEST-S-04: Penetration Testing (Annual)**
- **Third-Party Audit**: Hire external security firm for annual pen test
- **Scope**: OWASP Top 10 vulnerabilities, API security, authentication/authorization
- **Remediation**: Fix all critical/high findings within 30 days

---

## 17. Deployment Strategy

### 17.1 Deployment Pipeline

**DEPLOY-P-01: CI/CD Pipeline (GitHub Actions)**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install ruff mypy black
      - name: Lint with ruff
        run: ruff check .
      - name: Type check with mypy
        run: mypy src/
      - name: Format check with black
        run: black --check .

  test:
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run unit tests
        run: pytest tests/unit --cov=src --cov-report=xml
      - name: Run integration tests
        run: pytest tests/integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4

  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/company/rca-platform:latest
            ghcr.io/company/rca-platform:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Staging (Kubernetes)
        run: |
          kubectl set image deployment/agent-orchestrator \
            agent-orchestrator=ghcr.io/company/rca-platform:${{ github.sha }} \
            --namespace=staging
          kubectl rollout status deployment/agent-orchestrator --namespace=staging

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production  # Requires manual approval
    steps:
      - name: Deploy to Production (Blue-Green)
        run: |
          # Deploy to green environment (inactive)
          kubectl set image deployment/agent-orchestrator-green \
            agent-orchestrator=ghcr.io/company/rca-platform:${{ github.sha }} \
            --namespace=production
          kubectl rollout status deployment/agent-orchestrator-green --namespace=production
          
          # Run smoke tests on green
          curl -f https://rca-platform-green.internal/health || exit 1
          
          # Switch traffic from blue to green
          kubectl patch service agent-orchestrator \
            -p '{"spec":{"selector":{"version":"green"}}}' \
            --namespace=production
          
          # Wait 5 minutes, monitor metrics
          sleep 300
          
          # If no errors, scale down blue environment
          kubectl scale deployment/agent-orchestrator-blue --replicas=0 --namespace=production
```

**Pipeline Stages**:
1. **Lint** (2 min): ruff, mypy, black → ensure code quality
2. **Test** (10 min): unit tests (>90% coverage), integration tests
3. **Build** (5 min): Docker image build, push to registry
4. **Deploy Staging** (3 min): Auto-deploy to staging Kubernetes cluster
5. **Deploy Production** (manual approval): Blue-green deployment with smoke tests

### 17.2 Environments

**ENV-01: Development Environment**
- **Purpose**: Local development, unit testing
- **Infrastructure**:
  - Docker Compose (PostgreSQL, Redis, Chroma)
  - Mock LLM API (pre-recorded responses, no actual GPT-4 calls)
  - Sample STDF files (synthetic data)
- **Access**: All developers via localhost
- **Data**: Synthetic/anonymized data only (no production data)

**ENV-02: Staging Environment**
- **Purpose**: Integration testing, QA validation, pre-production testing
- **Infrastructure** (Kubernetes cluster):
  - 3 agent orchestrator pods
  - PostgreSQL RDS (smaller instance: db.r6g.large, 2 vCPU, 16GB RAM)
  - Redis single-node (4GB)
  - Chroma single-node (16GB RAM, 1M sample vectors)
  - LLM API: OpenAI dev account (rate limits: 1000 req/min)
- **Data**: Anonymized production STDF files (scrubbed of PII)
- **Access**: Dev team, QA engineers (SSO authentication)
- **Deployment**: Auto-deploy on every commit to `main` branch

**ENV-03: Production Environment**
- **Purpose**: Live system serving end users
- **Infrastructure** (Kubernetes cluster, AWS):
  - 5-15 agent orchestrator pods (HPA auto-scales)
  - PostgreSQL RDS Multi-AZ (db.r6g.2xlarge, 8 vCPU, 64GB RAM)
  - Redis Cluster (3 nodes, 16GB each)
  - Qdrant Cluster (3 nodes, 32GB RAM each, 10M vectors)
  - LLM API: OpenAI enterprise account (rate limits: 10,000 req/min)
- **Data**: Real production STDF files, wafer maps, RCA reports
- **Access**: All users (150 test engineers, 50 yield engineers, 30 FA engineers)
- **Deployment**: Blue-green deployment with manual approval gate
- **High Availability**:
  - Multi-AZ deployment (spread across 3 availability zones)
  - Database: Multi-AZ standby (auto-failover in <60 seconds)
  - Load balancer: AWS ALB with health checks (route traffic only to healthy pods)

**ENV-04: Disaster Recovery (DR) Environment**
- **Purpose**: Failover if primary region fails
- **Infrastructure**: Minimal standby (1 pod, smaller database)
- **Data**: Daily backups replicated from production (cross-region replication)
- **RTO (Recovery Time Objective)**: 4 hours (time to restore full functionality)
- **RPO (Recovery Point Objective)**: 1 hour (max data loss acceptable)
- **Activation**: Manual switchover if primary region down >2 hours

### 17.3 Rollout Plan

**ROLLOUT-01: Phase 1 - Pilot (Weeks 1-4)**
- **Scope**: 10 test engineers, 1 product line (TC41x)
- **Deployment**: Staging environment promoted to production
- **Features**: Core RCA flow (submit, status, results), no RAG yet
- **Success Criteria**:
  - 50+ RCAs submitted by pilot users
  - >80% RCA accuracy (validated against expert engineers)
  - <30 min average RCA duration
  - >4.0/5.0 user satisfaction
- **Feedback**: Weekly meetings with pilot users, iterate on UI/UX

**ROLLOUT-02: Phase 2 - Expanded Pilot (Weeks 5-8)**
- **Scope**: 30 engineers, 3 product lines (TC3x, TC4x, TC5x)
- **New Features**:
  - RAG integration (10 years historical RCAs embedded)
  - Agent communication dashboard
  - PDF report generation
- **Success Criteria**:
  - 200+ RCAs submitted
  - >85% RCA accuracy
  - RAG retrieval relevance >70% (top-3 results useful)
- **Training**: 2-hour onboarding session for new users

**ROLLOUT-03: Phase 3 - General Availability (Weeks 9-12)**
- **Scope**: All 230 users (150 test engineers, 50 yield engineers, 30 FA engineers)
- **Deployment**: Full production infrastructure (HPA, multi-AZ, DR)
- **Features**: All features (real-time websockets, feedback loop, knowledge base search)
- **Marketing**: Company-wide announcement, demo videos, lunch-and-learn sessions
- **Support**: Dedicated Slack channel, weekly office hours

**ROLLOUT-04: Phase 4 - Optimization (Weeks 13-16)**
- **Focus**: Performance tuning, cost optimization, advanced features
- **Optimizations**:
  - LLM prompt optimization (reduce token usage by 20%)
  - Caching strategy (30% cache hit rate → reduce LLM costs)
  - Auto-scaling tuning (reduce idle pods)
- **Advanced Features**:
  - Self-reflection agents (agents critique their own hypotheses)
  - Dynamic tool creation (agents write custom Python functions)
  - Multi-modal data integration (shmoo plots, FA images)

### 17.4 Rollback Procedures

**ROLLBACK-01: Blue-Green Deployment Rollback**
- **Trigger**: Error rate >5% in production, p95 latency >2× baseline, critical bug discovered
- **Procedure**:
  1. **Immediate**: Switch traffic back to blue (previous stable version)
     ```bash
     kubectl patch service agent-orchestrator \
       -p '{"spec":{"selector":{"version":"blue"}}}' \
       --namespace=production
     ```
  2. **Verify**: Check metrics dashboard (error rate drops, latency normalizes)
  3. **Investigate**: Analyze green deployment logs, identify root cause
  4. **Fix**: Patch code, redeploy to staging, re-test
  5. **Re-attempt**: Deploy to green again (with fix), switch traffic if successful
- **Rollback Time**: <5 minutes (instant traffic switch)

**ROLLBACK-02: Database Migration Rollback**
- **Trigger**: Migration breaks critical queries, data corruption detected
- **Procedure**:
  1. **Stop Application**: Scale agent orchestrator to 0 replicas (prevent writes)
  2. **Rollback Migration**: Use Alembic downgrade
     ```bash
     alembic downgrade -1  # Rollback 1 migration
     ```
  3. **Verify Schema**: Run schema validation tests
  4. **Restore Application**: Scale agent orchestrator back to normal (3-15 replicas)
- **Data Loss Risk**: Minimal (migrations tested in staging, production backups every 1 hour)
- **Rollback Time**: <30 minutes

**ROLLBACK-03: Agent Prompt Rollback**
- **Trigger**: New agent prompt causes hallucinations, accuracy drops >10%
- **Procedure**:
  1. **Revert Prompt**: Database table `agents` → update `prompt_template` to previous version
     ```sql
     UPDATE agents 
     SET prompt_template = (SELECT prompt_template FROM agent_versions WHERE version='v1.2.0'), 
         version = 'v1.2.0'
     WHERE name = 'StatisticalAnalyst';
     ```
  2. **No Restart Required**: Agents read prompt from database on every RCA (dynamic, no code deploy)
  3. **Monitor**: Check accuracy metrics for next 10 RCAs
- **Rollback Time**: <2 minutes

**ROLLBACK-04: Vector Database Rollback**
- **Trigger**: New embeddings corrupt knowledge base, search results irrelevant
- **Procedure**:
  1. **Restore from Snapshot**: Qdrant daily snapshots (S3 backup)
     ```bash
     qdrant-cli restore --snapshot s3://qdrant-backups/2025-12-03.snapshot
     ```
  2. **Re-index If Needed**: If snapshot >24 hours old, re-embed recent RCAs (incremental)
  3. **Verify Search**: Run test queries, check relevance
- **Data Loss**: Max 24 hours of new RCAs (if daily backup used)
- **Rollback Time**: <1 hour (snapshot restore)

---

## 18. Monitoring & Observability

### 18.1 Metrics

**METRIC-01: Application Metrics (Prometheus)**

**Agent Orchestration Metrics**:
```python
# Custom Prometheus metrics exported by agent orchestrator
from prometheus_client import Counter, Histogram, Gauge

# RCA session metrics
rca_submissions_total = Counter('rca_submissions_total', 'Total RCA submissions', ['status', 'priority'])
rca_duration_seconds = Histogram('rca_duration_seconds', 'RCA processing duration', ['outcome'])
rca_active_sessions = Gauge('rca_active_sessions', 'Currently active RCA sessions')

# Agent-specific metrics
agent_executions_total = Counter('agent_executions_total', 'Agent executions', ['agent_name', 'status'])
agent_duration_seconds = Histogram('agent_duration_seconds', 'Agent execution time', ['agent_name'])
agent_errors_total = Counter('agent_errors_total', 'Agent errors', ['agent_name', 'error_type'])

# LLM API metrics
llm_api_calls_total = Counter('llm_api_calls_total', 'LLM API calls', ['provider', 'model'])
llm_tokens_total = Counter('llm_tokens_total', 'LLM tokens consumed', ['provider', 'type'])  # type=input/output
llm_api_latency_seconds = Histogram('llm_api_latency_seconds', 'LLM API latency', ['provider', 'model'])
llm_api_errors_total = Counter('llm_api_errors_total', 'LLM API errors', ['provider', 'error_type'])

# RAG metrics
rag_queries_total = Counter('rag_queries_total', 'RAG vector searches', ['status'])
rag_retrieval_latency_seconds = Histogram('rag_retrieval_latency_seconds', 'RAG retrieval time')
rag_relevance_score = Histogram('rag_relevance_score', 'Top-1 similarity score')

# Tool execution metrics
tool_executions_total = Counter('tool_executions_total', 'Tool executions', ['tool_name', 'status'])
tool_duration_seconds = Histogram('tool_duration_seconds', 'Tool execution time', ['tool_name'])
```

**Key Metrics Tracked**:
- **RCA Throughput**: RCAs submitted/hour, completed/hour, failed/hour
- **RCA Latency**: p50, p95, p99 end-to-end duration
- **Agent Performance**: Execution count per agent, success rate, avg duration
- **LLM Usage**: Tokens consumed/hour, API calls/hour, cost/hour, latency distribution
- **RAG Effectiveness**: Queries/hour, avg relevance score, cache hit rate
- **Error Rates**: Agent errors, LLM errors, tool errors, API errors
- **Resource Usage**: CPU, memory, disk I/O per component

**METRIC-02: Infrastructure Metrics (Kubernetes)**

**Node Metrics**:
- CPU usage per node (target: <70% average)
- Memory usage per node (target: <80% average)
- Disk I/O saturation (target: <70%)
- Network throughput (ingress/egress)

**Pod Metrics**:
- Pod count by deployment (agent-orchestrator, api-gateway, worker pods)
- Pod restarts (alert if >5 restarts in 1 hour)
- Pod readiness/liveness failures
- Container CPU throttling (indicates CPU limit too low)

**Cluster Metrics**:
- Total cluster CPU/memory capacity vs used
- Pending pods (indicates insufficient resources)
- HPA scaling events (scale up/down frequency)

**METRIC-03: Database Metrics**

**PostgreSQL (AWS RDS CloudWatch)**:
- **Connections**: Active connections, max connections (alert if >80% of max)
- **Latency**: Query latency p95 (target: <200ms)
- **IOPS**: Read/write IOPS (monitor against provisioned IOPS)
- **CPU**: Database CPU utilization (alert if >80% for 10 min)
- **Storage**: Disk space used (alert if >85% full)
- **Replication Lag**: Multi-AZ standby lag (target: <5 seconds)

**Redis**:
- **Memory**: Used memory vs max (alert if >90%)
- **Evictions**: Keys evicted due to memory pressure (should be 0 for session data)
- **Hit Rate**: Cache hit rate (target: >30% for LLM responses)
- **Latency**: Command latency p95 (target: <5ms)

**Qdrant (Vector DB)**:
- **Index Size**: Number of vectors, memory usage
- **Query Latency**: Search latency p95 (target: <1s)
- **Indexing Rate**: Vectors indexed/sec
- **Storage**: Disk usage for vector data

**METRIC-04: Business Metrics**

**User Engagement**:
- Daily active users (DAU), weekly active users (WAU)
- RCAs per user per week (avg)
- Repeat usage rate (users who submit >5 RCAs/month)

**RCA Quality**:
- User satisfaction rating (avg across all feedback, target: >4.0/5.0)
- RCA accuracy (% of RCAs validated as correct by reviewers, target: >85%)
- False positive rate (RCA identifies wrong root cause, target: <10%)
- Feedback submission rate (% of users providing feedback, target: >50%)

**Cost Metrics**:
- Cost per RCA (infrastructure + LLM, target: <$3/RCA)
- LLM cost per RCA (target: <$0.50)
- Infrastructure cost per user per month
- Cost savings vs manual RCA (6 hours @ $100/hr = $600 saved per RCA)

### 18.2 Logging

**LOG-01: Structured Logging (JSON Format)**

**Log Schema**:
```json
{
  "timestamp": "2025-12-04T15:32:10.123Z",
  "level": "INFO",  // DEBUG, INFO, WARNING, ERROR, CRITICAL
  "service": "agent-orchestrator",
  "version": "v1.3.0",
  "trace_id": "req-abc123",  // Distributed tracing ID
  "span_id": "span-xyz789",
  "session_id": "rca-session-456",
  "user_id": "user@company.com",
  "agent_name": "StatisticalAnalyst",  // Optional: if log from agent
  "message": "Completed t-test analysis",
  "duration_ms": 1250,
  "metadata": {
    "lot_id": "TC41x_LOT123",
    "wafer_id": "W05",
    "p_value": 0.003,
    "bins_compared": [5, 1]
  },
  "error": {  // Optional: only if level=ERROR
    "type": "LLMAPIError",
    "message": "OpenAI API rate limit exceeded",
    "stack_trace": "..."
  }
}
```

**LOG-02: Log Levels and Retention**

**Log Levels**:
- **DEBUG**: Agent internal state, tool execution details (only in dev/staging)
- **INFO**: RCA lifecycle events (submitted, agent started, completed), API requests
- **WARNING**: Retryable errors (LLM timeout → retry), performance degradation
- **ERROR**: Agent failures, LLM errors, tool failures, API errors
- **CRITICAL**: System failures (database down, Redis unreachable, cluster outage)

**Retention Policy**:
- **DEBUG**: 7 days (staging only, not collected in production)
- **INFO**: 30 days (compressed after 7 days)
- **WARNING**: 90 days
- **ERROR/CRITICAL**: 1 year (for compliance, incident analysis)
- **Audit Logs**: 3 years (authentication, authorization, data access)

**LOG-03: Centralized Logging (OpenSearch)**

**Architecture**:
```
Kubernetes Pods
    ↓ (stdout/stderr)
Fluentd DaemonSet (log collector)
    ↓ (forward)
OpenSearch Cluster (3 nodes)
    ↓ (visualize)
OpenSearch Dashboards (Kibana fork)
```

**Log Aggregation**:
- **Fluentd**: Collects logs from all Kubernetes pods, enriches with metadata (namespace, pod name, node)
- **OpenSearch**: Indexes logs, supports full-text search, aggregations, dashboards
- **Retention**: Auto-delete logs older than retention period (lifecycle policy)

**Search Queries** (examples):
- All errors for a specific RCA session: `session_id:"rca-session-456" AND level:"ERROR"`
- LLM API failures in last hour: `service:"agent-orchestrator" AND error.type:"LLMAPIError" AND timestamp:[now-1h TO now]`
- Slow agents (>5 min execution): `agent_name:* AND duration_ms:>300000`

**LOG-04: Log Sanitization (PII Redaction)**

**Sensitive Data Patterns**:
- Email addresses: `user@company.com` → `user@***`
- Lot IDs (may contain customer names): `CUSTOMER_LOT123` → `***_LOT123`
- IP addresses: `192.168.1.100` → `192.168.*.*`
- Session tokens/JWTs: Redacted entirely

**Implementation**:
- Fluentd filter plugin: Regex-based redaction before sending to OpenSearch
- Log library (Python `structlog`): Auto-redact fields marked as `sensitive=True`

### 18.3 Alerting

**ALERT-01: Critical Alerts (PagerDuty)**

**RCA Platform Down** (P1 - Page on-call immediately):
- **Trigger**: Health check endpoint returns 503 for >2 minutes
- **Action**: Page SRE on-call, auto-create incident ticket
- **Escalation**: If not acknowledged in 5 min → escalate to engineering manager

**Database Outage** (P1):
- **Trigger**: PostgreSQL or Redis unreachable for >1 minute
- **Action**: Page SRE + DBA on-call, attempt auto-failover to Multi-AZ standby

**High Error Rate** (P1):
- **Trigger**: API error rate >10% for >5 minutes
- **Action**: Page SRE, trigger auto-rollback to previous stable version

**ALERT-02: High-Priority Alerts (Slack Notification)**

**LLM API Errors** (P2):
- **Trigger**: LLM API error rate >5% OR 10+ errors in 5 minutes
- **Action**: Post to #rca-platform-alerts Slack channel, notify ML team

**Agent Failures** (P2):
- **Trigger**: Agent error rate >20% for any single agent (e.g., StatisticalAnalyst fails 20% of time)
- **Action**: Slack alert, disable failing agent (route around it), file bug ticket

**Performance Degradation** (P2):
- **Trigger**: RCA duration p95 >45 min (exceeds 30 min target by 50%)
- **Action**: Slack alert, investigate (check LLM latency, database slow queries, resource exhaustion)

**Resource Exhaustion** (P2):
- **Trigger**: Database connections >80% of max, Redis memory >90%, CPU >85% sustained
- **Action**: Slack alert, auto-scale (if HPA enabled), investigate root cause

**ALERT-03: Warning Alerts (Email Notification)**

**Increased Queue Depth** (P3):
- **Trigger**: RCA queue depth >50 for >30 minutes
- **Action**: Email to dev team, consider scaling up orchestrator pods

**Cache Miss Rate High** (P3):
- **Trigger**: LLM cache hit rate <10% (expected 30%)
- **Action**: Investigate cache configuration, check if cache was cleared

**User Feedback Negative** (P3):
- **Trigger**: 5+ RCAs rated <2.0/5.0 in 1 day
- **Action**: Email to product team, review recent changes

**ALERT-04: Alert Routing and Deduplication**

**Routing**:
- **P1 (Critical)**: PagerDuty → SMS + phone call to on-call SRE
- **P2 (High)**: Slack #rca-platform-alerts channel
- **P3 (Warning)**: Email to rca-dev-team@company.com

**Deduplication**:
- Same alert firing repeatedly → group into single incident (don't spam 100 alerts)
- Auto-resolve: If condition clears for 10 minutes, mark alert as resolved

**Suppression**:
- During scheduled maintenance windows → suppress alerts (manual toggle)

### 18.4 Dashboards

**DASH-01: Operational Dashboard (Grafana)**

**Overview Panel** (real-time, auto-refresh every 30 seconds):
- **RCA Status**: 
  - Active RCA sessions (gauge, target: 5-10)
  - Queue depth (gauge, alert if >50)
  - Throughput (RCAs/hour, time series graph - last 24 hours)
- **System Health**:
  - API response time p95 (line graph, target: <500ms)
  - Error rate (line graph, alert threshold 5%)
  - Pod count (stacked area chart: orchestrator, API, workers)
- **LLM Usage**:
  - API calls/hour (bar chart by provider: OpenAI, Anthropic)
  - Tokens consumed/hour (stacked area: input tokens, output tokens)
  - Cost/hour (calculated: tokens × price)

**Agent Performance Panel**:
- **Agent Execution Count** (bar chart, last 24 hours):
  - DataAgent: 450 executions
  - StatisticalAnalyst: 420 executions
  - SpatialAnalyst: 410 executions
  - CorrelationHunter: 400 executions
  - ConclusionEngine: 450 executions
  - ReportGenerator: 450 executions
- **Agent Success Rate** (horizontal bar chart, %):
  - DataAgent: 98% success
  - StatisticalAnalyst: 95% success
  - SpatialAnalyst: 92% success (lower due to complex pattern recognition)
  - ConclusionEngine: 97% success
- **Agent Latency** (box plot, p50/p95):
  - DataAgent: 90s / 180s
  - StatisticalAnalyst: 120s / 240s
  - SpatialAnalyst: 180s / 360s (slowest, heavy CV processing)
  - ConclusionEngine: 60s / 120s

**Infrastructure Panel**:
- **Kubernetes Resources**:
  - CPU usage by pod (heatmap)
  - Memory usage by pod (stacked area chart)
  - Network I/O (line graph)
- **Database**:
  - PostgreSQL connections (gauge, max 1000)
  - Query latency p95 (line graph)
  - IOPS (read/write, dual-axis line graph)
- **Redis**:
  - Memory usage (gauge, max 16GB)
  - Cache hit rate (pie chart: hits vs misses)
  - Command latency (histogram)

**DASH-02: Business Dashboard (Grafana)**

**User Engagement** (weekly view):
- **Active Users** (time series):
  - Daily active users (DAU)
  - Weekly active users (WAU)
  - New users this week
- **RCA Volume** (stacked area chart):
  - RCAs submitted per day (by product: TC3x, TC4x, TC5x)
  - RCAs completed per day
  - RCAs failed per day
- **User Satisfaction**:
  - Average rating (gauge, target: >4.0/5.0)
  - Rating distribution (bar chart: 5-star, 4-star, ..., 1-star)

**Cost Dashboard** (monthly view):
- **Total Cost** (big number panel): $12,000/month
- **Cost Breakdown** (pie chart):
  - LLM API: $7,500 (62.5%)
  - Compute: $2,000 (16.7%)
  - Database: $1,500 (12.5%)
  - Storage: $500 (4.2%)
  - Network: $500 (4.2%)
- **Cost Trend** (line graph, last 6 months):
  - Track cost growth as usage scales
  - Identify cost optimization opportunities
- **Cost per RCA** (calculated metric): $12,000 / 6,000 RCAs = $2.00/RCA (within $3 target)

**ROI Dashboard**:
- **Time Savings**: 450 RCAs/month × 5.5 hours saved/RCA = 2,475 hours/month
- **Cost Savings**: 2,475 hours × $100/hr = $247,500/month (labor cost avoided)
- **Net Savings**: $247,500 - $12,000 = $235,500/month = **$2.8M/year**
- **Payback Period**: Development cost $1.2M ÷ $235,500/month = 5 months

**DASH-03: ML/Agent Dashboard (Custom UI)**

**LLM Performance** (real-time):
- **Model Usage** (pie chart): GPT-4 Turbo 70%, Claude 3.5 Sonnet 25%, GPT-3.5 5%
- **Token Distribution** (stacked bar chart per agent):
  - Input tokens vs output tokens
  - Identify which agents consume most tokens
- **Prompt Effectiveness** (table):
  - Prompt version, success rate, avg tokens, avg cost
  - Compare A/B test results (prompt v1.3 vs v1.4)
- **Hallucination Rate** (calculated from user feedback):
  - RCAs marked "incorrect root cause" ÷ total RCAs
  - Target: <5%

**RAG Performance**:
- **Retrieval Quality** (histogram):
  - Distribution of top-1 similarity scores (0.0-1.0)
  - Target: >70% of queries have top-1 score >0.7
- **Knowledge Base Growth** (line graph):
  - Total vectors over time (target: 10M by end of year)
  - New RCAs added per week
- **Cache Hit Rate** (gauge):
  - Percentage of RAG queries served from cache
  - Target: 20%

**Agent Collaboration**:
- **Communication Graph** (network diagram):
  - Nodes: 6 agents
  - Edges: Messages exchanged between agents (thickness = message count)
  - Identify bottlenecks (e.g., ConclusionEngine receives from all agents → high fan-in)
- **Consensus Metrics**:
  - Percentage of RCAs where all agents agree on top hypothesis (target: >60%)
  - Percentage requiring tie-breaking by ConclusionEngine (target: <20%)

---

## 19. Risk Assessment

### 19.1 Technical Risks

**RISK-T-01: LLM Hallucination and Inaccurate Root Cause**
- **Description**: LLM (GPT-4/Claude) generates plausible-sounding but incorrect root cause hypotheses
- **Likelihood**: Medium (LLMs are prone to hallucination on domain-specific tasks)
- **Impact**: High (engineers act on wrong RCA → wasted debug time, delayed fixes, potential ship risk)
- **Mitigation**:
  - **Multi-Agent Consensus**: Require 3+ agents to agree before high-confidence hypothesis
  - **RAG Grounding**: All hypotheses must cite historical RCA evidence (prevent pure speculation)
  - **Human-in-the-Loop**: Reviewers (rca_reviewer role) validate RCAs before mark as "approved"
  - **Confidence Scoring**: Display confidence (0-1) for each hypothesis, flag low-confidence (<0.6) for manual review
  - **Feedback Loop**: User feedback ("incorrect") trains fine-tuned model to reduce hallucination
  - **Regular Audits**: Random sample 10% of RCAs monthly, expert engineers validate accuracy (target >85%)

**RISK-T-02: Agent Orchestration Failures (LangGraph State Machine Errors)**
- **Description**: LangGraph state machine gets stuck in infinite loop, routes to wrong agent, or crashes mid-execution
- **Likelihood**: Low (LangGraph is stable, but edge cases exist)
- **Impact**: High (RCA never completes, wasted LLM tokens, poor user experience)
- **Mitigation**:
  - **Max Iterations**: Limit state machine to 10 agent executions (prevent infinite loops)
  - **Timeout per Agent**: 10-minute timeout per agent execution (prevent hangs)
  - **Circuit Breaker**: If agent fails 3× consecutively → skip agent, continue with partial results
  - **State Persistence**: Save state machine checkpoint after each agent → restart from last checkpoint on crash
  - **Unit Tests**: Comprehensive state machine tests (all routing paths, error conditions)
  - **Monitoring**: Track state machine execution time, alert if p95 >40 min

**RISK-T-03: RAG Retrieval Irrelevance (Vector Search Returns Wrong RCAs)**
- **Description**: Vector search returns historical RCAs unrelated to current failure (embedding model poor quality, query formulation bad)
- **Likelihood**: Medium (embedding quality depends on model, query formulation tricky)
- **Impact**: Medium (agents use wrong historical context → lower quality hypotheses, but consensus mitigates)
- **Mitigation**:
  - **Embedding Model Selection**: Use domain-fine-tuned embeddings (e.g., fine-tune `all-mpnet-base-v2` on semiconductor RCAs)
  - **Hybrid Search**: Combine vector search (semantic) + keyword search (exact match) → better recall
  - **Metadata Filtering**: Filter by product family (TC3x, TC4x), package (BGA436), date range
  - **Relevance Threshold**: Only use top-K results if similarity >0.6 (discard low-quality matches)
  - **User Feedback**: "Was this historical RCA helpful?" → retrain retrieval model
  - **Regular Reindexing**: Rebuild embeddings every 3 months with improved models

**RISK-T-04: Database Performance Degradation at Scale**
- **Description**: PostgreSQL slows down as data grows (millions of RCA sessions, billions of agent messages)
- **Likelihood**: Medium (inevitable with unbounded growth)
- **Impact**: Medium (slow API responses, poor user experience, but not system failure)
- **Mitigation**:
  - **Partitioning**: Partition `rca_sessions` table by date (monthly partitions, drop old partitions after 3 years)
  - **Archival**: Move completed RCAs older than 1 year to cold storage (S3 Glacier), keep in PostgreSQL for 1 year only
  - **Read Replicas**: Route read-heavy queries (status polls, results retrieval) to read replicas
  - **Indexing**: Optimize indexes (session_id, user_id, created_at, status)
  - **Query Optimization**: Use EXPLAIN ANALYZE, optimize slow queries (avoid N+1, use JOIN instead of loops)
  - **Connection Pooling**: PgBouncer prevents connection exhaustion

**RISK-T-05: LLM API Rate Limiting and Outages**
- **Description**: OpenAI/Anthropic API rate limits exceeded (10K req/min) or service outage
- **Likelihood**: Medium (rate limits hit during peak usage, outages rare but possible)
- **Impact**: Medium (RCAs delayed, users frustrated, but queued for later processing)
- **Mitigation**:
  - **Multi-Provider Fallback**: OpenAI primary → Anthropic Claude secondary → queue if both fail
  - **Request Throttling**: Limit concurrent LLM API calls to 100 (stay below rate limit)
  - **Exponential Backoff**: Retry failed requests with backoff (1s, 2s, 4s, 8s, 16s)
  - **Caching**: 30% cache hit rate → reduce API calls by 30%
  - **Prompt Optimization**: Reduce token usage (compress prompts, use JSON mode, avoid verbose examples)
  - **Enterprise Contracts**: Negotiate higher rate limits with OpenAI (10K → 50K req/min)

**RISK-T-06: Data Privacy and PII Leakage to LLM APIs**
- **Description**: STDF files contain PII (engineer names, internal lot codes) sent to OpenAI/Anthropic (external APIs)
- **Likelihood**: Low (STDF typically doesn't have PII, but lot IDs may be sensitive)
- **Impact**: High (compliance violation, customer data exposure, regulatory fines)
- **Mitigation**:
  - **Data Sanitization**: Redact PII before sending to LLM (engineer names → "Engineer A", lot IDs → hashed)
  - **Azure OpenAI / AWS Bedrock**: Use private LLM deployments (data never leaves company tenant)
  - **Data Processing Addendum (DPA)**: Sign DPA with OpenAI/Anthropic (GDPR-compliant, data deletion guarantees)
  - **Audit Logging**: Log all data sent to LLM APIs (for compliance audits)
  - **User Consent**: Terms of service disclose LLM usage, users consent to data processing
  - **On-Prem LLM (Future)**: Deploy open-source LLM (Llama 3, Mistral) on-prem if compliance requires

### 19.2 Business Risks

**RISK-B-01: Low User Adoption (Engineers Don't Trust AI RCA)**
- **Description**: Engineers skeptical of AI, prefer manual RCA, platform usage <50%
- **Likelihood**: Medium (common with AI tools, trust takes time to build)
- **Impact**: High (ROI not realized, project deemed failure, $1.2M investment wasted)
- **Mitigation**:
  - **Pilot Program**: Start with 10 early adopters (trusted engineers), gather testimonials
  - **Transparency**: Show agent reasoning (not black box), explain how hypotheses derived
  - **Human-in-the-Loop**: Agents augment engineers (not replace), final decision always with human
  - **Training**: 2-hour onboarding sessions, office hours, demo videos
  - **Incentives**: Recognize top users (monthly leaderboard), tie to performance reviews (time saved metric)
  - **Iterative Improvement**: Collect feedback weekly, ship improvements biweekly, show responsiveness

**RISK-B-02: High Operational Costs Exceed Budget**
- **Description**: LLM API costs exceed $7.5K/month budget (due to high token usage, inefficient prompts)
- **Likelihood**: Medium (LLM costs hard to predict, usage may spike)
- **Impact**: Medium (project profitability reduced, but still net positive ROI)
- **Mitigation**:
  - **Cost Monitoring**: Real-time Grafana dashboard, alert if cost >$10K/month
  - **Prompt Optimization**: Compress prompts (remove examples, use system messages), reduce output tokens
  - **Model Selection**: Use GPT-3.5 for simple tasks ($0.002/1K vs GPT-4 $0.01/1K → 5× cheaper)
  - **Caching**: 30% cache hit rate → $7.5K × 0.7 = $5.25K/month (30% savings)
  - **Rate Limiting**: Cap LLM budget at $10K/month (throttle requests if exceeded)
  - **Self-Hosted LLM**: If costs grow beyond $15K/month, consider self-hosting Llama 3 70B (one-time GPU cost)

**RISK-B-03: Resistance from Management (ROI Unclear)**
- **Description**: Management questions value, asks to cut funding, reallocate team
- **Likelihood**: Low (strong business case: $2.8M/year savings, <5 month payback)
- **Impact**: High (project canceled, team disbanded)
- **Mitigation**:
  - **Clear Metrics**: Track time saved, cost savings, user satisfaction (monthly exec report)
  - **Case Studies**: Document 10 high-impact RCAs where AI found root cause in <30 min (manual would take 8 hours)
  - **Executive Demos**: Quarterly demos to VPs, show before/after (manual RCA report vs AI-generated)
  - **Benchmarking**: Compare to competitors (Intel, NVIDIA use AI for test analytics, we need parity)
  - **Quick Wins**: Deliver pilot in 4 weeks (show early results, build momentum)

**RISK-B-04: Regulatory Compliance Challenges (AI Governance)**
- **Description**: New AI regulations (EU AI Act, US executive orders) require transparency, explainability, auditability
- **Likelihood**: Medium (regulations evolving, semiconductor industry regulated)
- **Impact**: Medium (compliance work, may need to redesign features)
- **Mitigation**:
  - **Explainability by Design**: All hypotheses cite evidence (STDF data, historical RCAs, statistical tests)
  - **Audit Trail**: Log all LLM prompts, responses, agent decisions (immutable logs, 3-year retention)
  - **Human Oversight**: Reviewer role approves critical RCAs (high-risk failures, customer returns)
  - **Model Cards**: Document LLM model (version, training data, limitations, bias mitigation)
  - **Legal Review**: Engage legal team early, review compliance with EU AI Act, GDPR, SOC 2

### 19.3 Mitigation Strategies

**MIT-01: Phased Rollout with Kill Switch**
- **Strategy**: Roll out in 4 phases (pilot → expanded → GA → optimization), each with go/no-go decision gate
- **Kill Switch**: If accuracy <70% or user satisfaction <3.0/5.0 → pause rollout, fix issues before next phase
- **Rollback Plan**: Blue-green deployment allows instant rollback to manual RCA process if catastrophic failure

**MIT-02: Continuous Monitoring and Alerting**
- **Strategy**: Real-time dashboards (Grafana), alerts for anomalies (error rate, latency, cost)
- **On-Call Rotation**: 24/7 SRE on-call for critical alerts (PagerDuty)
- **Weekly Reviews**: Dev team reviews metrics (accuracy, user feedback, cost), adjusts strategy

**MIT-03: Human-in-the-Loop Validation**
- **Strategy**: `rca_reviewer` role manually validates 20% of RCAs (random sample)
- **Escalation**: Low-confidence RCAs (<0.6) automatically routed to reviewers
- **Feedback Loop**: Reviewers mark incorrect hypotheses → fine-tune LLM, improve prompts

**MIT-04: Redundancy and Failover**
- **Strategy**: Multi-AZ database (auto-failover <60s), multi-provider LLM (OpenAI → Claude), distributed vector DB (3-node Qdrant)
- **Disaster Recovery**: Cross-region backups (RTO 4 hours, RPO 1 hour), DR environment standby

**MIT-05: Regular Security Audits**
- **Strategy**: Quarterly internal security reviews, annual external pen test
- **Vulnerability Scanning**: Automated SAST/DAST in CI/CD pipeline (Snyk, SonarQube)
- **Compliance**: SOC 2 Type II audit (planned Year 2), GDPR compliance validation

---

## 20. Timeline & Milestones

### 20.1 Phase Breakdown

**Overall Timeline**: 16 weeks (4 months)  
**Team Size**: 6-8 FTE (2 backend engineers, 1 ML engineer, 1 DevOps, 1 QA, 1 product manager, 1 UI/UX designer, 1 tech lead)  
**Budget**: $1.2M (labor $900K, infrastructure $200K, LLM API $100K)

---

**Phase 1: Requirements & Design (Weeks 1-2)**

**Objectives**:
- Finalize PRD (this document)
- Design multi-agent architecture (LangGraph state machine, CrewAI team structure)
- Define agent personas and tools
- Set up project infrastructure (GitHub repo, CI/CD, dev environments)

**Deliverables**:
- ✅ PRD approved by stakeholders (product, engineering, yield team)
- ✅ Architecture diagrams (system architecture, agent communication flow, data model)
- ✅ Agent specifications (6 agents: roles, inputs, outputs, tools)
- ✅ Technical stack finalized (LangGraph 0.2+, CrewAI 0.51+, GPT-4 Turbo, Qdrant)

**Team**:
- Product Manager: PRD refinement, stakeholder alignment
- Tech Lead: Architecture design, technology selection
- ML Engineer: Agent design, LLM selection
- Backend Engineer: Database schema, API design

**Milestones**:
- **M1 (Week 1)**: PRD v1.0 complete, stakeholder review meeting
- **M2 (Week 2)**: Architecture design complete, tech stack approved

---

**Phase 2: Core Agent Development (Weeks 3-6)**

**Objectives**:
- Implement 6 core agents (Data Analyst, Statistical Analyst, Spatial Pattern Detector, Correlation Hunter, ConclusionEngine, Report Generator)
- Develop agent tools (STDF parser, wafer map generator, statistical tests, PDF report)
- Build LangGraph state machine (agent orchestration, conditional routing)
- Create CrewAI hierarchical teams (manager delegates to specialist agents)

**Deliverables**:
- ✅ 6 agents implemented (Python, LangChain StructuredTool)
- ✅ Tool library (STDF parser, wafer map CV, t-test/correlation, Pareto charts, PDF generation)
- ✅ LangGraph state machine (START → DataAgent → ParallelAnalysis → ConclusionEngine → END)
- ✅ CrewAI team orchestration (Orchestrator manages 5 specialist agents)
- ✅ Unit tests (>85% coverage for agent logic, tools)

**Team**:
- ML Engineer (lead): Agent implementation, LLM prompts, tool design
- Backend Engineer: Tool library (STDF parser, statistical functions)
- QA Engineer: Unit test development, test fixtures

**Milestones**:
- **M3 (Week 4)**: Data Analyst + Statistical Analyst complete, unit tested
- **M4 (Week 5)**: Spatial + Correlation agents complete, LangGraph routing implemented
- **M5 (Week 6)**: ConclusionEngine + Report Generator complete, end-to-end agent flow working

---

**Phase 3: RAG Integration & Knowledge Base (Weeks 7-8)**

**Objectives**:
- Set up vector database (Qdrant cluster, 3 nodes)
- Embed 10 years of historical RCA reports (50K reports → 10M vectors)
- Implement RAG retrieval (query formulation, hybrid search, metadata filtering)
- Integrate RAG into agents (agents query knowledge base for similar failures)

**Deliverables**:
- ✅ Qdrant cluster deployed (dev + staging environments)
- ✅ Embedding pipeline (extract text from RCA PDFs, chunk, embed with `all-mpnet-base-v2`)
- ✅ 10M vectors indexed (50K reports × 200 chunks/report avg)
- ✅ RAG API (`/api/v1/rag/search` endpoint)
- ✅ Agents use RAG (ConclusionEngine queries for historical context, cites sources)

**Team**:
- ML Engineer (lead): Embedding model selection, chunking strategy, RAG retrieval
- Backend Engineer: Qdrant deployment, API integration
- DevOps: Kubernetes deployment, storage provisioning (150GB SSD)

**Milestones**:
- **M6 (Week 7)**: Qdrant deployed, 1M vectors indexed (test dataset)
- **M7 (Week 8)**: Full 10M vectors indexed, RAG integrated into ConclusionEngine agent

---

**Phase 4: API & Database Development (Weeks 9-10)**

**Objectives**:
- Design PostgreSQL schema (9 tables: rca_sessions, agent_messages, hypotheses, etc.)
- Implement REST API (FastAPI, 8 endpoints)
- Build authentication/authorization (OAuth2 SSO, JWT, RBAC)
- Develop caching layer (Redis for LLM responses, API results)

**Deliverables**:
- ✅ PostgreSQL database (9 tables, migrations with Alembic)
- ✅ FastAPI REST API (8 endpoints: submit, status, results, feedback, RAG search, etc.)
- ✅ OAuth2/JWT authentication (Azure AD integration, 4 roles)
- ✅ Redis caching (LLM response cache 7-day TTL, API cache 5-second TTL)
- ✅ API documentation (OpenAPI/Swagger auto-generated)

**Team**:
- Backend Engineer (lead): Database schema, API implementation, authentication
- DevOps: PostgreSQL RDS setup, Redis deployment
- Security: OAuth2 configuration, RBAC policies

**Milestones**:
- **M8 (Week 9)**: Database schema complete, API skeleton implemented
- **M9 (Week 10)**: Authentication working, all 8 endpoints functional, integration tests passing

---

**Phase 5: UI Development & Integration (Weeks 11-12)**

**Objectives**:
- Design UI mockups (Figma: RCA submission form, dashboard, status page, results page)
- Implement React frontend (6 UI components)
- Integrate WebSocket for real-time status updates
- Implement accessibility (WCAG 2.1 AA compliance)

**Deliverables**:
- ✅ React frontend (TypeScript, Material-UI components)
- ✅ 6 UI screens (submission, dashboard, status with real-time updates, results, agent communication graph, RAG search)
- ✅ WebSocket integration (backend pushes updates every 5s, client displays progress bar)
- ✅ Accessibility features (keyboard navigation, ARIA labels, 4.5:1 contrast)
- ✅ Responsive design (mobile, tablet, desktop)

**Team**:
- UI/UX Designer (lead): Mockups, user flows, design system
- Frontend Engineer: React implementation, WebSocket client, accessibility
- Backend Engineer: WebSocket server (FastAPI WebSocket endpoint)

**Milestones**:
- **M10 (Week 11)**: UI mockups approved, React skeleton implemented
- **M11 (Week 12)**: All 6 screens functional, WebSocket real-time updates working

---

**Phase 6: Testing & QA (Weeks 13-14)**

**Objectives**:
- End-to-end testing (submit RCA, wait for completion, validate results)
- Performance testing (Locust load tests: 100 concurrent users, 500 RCAs/day)
- Security testing (pen test, OWASP Top 10, authentication bypass attempts)
- User acceptance testing (10 pilot engineers test in staging)

**Deliverables**:
- ✅ E2E test suite (pytest, 20 scenarios covering happy path + edge cases)
- ✅ Load test results (system handles 100 concurrent users, <500ms API latency p95)
- ✅ Security audit report (no critical/high vulnerabilities, all medium fixed)
- ✅ UAT feedback (pilot users complete 50 RCAs, avg rating >4.0/5.0)

**Team**:
- QA Engineer (lead): E2E tests, load tests, UAT coordination
- Security Engineer: Security testing, vulnerability remediation
- ML Engineer: RCA accuracy validation (compare AI vs manual RCA)

**Milestones**:
- **M12 (Week 13)**: E2E tests passing, load tests show <500ms latency
- **M13 (Week 14)**: Security audit complete, UAT feedback collected

---

**Phase 7: Pilot Deployment (Week 15)**

**Objectives**:
- Deploy to production (blue-green deployment)
- Onboard 10 pilot users (test engineers from TC41x team)
- Monitor system (Grafana dashboards, alerting via Slack)
- Collect feedback (weekly meetings, Slack channel)

**Deliverables**:
- ✅ Production deployment (Kubernetes cluster, PostgreSQL RDS, Qdrant, Redis)
- ✅ 10 pilot users onboarded (2-hour training session, demo videos)
- ✅ Monitoring dashboards (Grafana: operational, business, ML metrics)
- ✅ 50+ RCAs completed by pilot users in Week 15
- ✅ Feedback report (user satisfaction, bug list, feature requests)

**Team**:
- DevOps (lead): Production deployment, monitoring setup
- Product Manager: Pilot user onboarding, training, feedback collection
- Full team: On-call rotation (respond to bugs, performance issues)

**Milestones**:
- **M14 (Week 15)**: Production live, 10 pilot users active, 50 RCAs completed

---

**Phase 8: Iteration & General Availability (Week 16)**

**Objectives**:
- Fix bugs identified in pilot (high-priority only)
- Optimize performance (LLM prompt compression, database query tuning)
- Expand to 30 users (expanded pilot: TC3x, TC4x, TC5x teams)
- Plan for general availability (all 230 users in Month 5)

**Deliverables**:
- ✅ Bug fixes deployed (10 high-priority bugs from pilot feedback)
- ✅ Performance improvements (token usage reduced 15%, API latency improved 10%)
- ✅ 30 users onboarded (expanded pilot)
- ✅ GA rollout plan (Weeks 17-20: 230 users, marketing, training)

**Team**:
- Full team: Bug fixes, performance optimization
- Product Manager: Expanded pilot onboarding, GA planning

**Milestones**:
- **M15 (Week 16)**: Pilot deemed successful (>85% accuracy, >4.0/5.0 satisfaction), expanded to 30 users
- **M16 (Week 16)**: GA rollout plan approved by exec team

---

### 20.2 Key Milestones

**Summary of 16 Milestones**:

| Milestone | Week | Description | Success Criteria |
|-----------|------|-------------|------------------|
| M1 | 1 | PRD Complete | PRD approved by stakeholders |
| M2 | 2 | Architecture Design | Architecture diagrams approved, tech stack finalized |
| M3 | 4 | Core Agents (Phase 1) | Data + Statistical agents implemented, unit tested |
| M4 | 5 | Agent Orchestration | LangGraph routing works, parallel agent execution |
| M5 | 6 | All Agents Complete | 6 agents working end-to-end, >85% test coverage |
| M6 | 7 | Vector DB Setup | Qdrant deployed, 1M test vectors indexed |
| M7 | 8 | RAG Integration | 10M vectors indexed, RAG retrieval <1s p95 |
| M8 | 9 | Database & API Skeleton | PostgreSQL schema deployed, 8 API endpoints stubbed |
| M9 | 10 | API Functional | Authentication works, all endpoints return data |
| M10 | 11 | UI Mockups | Figma designs approved by UX team |
| M11 | 12 | UI Functional | React frontend deployed, WebSocket updates working |
| M12 | 13 | Testing Complete | E2E tests pass, load tests show <500ms latency |
| M13 | 14 | Security Audit | No critical vulnerabilities, UAT feedback positive |
| M14 | 15 | Pilot Launch | 10 users onboarded, 50 RCAs completed, monitoring live |
| M15 | 16 | Pilot Success | >85% accuracy, >4.0/5.0 satisfaction, bugs fixed |
| M16 | 16 | GA Plan | Exec approval for 230-user rollout in Month 5 |

**Critical Path**:
- **Weeks 1-2**: Requirements/Design (blocks all dev work)
- **Weeks 3-6**: Core Agent Development (blocks RAG, API, UI)
- **Weeks 7-8**: RAG Integration (blocks high-accuracy RCAs)
- **Weeks 9-12**: API + UI (blocks end-user testing)
- **Weeks 13-14**: Testing (blocks pilot launch)
- **Week 15**: Pilot (validates product-market fit)
- **Week 16**: Iteration (prepares for GA)

**Dependencies**:
- RAG depends on Core Agents (agents must exist before RAG integration)
- UI depends on API (frontend needs backend endpoints)
- Pilot depends on Testing (must pass QA before production)

---

## 21. Success Metrics & KPIs

### 21.1 Measurable Targets

**PRIMARY SUCCESS METRICS**

**METRIC-01: RCA Accuracy**
- **Definition**: Percentage of AI-generated root cause hypotheses validated as correct by expert engineers (rca_reviewer role)
- **Target**: **>85% accuracy** (stretch goal: 90%)
- **Measurement Method**:
  - Random sample 20% of completed RCAs monthly (100 RCAs/month if 500 total)
  - Expert reviewers independently validate top-ranked hypothesis (mark as "correct", "partially correct", "incorrect")
  - Accuracy = (correct + 0.5 × partially correct) / total reviewed
- **Baseline**: Manual RCA accuracy ~95% (expert engineers, 6-8 hours)
- **Acceptance Criteria**: 
  - Pilot (Month 1): >75% accuracy acceptable (early learning phase)
  - Months 2-3: >80% accuracy
  - Month 4+: Sustained >85% accuracy
- **Reporting**: Monthly accuracy report, broken down by product family (TC3x, TC4x), failure type (bin5, bin7), agent performance

**METRIC-02: Time Reduction (RCA Duration)**
- **Definition**: Time from RCA submission to completed report delivery
- **Target**: **<30 minutes p95** (median <20 minutes)
- **Baseline**: Manual RCA takes 4-8 hours (median 6 hours)
- **Time Savings**: 6 hours - 0.5 hours (30 min) = **5.5 hours saved per RCA**
- **Measurement**: Automatically tracked in database (`rca_sessions.created_at` vs `rca_sessions.completed_at`)
- **Breakdown**:
  - Data ingestion: <2 min
  - Parallel agent analysis: <15 min (5 agents run concurrently)
  - RAG retrieval: <3 min
  - Synthesis + consensus: <5 min
  - Report generation: <5 min
- **Acceptance Criteria**:
  - 50% of RCAs complete in <15 min (simple cases, known patterns)
  - 95% of RCAs complete in <30 min
  - 99% of RCAs complete in <45 min (complex, novel failures)

**METRIC-03: User Adoption Rate**
- **Definition**: Percentage of target users actively using platform (submit ≥1 RCA/month)
- **Target**: **>70% adoption** within 6 months of GA
- **Baseline**: 0% (new platform)
- **Measurement**:
  - DAU (daily active users): Users who submit or view RCA results each day
  - MAU (monthly active users): Users who submit ≥1 RCA/month
  - Adoption rate = MAU / total eligible users (230 engineers)
- **Milestones**:
  - Pilot (10 users, Week 15): 100% adoption (all 10 users submit ≥5 RCAs in pilot week)
  - Expanded pilot (30 users, Week 16-20): >80% adoption
  - GA (230 users, Months 5-6): >70% adoption by Month 6
- **Churn Prevention**: Track users who stop using (0 RCAs for 2 consecutive months), conduct interviews to identify barriers

**METRIC-04: User Satisfaction (CSAT)**
- **Definition**: Average user rating of RCA quality (1-5 star scale)
- **Target**: **>4.0/5.0 average** (stretch goal: 4.3/5.0)
- **Baseline**: Manual RCA satisfaction ~4.5/5.0 (high bar, expert engineers)
- **Measurement**:
  - Post-RCA feedback form (appears after viewing results, optional)
  - Questions:
    - "How accurate was the top hypothesis?" (1-5 stars)
    - "How useful were the supporting insights (wafer maps, correlations)?" (1-5 stars)
    - "Would you use this tool again?" (Yes/No)
    - "Any suggestions for improvement?" (free text)
- **Acceptance Criteria**:
  - Pilot: >3.5/5.0 (early version, bugs expected)
  - Month 2-3: >3.8/5.0
  - Month 4+: Sustained >4.0/5.0
- **Response Rate**: Target >50% of users provide feedback (incentivize with monthly raffle)

**METRIC-05: Cost per RCA**
- **Definition**: Total infrastructure + LLM costs divided by RCAs completed
- **Target**: **<$3.00 per RCA** (stretch goal: <$2.50)
- **Calculation**:
  - Total monthly cost: $12,000 (infrastructure $4,500 + LLM API $7,500)
  - RCAs per month: 6,000 (500/day × 30 days × 40% utilization = 6,000)
  - Cost per RCA: $12,000 / 6,000 = **$2.00/RCA** (well below $3 target)
- **Components**:
  - LLM cost: $0.50/RCA (50K tokens @ $0.01/1K tokens)
  - Infrastructure: $1.50/RCA (compute, database, storage, network)
- **Optimization Opportunities**:
  - Increase caching (30% → 50% hit rate) → reduce LLM cost by 20%
  - Use GPT-3.5 for simple tasks → reduce LLM cost by 30%
  - Scale infrastructure efficiently (HPA) → reduce idle compute cost

**METRIC-06: ROI (Return on Investment)**
- **Definition**: Net savings from AI RCA vs manual RCA cost
- **Calculation**:
  - **Manual RCA Cost**: 6 hours × $100/hr (test engineer hourly rate) = **$600 per RCA**
  - **AI RCA Cost**: $2.00 (infrastructure + LLM, from METRIC-05)
  - **Savings per RCA**: $600 - $2.00 = **$598 saved**
  - **Monthly Savings**: 500 RCAs/month × $598 = **$299,000/month**
  - **Annual Savings**: $299,000 × 12 = **$3.6M/year** (exceeds $4M goal from section 3.2)
- **Investment**:
  - Development: $1.2M (16 weeks, 6-8 FTE)
  - Ongoing operations: $12K/month = $144K/year
  - Total first-year cost: $1.2M + $144K = $1.344M
- **Net ROI Year 1**: ($3.6M - $1.344M) / $1.344M = **168% ROI**
- **Payback Period**: $1.2M / $299K/month = **4 months** (earlier than 5-month estimate in section 18.4)

**METRIC-07: Error Rate (False Positives)**
- **Definition**: Percentage of RCAs where top hypothesis is incorrect (validated by reviewers)
- **Target**: **<15% error rate** (inverse of 85% accuracy target)
- **Measurement**: Same validation process as METRIC-01 (expert reviewer marks "incorrect")
- **Breakdown by Error Type**:
  - LLM hallucination (invents root cause not supported by data): <5%
  - Agent tool failure (wafer map misclassified, statistical test error): <5%
  - Data quality issues (corrupted STDF, insufficient data): <5%
- **Actionable Insights**:
  - High hallucination rate → improve prompts, add RAG citations
  - High tool failure → retrain CV models, fix statistical bugs
  - High data quality issues → improve STDF validation, user education

**SECONDARY METRICS (OPERATIONAL KPIs)**

**METRIC-08: System Uptime**
- **Target**: **99.5% uptime** (43.8 hours downtime/year, ~3.6 hours/month)
- **Measurement**: API health check endpoint monitored every 1 minute (Prometheus)
- **Excludes**: Scheduled maintenance windows (announced 48 hours ahead)
- **Reporting**: Monthly uptime report, root cause for all incidents >15 min downtime

**METRIC-09: API Latency**
- **Target**: **p95 <500ms** for all API endpoints (submit, status, results)
- **Measurement**: Prometheus histogram `http_request_duration_seconds`
- **SLO (Service Level Objective)**:
  - p50 <200ms
  - p95 <500ms
  - p99 <1000ms

**METRIC-10: LLM Token Efficiency**
- **Target**: **<50,000 tokens per RCA** (input + output combined)
- **Baseline**: Initial prompts may use 70K tokens (verbose, many examples)
- **Optimization Goal**: Reduce to 40K tokens through prompt compression (20% reduction)
- **Measurement**: Track `llm_tokens_total` metric per RCA session
- **Impact**: 10K token reduction × $0.01/1K = $0.10 saved per RCA (20% LLM cost reduction)

**METRIC-11: Agent Collaboration Efficiency**
- **Definition**: Percentage of RCAs where agents reach consensus without tie-breaking
- **Target**: **>60% consensus** (agents agree on top hypothesis without ConclusionEngine override)
- **Measurement**: Track `agent_messages` where `message_type='consensus'` vs `message_type='tie_break'`
- **High Collaboration**: Indicates agents have complementary skills, reduce redundancy

**METRIC-12: Knowledge Base Coverage**
- **Definition**: Percentage of RCAs where RAG retrieval finds relevant historical context (top-1 similarity >0.7)
- **Target**: **>70% coverage** (7 out of 10 RCAs have useful historical match)
- **Measurement**: Track `rag_relevance_score` histogram, count scores >0.7
- **Growth**: As knowledge base grows (50K → 100K RCAs over 2 years), coverage should increase to >85%

**METRIC-13: Feedback Loop Engagement**
- **Definition**: Percentage of completed RCAs where user provides feedback (rating + comments)
- **Target**: **>50% feedback rate**
- **Measurement**: Count RCAs with feedback submission vs total completed RCAs
- **Incentive**: Monthly raffle (random draw from users who provide feedback, prize: $100 gift card)

**TERTIARY METRICS (ADVANCED ANALYTICS)**

**METRIC-14: Multi-Agent Synergy Score**
- **Definition**: Improvement in accuracy when using 6 agents vs single agent (Data Analyst only)
- **Target**: **>15% accuracy improvement** (multi-agent 85% vs single-agent 70%)
- **Measurement**: A/B test (10% of RCAs use single Data Analyst, 90% use full multi-agent)
- **Validates**: Multi-agent architecture adds value beyond single LLM call

**METRIC-15: RAG Contribution to Accuracy**
- **Definition**: Accuracy improvement when RAG enabled vs disabled
- **Target**: **>10% accuracy improvement** (RAG enabled 85% vs disabled 75%)
- **Measurement**: A/B test (5% of RCAs have RAG disabled, 95% RAG enabled)
- **Validates**: Historical knowledge base provides value (not just LLM reasoning)

**METRIC-16: Time-to-Value (Onboarding)**
- **Definition**: Days from user account creation to first successful RCA submission
- **Target**: **<3 days** (ideally same day as onboarding session)
- **Measurement**: Track `users.created_at` vs first `rca_sessions.created_at` per user
- **Bottlenecks**: Identify if training, UI complexity, or access issues delay adoption

**METRIC-17: Repeat Usage Rate**
- **Definition**: Percentage of users who submit ≥5 RCAs/month (power users)
- **Target**: **>30% power users** (70 out of 230 users)
- **Measurement**: Count users with `COUNT(rca_sessions) >= 5 WHERE month = current_month`
- **Insight**: Power users are champions, can provide detailed feedback and advocate for platform

**METRIC-18: Agent Error Diversity**
- **Definition**: Distribution of errors across 6 agents (detect if one agent is bottleneck)
- **Target**: **No single agent accounts for >40% of errors** (balanced failure modes)
- **Measurement**: Count `agent_errors_total` by `agent_name`, calculate percentage
- **Actionable**: If StatisticalAnalyst has 60% of errors → prioritize fixing that agent

**DASHBOARD VISUALIZATION**

**Executive Dashboard (Monthly Review)**:
- **Accuracy Trend**: Line graph (last 6 months, target line at 85%)
- **Time Savings**: Big number panel (total hours saved this month: 2,475 hours)
- **ROI**: Big number panel (monthly savings: $299K, annual projection: $3.6M)
- **User Adoption**: Gauge (70% of 230 users = 161 active users)
- **CSAT**: Star rating visual (4.2/5.0 average, 850 feedback submissions)

**Operational Dashboard (Real-Time)**:
- **Active RCAs**: Gauge (currently processing: 8 sessions)
- **Queue Depth**: Gauge (waiting: 3 RCAs, alert threshold: 50)
- **API Latency**: Line graph (last 24 hours, p95 <500ms target)
- **Error Rate**: Line graph (last 7 days, target <15%)
- **Uptime**: Big number (99.7% this month, 12 hours downtime/year pace)

**REPORTING CADENCE**

- **Daily**: Automated Slack message to #rca-platform (RCAs completed today, avg duration, error count)
- **Weekly**: Email to dev team (accuracy, user feedback summary, top 3 bugs)
- **Monthly**: Executive report (ROI, user adoption, accuracy trend, cost analysis)
- **Quarterly**: Business review with VPs (strategic metrics, roadmap, budget)

---

## 22. Appendices & Glossary

### 22.1 Technical Background

**Multi-Agent AI Systems**

Multi-agent systems consist of multiple autonomous agents that collaborate to solve complex problems. In the context of RCA:
- **Agent**: An AI entity with a specific role (e.g., Statistical Analyst, Spatial Pattern Detector)
- **Orchestration**: Coordination mechanism that routes tasks between agents (LangGraph state machine)
- **Shared Memory**: Blackboard pattern where agents write findings for others to read (PostgreSQL `agent_messages` table)
- **Consensus**: Process where agents vote on hypotheses, ConclusionEngine resolves ties
- **Emergent Behavior**: System intelligence exceeds sum of individual agents (collaboration improves accuracy)

**LangGraph (Agent Orchestration Framework)**

LangGraph is a framework for building stateful, multi-agent workflows:
- **State Machine**: Directed graph where nodes are agents, edges are transitions
- **Conditional Routing**: Routes to different agents based on state (e.g., if edge_effect detected → route to FA specialist)
- **Cycles**: Allows iterative refinement (agent can be called multiple times in one workflow)
- **Persistence**: State saved to database, workflow resumes after crash
- **Human-in-the-Loop**: Workflow can pause for human input (e.g., user approves hypothesis before continuing)

**CrewAI (Hierarchical Agent Teams)**

CrewAI extends LangChain with team structures:
- **Manager Agent**: Orchestrator that delegates tasks to specialist agents
- **Worker Agents**: 5 specialist agents (Data Analyst, Statistical Analyst, Spatial, Correlation, ConclusionEngine)
- **Sequential Tasks**: Manager assigns tasks in order (data ingestion → analysis → synthesis)
- **Parallel Execution**: Workers run concurrently (3 agents analyze different aspects simultaneously)
- **Context Sharing**: Workers share findings via shared memory, Manager aggregates results

**Retrieval-Augmented Generation (RAG)**

RAG combines retrieval (search) with generation (LLM):
1. **Query Formulation**: User input → query (e.g., "TC41x BGA436 edge effect bin5")
2. **Retrieval**: Query embedding → vector search → top-K similar historical RCAs (K=5)
3. **Augmentation**: Retrieved RCAs + current data → augmented prompt for LLM
4. **Generation**: LLM generates hypothesis grounded in historical evidence (cites RCA IDs)
5. **Benefit**: Reduces hallucination, improves accuracy (historical patterns guide reasoning)

**Vector Databases (Qdrant)**

Vector databases store and search high-dimensional embeddings:
- **Embedding**: Text (RCA report) → 768-dimensional vector (via embedding model like `all-mpnet-base-v2`)
- **Index**: HNSW (Hierarchical Navigable Small World) index for fast approximate nearest neighbor search
- **Similarity**: Cosine similarity measures closeness (1.0 = identical, 0.0 = orthogonal)
- **Metadata Filtering**: Filter by product, date, failure type before similarity search (hybrid search)
- **Scalability**: Distributed clusters (3 nodes) handle 10M+ vectors with <1s query latency

**LLM Prompting Techniques**

- **System Message**: Sets agent persona, role, constraints (e.g., "You are a statistical analyst expert in semiconductor testing")
- **Few-Shot Learning**: Provide 2-3 examples in prompt (input → expected output)
- **Chain-of-Thought**: Ask LLM to explain reasoning step-by-step (improves accuracy on complex tasks)
- **JSON Mode**: Force LLM to output valid JSON (structured data for parsing)
- **Temperature**: Controls randomness (0.0 = deterministic, 1.0 = creative; use 0.3 for RCA)
- **Token Budget**: Limit max tokens to control cost (e.g., max_tokens=2000 for hypothesis generation)

### 22.2 References

**Industry Standards**

1. **STDF (Standard Test Data Format)**: JEDEC specification for semiconductor test data
   - Version: STDF V4-2007
   - URL: https://www.jedec.org/standards-documents/docs/jesd22-b116b
   - Binary format for storing test results (MIR, WIR, PTR, FTR records)

2. **ATDF (ASCII Test Data Format)**: Human-readable alternative to STDF
   - Used for debugging, manual inspection of test data

3. **SEMI Standards**: Semiconductor Equipment and Materials International
   - E5: Diagnostic Data Standard
   - E30: Generic Model for Communications and Control (GEM)

**AI/ML Frameworks**

4. **LangChain**: Framework for building LLM applications
   - Documentation: https://python.langchain.com/
   - Version used: 0.2+
   - Key modules: StructuredTool, LLMChain, PromptTemplate

5. **LangGraph**: State machine framework for multi-agent workflows
   - Documentation: https://langchain-ai.github.io/langgraph/
   - Version used: 0.2+
   - Tutorials: Multi-agent examples, supervisor pattern

6. **CrewAI**: Hierarchical agent orchestration
   - Documentation: https://docs.crewai.com/
   - Version used: 0.51+
   - Features: Manager-worker delegation, sequential/parallel tasks

7. **OpenAI API**: GPT-4 Turbo, GPT-3.5 Turbo
   - Documentation: https://platform.openai.com/docs/
   - Pricing: https://openai.com/pricing
   - Enterprise: https://openai.com/enterprise

8. **Anthropic Claude**: Claude 3.5 Sonnet
   - Documentation: https://docs.anthropic.com/
   - Pricing: https://www.anthropic.com/pricing
   - Safety: Constitutional AI (CAI)

**Vector Databases**

9. **Qdrant**: Open-source vector search engine
   - Documentation: https://qdrant.tech/documentation/
   - Version used: 1.9+
   - Features: HNSW index, metadata filtering, distributed clustering

10. **ChromaDB**: Alternative vector DB (used in dev/testing)
    - Documentation: https://docs.trychroma.com/
    - Version used: 0.4+
    - Lightweight, embedded mode for local dev

**Embedding Models**

11. **Sentence Transformers**: Pre-trained embedding models
    - Documentation: https://www.sbert.net/
    - Model used: `all-mpnet-base-v2` (768-dim, fine-tuned on 1B sentence pairs)
    - Hugging Face: https://huggingface.co/sentence-transformers/all-mpnet-base-v2

**DevOps & Infrastructure**

12. **Kubernetes**: Container orchestration
    - Documentation: https://kubernetes.io/docs/
    - Version: 1.30+
    - Features: HPA, StatefulSets, Secrets, ConfigMaps

13. **Prometheus**: Metrics collection and alerting
    - Documentation: https://prometheus.io/docs/
    - Client: prometheus-client (Python)
    - Query language: PromQL

14. **Grafana**: Metrics visualization dashboards
    - Documentation: https://grafana.com/docs/
    - Dashboards: Pre-built Kubernetes, PostgreSQL, Redis dashboards

15. **OpenSearch**: Log aggregation and search (Elasticsearch fork)
    - Documentation: https://opensearch.org/docs/
    - Version: 2.11+
    - Dashboards: OpenSearch Dashboards (Kibana fork)

**Research Papers**

16. **"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"** (Lewis et al., 2020)
    - URL: https://arxiv.org/abs/2005.11401
    - Foundation for RAG approach in this project

17. **"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"** (Wei et al., 2022)
    - URL: https://arxiv.org/abs/2201.11903
    - Technique used in ConclusionEngine agent prompts

18. **"Multi-Agent Reinforcement Learning: A Survey"** (Busoniu et al., 2008)
    - Background on multi-agent coordination (future RL optimization)

19. **"HNSW: Hierarchical Navigable Small World graphs"** (Malkov & Yashunin, 2018)
    - URL: https://arxiv.org/abs/1603.09320
    - Algorithm used by Qdrant for vector search

**Compliance & Governance**

20. **EU AI Act**: Regulation on artificial intelligence
    - URL: https://artificialintelligenceact.eu/
    - Relevant: High-risk AI systems (quality management, transparency)

21. **GDPR**: General Data Protection Regulation
    - URL: https://gdpr.eu/
    - Relevant: Data subject rights, DPA with LLM providers

22. **SOC 2**: Security and compliance framework
    - URL: https://www.aicpa.org/soc2
    - Future: SOC 2 Type II audit (Year 2)

### 22.3 Future Enhancements with P16 ML Data Pipeline

The Enterprise ML Data Pipeline Platform (P16) can extend the Multi-Agent RCA Platform with scalable infrastructure for real-time failure ingestion, distributed agent orchestration, and production-grade model serving:

**Real-time Failure Ingestion (Apache Kafka)**:
- Stream failure data from testers → Kafka `failures-topic` → immediate RCA triggers
- Support 1000s failures/day ingestion with <30 sec latency (current: batch hourly)
- Priority queues: critical failures (yield <80%) → high-priority RCA agents
- Event-driven architecture: new failure → auto-spawn RCA agent swarm

**Distributed Agent Orchestration (Apache Spark + Databricks)**:
- Parallelize 6 agents across Spark cluster (10× faster RCA than sequential)
- Distributed RAG: vector searches across 10 years of RCA reports using PySpark
- Multi-agent coordination at scale: 100 concurrent RCAs for daily failure batch
- GPU-accelerated LLM inference: GPT-4/Claude API calls distributed across cluster

**Feature Store (Delta Lake)**:
- Versioned failure tables: `failure_patterns`, `rca_history`, `solution_repository`
- ACID transactions: consistent reads across 6 agents querying same failure
- Time-travel: reproduce RCA from 6 months ago (regulatory audit trail)
- Shared knowledge base: P03 agents, P05 AMSA, P10 GNN all read same failure data

**Experiment Tracking (MLflow)**:
- Track multi-agent performance: RCA accuracy, time-to-solution, hallucination rate
- A/B testing: CrewAI vs. LangGraph, GPT-4 vs. Claude-3.5, 6-agent vs. 8-agent swarms
- LLM prompt versioning: track prompt templates for each agent role
- Automated agent selection: deploy champion agent configuration based on accuracy

**Orchestration (Apache Airflow)**:
- DAG workflow: Ingest failures → Prioritize → Spawn agents → Generate report → Email stakeholders
- Scheduled batch RCA: nightly analysis of all day's failures
- Agent health checks: restart hung agents, timeout after 30 min
- Automated escalation: if RCA confidence <70% → human expert review

**Model Serving (FastAPI + MLflow)**:
- Production API: `POST /api/v1/rca/analyze` with <2 min end-to-end RCA
- Serve agent swarm as microservices: `/data-agent`, `/pattern-agent`, `/solution-agent`
- Load balancing: distribute 100 concurrent RCAs across 10 agent instances
- Response caching: similar failures → reuse recent RCA (80% cache hit rate)

**Example Use Cases**:
- **Real-time RCA**: Kafka streams Bin5 failure spike → Airflow spawns priority RCA → 6 agents analyze in parallel on Spark → FastAPI returns root cause in <2 min → Automated email to yield engineer with fix recommendations
- **Distributed Knowledge Base**: Delta Lake stores 10 years RCA reports (500K failures) → Spark indexes for RAG → All 6 agents query in parallel (<5 sec vs. 60 sec sequential) → 90% faster RCA
- **Automated Retraining**: MLflow tracks RCA accuracy weekly → Airflow triggers prompt re-optimization when accuracy <85% → A/B test new prompts → Auto-deploy if >5% improvement
- **Cross-Project Intelligence**: P03 RCA identifies wafer edge defect → P04 ResNet confirms spatial pattern → P10 GNN traces propagation → P16 aggregates insights in Delta Lake → Future failures auto-solved

**Integration Timeline**:
- **Phase 1** (Month 1-2): Kafka ingestion + FastAPI serving
- **Phase 2** (Month 3-4): Delta Lake knowledge base + MLflow tracking
- **Phase 3** (Month 5-6): Spark distributed agents + Airflow orchestration
- **Phase 4** (Month 7+): Production deployment with 168% ROI validation

### 22.4 Glossary

**A**

- **AMSA**: Analog Mixed-Signal Automated (test system for analog/mixed-signal ICs)
- **API**: Application Programming Interface (REST endpoints for system access)
- **ARIA**: Accessible Rich Internet Applications (web accessibility standard)
- **Attention Mechanism**: Neural network technique that weights input importance (used in Transformers)
- **Autonomous Agent**: AI agent that operates independently, makes decisions without human intervention

**B**

- **Baseline**: Historical average performance (e.g., baseline yield 95%, baseline bin5 rate 5%)
- **BGA (Ball Grid Array)**: IC package type (e.g., BGA436 = 436-pin BGA)
- **Bin**: Test outcome category (bin1 = pass, bin5 = fail functional test, bin7 = fail parametric)
- **Blackboard Pattern**: Shared memory architecture where agents write findings for others to read
- **Blue-Green Deployment**: Deployment strategy with two identical environments (blue=active, green=staging)

**C**

- **Chain-of-Thought (CoT)**: Prompting technique asking LLM to explain reasoning step-by-step
- **Chroma/ChromaDB**: Embedded vector database (used in dev environments)
- **Conditional Routing**: LangGraph feature to route workflow based on state (if-else logic)
- **Consensus**: Agreement among agents on hypothesis ranking (majority vote or weighted average)
- **Correlation**: Statistical measure of relationship between variables (Pearson r, -1 to +1)
- **CrewAI**: Framework for building hierarchical agent teams (manager delegates to workers)
- **CSAT**: Customer Satisfaction Score (1-5 star rating)

**D**

- **DAU**: Daily Active Users (users who submit or view RCA each day)
- **Die**: Individual IC chip on wafer (before packaging)
- **Distributed Tracing**: Tracking requests across microservices (trace_id, span_id)
- **DPA**: Data Processing Addendum (GDPR-compliant contract with LLM providers)
- **DQN**: Deep Q-Network (reinforcement learning algorithm, used in P13)

**E**

- **Edge Effect**: Wafer map failure pattern (defects concentrated at wafer edge)
- **Embedding**: Numerical representation of text (768-dim vector for `all-mpnet-base-v2`)
- **End-to-End (E2E)**: Full workflow from input to output (submit RCA → completed report)

**F**

- **FA (Failure Analysis)**: Physical analysis of failed die (SEM, FIB, X-ray)
- **False Positive**: Incorrect root cause hypothesis (marked wrong by reviewer)
- **Few-Shot Learning**: Training with few examples (2-3 examples in prompt)
- **FIFO**: First-In-First-Out (queue discipline for RCA submissions)
- **Fine-Tuning**: Re-training LLM on domain-specific data (semiconductor RCA reports)
- **FTR (Functional Test Record)**: STDF record type (functional test results per die)

**G**

- **GAN (Generative Adversarial Network)**: Generative model (used in P07 for synthetic data)
- **Grafana**: Open-source dashboard platform (metrics visualization)
- **Graph Neural Network (GNN)**: Neural network for graph data (used in P10)

**H**

- **Hallucination**: LLM generates false information not grounded in data
- **HNSW**: Hierarchical Navigable Small World (fast approximate nearest neighbor index)
- **HPA (Horizontal Pod Autoscaler)**: Kubernetes auto-scaling (CPU/memory-based)
- **Hybrid Search**: Combines vector search (semantic) + keyword search (exact match)
- **Hypothesis**: Proposed root cause explanation (ranked by confidence 0-1)

**I**

- **IOPS**: Input/Output Operations Per Second (database performance metric)

**J**

- **JEDEC**: Joint Electron Device Engineering Council (semiconductor standards)
- **JSON Mode**: LLM output constraint (force valid JSON, no markdown)
- **JWT (JSON Web Token)**: Authentication token (RS256 signature, 8-hour expiry)

**K**

- **Knowledge Base**: Collection of historical RCA reports (50K reports, 10M vectors)
- **Kubernetes (K8s)**: Container orchestration platform (manages pods, services, HPA)

**L**

- **LangChain**: Framework for building LLM applications (StructuredTool, PromptTemplate)
- **LangGraph**: State machine framework for multi-agent workflows (nodes=agents, edges=transitions)
- **LLM (Large Language Model)**: AI model trained on vast text (GPT-4, Claude 3.5)
- **Lot**: Batch of wafers processed together (lot_id = "TC41x_LOT123")

**M**

- **MAU**: Monthly Active Users (users who submit ≥1 RCA/month)
- **MIR (Master Information Record)**: STDF header (lot_id, product, test program)
- **Multi-Agent System**: AI system with multiple autonomous agents collaborating

**N**

- **Neo4j**: Graph database (used in P10 for test failure propagation)
- **NER (Named Entity Recognition)**: NLP task extracting entities (product, test, failure mode)

**O**

- **OAuth2/OIDC**: Authentication protocols (SSO with Azure AD, Okta)
- **On-Prem**: On-premises (self-hosted infrastructure, not cloud)
- **OpenSearch**: Open-source search/analytics (Elasticsearch fork, log aggregation)
- **Orchestration**: Coordination of multiple agents/services (LangGraph, CrewAI)

**P**

- **Pareto Chart**: Bar chart showing most frequent contributors (80/20 rule)
- **PII (Personally Identifiable Information)**: Sensitive data (email, name, IP address)
- **Prompt**: Input text to LLM (system message + user query + examples)
- **PTR (Parametric Test Record)**: STDF record (voltage, current, frequency measurements per die)

**Q**

- **Qdrant**: Open-source vector database (distributed cluster, HNSW index)
- **Queue**: FIFO buffer for RCA submissions (Redis List, LPUSH/BRPOP)

**R**

- **RAG (Retrieval-Augmented Generation)**: LLM technique combining search + generation
- **RBAC (Role-Based Access Control)**: Authorization model (4 roles: user, reviewer, admin, curator)
- **RCA (Root Cause Analysis)**: Systematic investigation to identify failure root cause
- **Redis**: In-memory key-value store (caching, sessions, queue)
- **ResNet**: Residual Neural Network (CNN architecture, used in P02, P04)
- **ROI**: Return on Investment (net savings / investment cost)
- **RTO (Recovery Time Objective)**: Max downtime acceptable (4 hours for DR)
- **RPO (Recovery Point Objective)**: Max data loss acceptable (1 hour backup interval)

**S**

- **Shmoo Plot**: 2D sweep plot (voltage vs frequency, used in P15)
- **Similarity Score**: Cosine similarity between embeddings (0.0-1.0, higher = more similar)
- **SLO (Service Level Objective)**: Performance target (p95 latency <500ms)
- **SOC 2**: Security audit framework (Type II = controls effective over time)
- **SSO (Single Sign-On)**: Centralized authentication (Azure AD, Okta)
- **State Machine**: Workflow graph (nodes=states, edges=transitions, LangGraph)
- **STDF (Standard Test Data Format)**: Binary format for test data (JEDEC standard)
- **ConclusionEngine**: Agent that aggregates findings from specialist agents, generates final hypothesis

**T**

- **TC3x, TC4x, TC5x**: Automotive MCU product families (Infineon TriCore)
- **TLS (Transport Layer Security)**: Encryption protocol (TLS 1.3 for HTTPS)
- **Tool (Agent Tool)**: Function an agent can call (STDF parser, wafer map generator, t-test)
- **Transfer Learning**: Re-using pre-trained model (ImageNet → wafer maps, used in P02)
- **Transformer**: Neural network architecture (attention mechanism, used in P14)
- **t-test**: Statistical test comparing two means (bin5 rate: test lot vs baseline)

**U**

- **UAT (User Acceptance Testing)**: Testing by end users (pilot engineers validate in staging)
- **U-Net**: CNN architecture for image segmentation (used in P04 wafer map defect segmentation)

**V**

- **VAE (Variational Autoencoder)**: Generative model (used in P07 for synthetic data)
- **Vector Database**: Database optimized for high-dimensional vector search (Qdrant, Chroma)
- **Vector Embedding**: Numerical representation (text → 768-dim vector)

**W**

- **Wafer**: Silicon disc containing hundreds of die (before dicing and packaging)
- **Wafer Map**: 2D visualization of die test results (color-coded by bin)
- **WCAG (Web Content Accessibility Guidelines)**: Accessibility standard (Level AA compliance)
- **WebSocket**: Bidirectional communication protocol (real-time status updates)
- **WIR (Wafer Information Record)**: STDF record (wafer_id, die count, start time)

**X**

- **XGBoost**: Gradient boosting library (used in P01, P08 for tabular data prediction)

**Y**

- **Yield**: Percentage of die passing test (yield = bin1 count / total die)

**Z**

- **Z-score**: Standard score (outlier detection, |Z| >3 indicates outlier)

---

**END OF DOCUMENT**

---

**Document Revision History**:
- **v1.0** (2025-12-04): Initial PRD created, all 22 sections complete
- **v1.1** (future): Updates after pilot feedback (Week 15-16)
- **v1.2** (future): Updates after GA rollout (Month 5-6)

**Approval Signatures**:
- **Product Manager**: _________________________ Date: _______
- **Engineering Lead**: _________________________ Date: _______
- **Yield Engineering Director**: ________________ Date: _______
- **VP Engineering**: ___________________________ Date: _______

---

**Total PRD Line Count**: ~6,300 lines  
**Total PRD Word Count**: ~45,000 words  
**Estimated Reading Time**: 3-4 hours (comprehensive review)

---

