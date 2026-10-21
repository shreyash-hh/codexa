# CODEXA: MINI PROJECT VIVA & TECHNICAL EXPLANATION GUIDE

**Project Title:** CODEXA: An Intelligent Platform for Automated Software Repository Quality Assessment and Risk Analysis  
**Candidate:** Shreyash Anilrao Thakare (PRN: 125M1H048)  
**Degree:** Master of Computer Applications (MCA) — Semester III  
**Guide:** Dr. Avinash Chormale  
**Institute:** Pimpri Chinchwad College of Engineering (PCCOE), Nigdi, Pune  
**Academic Year:** 2026 – 2027  

---

## 📌 TABLE OF CONTENTS
1. [Project Overview & Problem Statement](#1-project-overview--problem-statement)
2. [End-to-End System Architecture & Data Flow](#2-end-to-end-system-architecture--data-flow)
3. [The Multi-Tool Analysis Suite: Role of Each Tool](#3-the-multi-tool-analysis-suite-role-of-each-tool)
4. [Mathematical Formulation of the CODEXA Scoring Model](#4-mathematical-formulation-of-the-codexa-scoring-model)
5. [Database Schema & Data Models](#5-database-schema--data-models)
6. [Step-by-Step Execution Guide](#6-step-by-step-execution-guide)
7. [Offline Demo Mode for Viva Presentation](#7-offline-demo-mode-for-viva-presentation)
8. [Top 20 Viva Questions & Expert Answers](#8-top-20-viva-questions--expert-answers)

---

## 1. PROJECT OVERVIEW & PROBLEM STATEMENT

### 1.1 The Real-World Problem
Modern software repositories accumulate thousands of lines of code, dozens of third-party dependencies, and contributions from multiple developers. Assessing overall code quality, maintainability, and security vulnerabilities manually is practically impossible.  
Traditionally, developers and auditors run separate, fragmented tools:
- One tool for linting (e.g., Pylint)
- One tool for complexity (e.g., Radon)
- One tool for security scanning (e.g., Bandit or Semgrep)
- One tool for dependencies (e.g., pip-audit)

**The Bottleneck:** Each tool outputs disparate formats (text, stdout, JSON, bitmasks), requires individual setup, and provides no consolidated health score or prioritized remediation plan.

### 1.2 The CODEXA Solution
CODEXA solves this by providing a unified, automated, web-based platform:
1. **Automated Ingestion:** Accepts any public or token-authenticated GitHub repository URL.
2. **Multi-Tool Analysis Engine:** Executes a 5-layer audit suite covering Code Quality, Cyclomatic Complexity, AST Security Vulnerabilities, and Dependency CVEs.
3. **Multi-Dimensional Scoring Engine:** Computes a normalized composite health score (0–100) using a mathematically transparent, defensible formula.
4. **AI Recommendation Engine:** Passes verified findings to Google Gemini AI (with heuristic fallback) to generate human-readable, prioritized remediation guidance.
5. **Interactive Dashboard & PDF Export:** Renders an interactive React/Tailwind dashboard and generates downloadable ReportLab executive PDF reports.

---

## 2. END-TO-END SYSTEM ARCHITECTURE & DATA FLOW

```
                          ┌────────────────────────┐
                          │ User / Evaluator       │
                          │ Submits GitHub URL     │
                          └───────────┬────────────┘
                                      │ HTTP POST /api/analyze/
                                      ▼
                        ┌───────────────────────────┐
                        │ Django Backend Orchestrator│
                        └─────────────┬─────────────┘
                                      │
            ┌─────────────────────────┼────────────────────────┐
            ▼                         ▼                        ▼
  ┌──────────────────┐      ┌──────────────────┐     ┌──────────────────┐
  │ GitHub API       │      │ Git Clone        │     │ DB Check         │
  │ Metadata Fetch   │      │ (depth=1 temp)   │     │ (SQLite/Postgres)│
  └─────────┬────────┘      └─────────┬────────┘     └──────────────────┘
            │                         │
            └────────────┬────────────┘
                         ▼
        ┌──────────────────────────────────────────────────┐
        │       Multi-Tool Analysis Engine (5 Layers)       │
        ├──────────────────────┬───────────────────────────┤
        │ Layer 1: Pylint      │ Code style, PEP8, smells  │
        │ Layer 2: Radon       │ Cyclomatic complexity (CC)│
        │ Layer 3: Bandit      │ AST Python security audit │
        │ Layer 4: Semgrep/AST │ Semantic security rules   │
        │ Layer 5: pip-audit   │ Supply chain PyPI CVEs    │
        └──────────────────────┬───────────────────────────┘
                               │ Normalized Findings List
                               ▼
        ┌──────────────────────────────────────────────────┐
        │         CODEXA Scoring Calculation Engine        │
        │  Quality (30%) + Security (45%) + Dep (25%)      │
        └──────────────────────┬───────────────────────────┘
                               │
            ┌──────────────────┴───────────────────┐
            ▼                                      ▼
┌──────────────────────────────┐       ┌──────────────────────────────┐
│ AI Recommendation Engine     │       │ Database Persistence         │
│ (Google Gemini 2.5 Flash /   │       │ Repository, AnalysisRun,     │
│ Heuristic Rule Fallback)     │       │ Score, Findings, Recs        │
└───────────┬──────────────────┘       └──────────────┬───────────────┘
            │                                         │
            └──────────────────┬──────────────────────┘
                               ▼
            ┌─────────────────────────────────────────┐
            │ Delivery & Presentation Layer           │
            ├────────────────────┬────────────────────┤
            │ React + TS UI      │ ReportLab PDF      │
            │ Interactive Dash   │ Executive Report   │
            └────────────────────┴────────────────────┘
```

---

## 3. THE MULTI-TOOL ANALYSIS SUITE: ROLE OF EACH TOOL

| Tool | Domain | Mechanism | Why Included in CODEXA |
|---|---|---|---|
| **Radon** | Maintainability | Computes Cyclomatic Complexity (McCabe metric) ranking blocks from A (1–5, low risk) to F (41+, unmaintainable). | Measures technical debt and identifies convoluted functions that need refactoring before they cause production regressions. |
| **Pylint** | Code Quality | Analyzes Python source code against PEP 8 style guides, convention violations, and common programming errors. | Catches syntax smells, unused variables, undefined symbols, and import anti-patterns. |
| **Bandit** | Security | Traverses the Abstract Syntax Tree (AST) looking for known insecure patterns (e.g., hardcoded passwords, shell injections, unsafe YAML). | Standard open-source security linter built specifically for Python codebases. |
| **Semgrep / AST Scanner** | Security | Performs semantic pattern matching across the AST for complex vulnerabilities (e.g., `eval()`, `exec()`, `shell=True`, weak hashes). | Deep rule-based analysis that validates security invariants. Features an in-built native AST fallback on Windows. |
| **pip-audit** | Dependencies | Scans `requirements.txt` manifests against the Python Packaging Advisory Database (PyPA) for known CVEs. | Detects vulnerable third-party dependencies before malicious or outdated packages compromise the production server. |
| **Google Gemini API** | AI Guidance | Large Language Model (Gemini 2.5 Flash) prompted with structured findings and domain scores. | Translates dense, technical scanner outputs into prioritized, plain-English remediation guidance. |
| **ReportLab** | Reporting | High-performance Python PDF library that constructs programmatic vector documents in-memory. | Creates an executive summary PDF with custom tables and badges without requiring heavy headless browsers. |

---

## 4. MATHEMATICAL FORMULATION OF THE CODEXA SCORING MODEL

The CODEXA scoring engine uses a mathematically rigorous, transparent, and defensible model:

### Step 1: Severity Penalty Weights ($W_s$)
Every finding $f$ is assigned a penalty weight based on its classified severity:
- **Critical:** $W_{\text{critical}} = 25.0$ points
- **High:** $W_{\text{high}} = 10.0$ points
- **Medium:** $W_{\text{medium}} = 4.0$ points
- **Low:** $W_{\text{low}} = 1.5$ points
- **Info:** $W_{\text{info}} = 0.5$ points

### Step 2: Domain Pillar Sub-Score Calculation
Findings are grouped into three distinct domain pillars:
1. **Quality Pillar ($S_Q$):** Tools = $\{\text{Pylint}, \text{Radon}\}$
2. **Security Pillar ($S_S$):** Tools = $\{\text{Bandit}, \text{Semgrep}\}$
3. **Dependency Pillar ($S_D$):** Tools = $\{\text{pip-audit}\}$

For each pillar $k \in \{Q, S, D\}$, total penalty $P_k$ is computed:
$$P_k = \sum_{f \in \text{Findings}_k} W_s(f)$$

*(Note: High-volume Pylint conventions apply a $0.4\times$ damping factor to prevent artificial zeroing of quality scores due to minor formatting warnings).*

The domain sub-score $S_k$ is bounded between 0.00 and 100.00:
$$S_k = \max\left(0.00, \; 100.00 - \min(100.00, P_k)\right)$$

### Step 3: Composite Holistic Score ($S_C$)
The composite score is the weighted linear combination of the three domain pillars:
$$S_C = \alpha \cdot S_S + \beta \cdot S_Q + \gamma \cdot S_D$$

Where:
- $\alpha = 0.45$ (**45% Security Weight** — direct operational breach and exploit risk)
- $\beta = 0.30$ (**30% Quality Weight** — maintainability, bug proneness, and technical debt)
- $\gamma = 0.25$ (**25% Dependency Weight** — third-party supply chain CVE exposure)
- $\alpha + \beta + \gamma = 1.00$

$$S_C = 0.45 \times S_S + 0.30 \times S_Q + 0.25 \times S_D$$

---

## 5. DATABASE SCHEMA & DATA MODELS

CODEXA utilizes a relational schema (SQLite for development, PostgreSQL-ready):

1. **`Repository`**: Stores repository identification and state:
   - `github_url` (URL, unique), `name`, `owner`, `cloned_at`, `status` (`pending`, `cloned`, `failed`), `created_at`.
2. **`AnalysisRun`**: Tracks individual execution runs:
   - `repository` (FK to Repository, CASCADE), `started_at`, `completed_at`, `status` (`pending`, `running`, `completed`, `failed`).
3. **`Finding`**: Stores discrete issues detected by tools:
   - `run` (FK to AnalysisRun, CASCADE), `tool_name` (e.g., `pylint`, `radon`, `bandit`, `semgrep`, `pip-audit`), `severity` (`critical`, `high`, `medium`, `low`, `info`), `message` (text), `file_path` (string), `line_no` (integer, nullable).
4. **`Score`**: Stores computed health metrics (1:1 with AnalysisRun):
   - `run` (OneToOneField to AnalysisRun), `quality_score` (float), `security_score` (float), `dependency_score` (float), `composite_score` (float).
5. **`Recommendation`**: Stores prioritized remediation advice:
   - `run` (FK to AnalysisRun, CASCADE), `text` (text), `priority` (`critical`, `high`, `medium`, `low`).

---

## 6. STEP-BY-STEP EXECUTION GUIDE

### Prerequisites
- Python 3.10+ (Verified on Python 3.13)
- Node.js 18+ and npm
- Git CLI installed

### Step 1: Start the Django Backend
Open a terminal in `mini project/CODEXA`:
```bash
python manage.py runserver 127.0.0.1:8000
```
*Expected Output:*
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 2: Start the React Frontend
Open a second terminal in `mini project/CODEXA/frontend`:
```bash
npm run dev
```
*Expected Output:*
```
  VITE v8.3.0  ready in 250 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 3: Run the Test Suite
To verify all backend endpoints, analyzers, and scoring algorithms:
```bash
python manage.py test
```
*Expected Output:*
```
Ran 8 tests in ~30s
OK
```

---

## 7. OFFLINE DEMO MODE FOR VIVA PRESENTATION

**Critical Safety Net for Viva:**  
If college Wi-Fi is unavailable or the GitHub API is rate-limited during your project demonstration:
1. Open the dashboard at `http://localhost:5173/`.
2. Notice the **"Recent Audits & Offline Demo Archive"** bar located immediately below the input box.
3. Click on **`Run #7 (codexa)`** or **`Run #6`**.
4. The frontend will immediately fetch the full archived run (`GET /api/runs/7/`) without touching the internet or cloning from GitHub!
5. The complete dashboard with **309 findings**, 4 domain score cards, Gemini recommendations, and the **"Download Executive PDF"** button will render instantly.

---

## 8. TOP 20 VIVA QUESTIONS & EXPERT ANSWERS

### Q1: What is the main objective of CODEXA?
**Answer:**  
> "CODEXA is an intelligent platform designed to automate the quality assessment and security auditing of software repositories. Instead of manually running fragmented tools for linting, security, complexity, and dependencies, CODEXA consolidates Radon, Pylint, Bandit, Semgrep, and pip-audit into a single pipeline, computes a transparent composite score from 0 to 100, and generates AI-driven remediation guidance."

### Q2: Why did you choose Django for the backend and React for the frontend?
**Answer:**  
> "Django provides enterprise-grade ORM, built-in security, and Python ecosystem interoperability, which is essential because all our analysis tools (Radon, Pylint, Bandit, pip-audit, ReportLab) are native Python packages. React with TypeScript was chosen for the frontend because it offers strict type safety, modular component architecture, and responsive real-time state updates when filtering hundreds of findings."

### Q3: Explain how the CODEXA composite score is calculated.
**Answer:**  
> "The composite score is a weighted linear model: 45% Security + 30% Quality + 25% Dependencies.  
> Each domain starts at 100 points. As findings are detected, penalty points are deducted based on severity (Critical = 25, High = 10, Medium = 4, Low = 1.5, Info = 0.5).  
> The final composite score represents a holistic index where security vulnerabilities carry the greatest weight due to immediate breach risks."

### Q4: Why does Security have a 45% weight while Quality has 30%?
**Answer:**  
> "In software engineering, a quality issue (such as a long function or missing docstring) increases maintainability friction, but does not immediately take a system offline or leak data. In contrast, a security vulnerability (such as SQL injection, shell execution, or hardcoded secrets) represents an existential operational risk that can lead to remote code execution or regulatory fines. Therefore, security carries the highest weight."

### Q5: How does Radon calculate Cyclomatic Complexity, and what do the ranks mean?
**Answer:**  
> "Radon uses Thomas McCabe's Cyclomatic Complexity metric, which measures the number of linearly independent paths through a program's source code based on decision points (like `if`, `while`, `for`, `except`).  
> Radon categorizes code into ranks:  
> - Rank A (1–5): Simple, low risk.  
> - Rank B (6–10): Well-structured, moderate complexity.  
> - Rank C (11–20): High complexity, difficult to unit test.  
> - Rank D to F (21–41+): Extremely convoluted, high bug hazard, requires urgent refactoring."

### Q6: What is the difference between Bandit and Semgrep?
**Answer:**  
> "Bandit is a specialized AST security scanner built specifically for Python that searches for dangerous standard library calls, insecure random generators, and hardcoded credentials.  
> Semgrep is a semantic, polyglot rule engine that matches code patterns across syntax trees. In CODEXA, Bandit catches standard Python vulnerability patterns, while Semgrep (with our native AST fallback engine) validates semantic invariants like deserialization risks, shell injection, and weak cryptography."

### Q7: How does pip-audit work, and what is its role?
**Answer:**  
> "pip-audit inspects Python dependency manifests (`requirements.txt`, `Pipfile.lock`, `pyproject.toml`) and queries the official PyPA (Python Packaging Advisory Database) to check if any installed packages contain known Common Vulnerabilities and Exposures (CVEs). It alerts developers to upgrade vulnerable third-party libraries to patched versions before deployment."

### Q8: What role does Google Gemini AI play in CODEXA?
**Answer:**  
> "Static analysis tools output raw, technical warnings that can overwhelm developers. CODEXA passes the top findings, domain scores, and repository context to Gemini 2.5 Flash using a structured prompt. Gemini acts as an expert DevSecOps architect, grouping related issues and generating prioritized, plain-English remediation instructions. If the Gemini API key is unavailable or the system is offline, our deterministic heuristic fallback engine automatically generates rule-based remediation guidance."

### Q9: How do you prevent cloning large repositories from overloading server disk space?
**Answer:**  
> "We implement two key architectural safeguards:  
> First, Git cloning uses `--depth 1` (shallow clone) and `--single-branch`, fetching only the latest commit rather than the entire commit history, which reduces bandwidth and storage by over 80%.  
> Second, repositories are cloned into isolated temporary directories created with `tempfile.mkdtemp()`. The analysis view wraps execution in a `try...finally` block that invokes `cleanup_cloned_repo()` to safely wipe the temporary files from disk even if analysis encounters an error."

### Q10: How does CODEXA handle GitHub API rate limits?
**Answer:**  
> "The GitHub public REST API allows 60 unauthenticated requests per hour per IP. In CODEXA, users can optionally supply a GitHub Personal Access Token (PAT), which raises the rate limit to 5,000 requests per hour and allows cloning private repositories. Furthermore, if metadata fetch experiences rate limits, the system falls back gracefully to default metadata so the core code analysis is never blocked."

### Q11: How does ReportLab generate the PDF report?
**Answer:**  
> "Unlike tools that render an HTML page in a headless browser (like Puppeteer or wkhtmltopdf) which consumes significant memory, ReportLab compiles vector PDF primitives directly into a Python `io.BytesIO` in-memory byte buffer. It builds the document flow using `SimpleDocTemplate`, custom `ParagraphStyle` typography, executive score tables, and severity badges, and streams the PDF directly as an attachment HTTP response."

### Q12: What happens if a repository has no Python files?
**Answer:**  
> "Our analyzers scan the directory recursively for `.py` files using `find_python_files()`. If zero Python files are detected, Pylint, Bandit, and Radon return empty findings lists, and pip-audit checks if any requirement manifests exist. The scoring engine evaluates the repository as clean for Python metrics (score = 100), and the system informs the user that no Python code was present for analysis."

### Q13: How does CODEXA connect to your Seminar topic?
**Answer:**  
> "My seminar synthesized research showing that pure LLMs hallucinate during code review and cannot be trusted alone (Park & Kim, 2026), while developer speed outpaces testing (Starace, 2026). Park & Kim proved that a **Neuro-Symbolic architecture**—combining deterministic AST static analysis with AI models—achieved 94.2% accuracy and 0 missed safety bugs at Hyundai Mobis. CODEXA is the practical implementation of this exact Neuro-Symbolic framework."

### Q14: Explain the difference between Static Analysis and Dynamic Analysis.
**Answer:**  
> "Static analysis analyzes source code without executing it—examining the syntax tree, control flow, and token structures to find bugs, anti-patterns, and vulnerabilities before runtime.  
> Dynamic analysis evaluates software while it is running, monitoring CPU/memory usage, memory leaks, and responding to live inputs (e.g., fuzzing or profiling). CODEXA focuses on static code and supply chain analysis because it is fast, safe, and can audit unbuilt repositories."

### Q15: How does your database maintain referential integrity?
**Answer:**  
> "We define relational foreign keys in `core/models.py`:  
> - `AnalysisRun` has a foreign key to `Repository` with `on_delete=models.CASCADE`.  
> - `Finding`, `Recommendation`, and `Score` link to `AnalysisRun` with `on_delete=models.CASCADE`.  
> If an analysis run or repository is deleted, all associated findings, scores, and recommendations are cleanly removed by the database engine without leaving orphaned rows."

### Q16: How do you handle Windows file permission locks during cleanup?
**Answer:**  
> "On Windows, files inside `.git` (such as pack files and hooks) are often marked read-only by Git. A standard `shutil.rmtree()` raises a `PermissionError`. In `github_service.py`, we implement a custom error handler `_onerror` that calls `os.chmod(path, stat.S_IWRITE)` to strip the read-only attribute before deleting, ensuring 100% clean teardown on Windows systems."

### Q17: What security precautions are taken when running subprocesses in analyzers?
**Answer:**  
> "1. We never use `shell=True` in subprocess calls; commands are passed as strict argument lists (e.g., `[python_bin, '-m', 'bandit', ...]`), preventing shell injection.  
> 2. Every subprocess specifies an explicit `timeout=120` to prevent hanging processes from exhausting system resources.  
> 3. Standard output and errors are captured via `stdout=PIPE, stderr=PIPE` and parsed strictly using JSON serializers."

### Q18: What is the purpose of the new `GET /api/runs/` endpoint?
**Answer:**  
> "It enables the frontend to retrieve historical audit runs stored in the SQLite database. This allows users to browse past analyses, track code quality improvements over time, and serves as an offline viva presentation archive where full reports can be loaded without requiring internet access."

### Q19: What are the future enhancements planned for CODEXA?
**Answer:**  
> "1. Multi-language support: Extending static and security analysis to JavaScript/TypeScript (ESLint, Retire.js) and Java (SpotBugs).  
> 2. GitHub Actions CI/CD Integration: Packaging CODEXA as a GitHub Action that posts audit comments directly on pull requests.  
> 3. Automated PR Remediation: Integrating an agent that automatically commits patches for detected vulnerabilities."

### Q20: What did you personally learn from building CODEXA?
**Answer:**  
> "Building CODEXA gave me deep, hands-on experience in full-stack architecture, REST API design with Django REST Framework, Abstract Syntax Tree parsing, supply chain security, and modern React/TypeScript UI development. More importantly, it taught me how to translate complex theoretical research into an operational software engineering product that solves a real industry problem."
