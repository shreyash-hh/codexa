# PIMPRI CHINCHWAD EDUCATION TRUST'S
# PIMPRI CHINCHWAD COLLEGE OF ENGINEERING (PCCOE)
### Sector No. 26, Pradhikaran, Nigdi, Pune – 411044
### Department of Master of Computer Applications (MCA)

---

# A MINI PROJECT REPORT ON
## **CODEXA: An Intelligent Platform for Automated Software Repository Quality Assessment and Risk Analysis**

*Submitted in partial fulfillment of the requirements for the degree of*  
### **MASTER OF COMPUTER APPLICATIONS (MCA) — SEMESTER III**

---

### **Submitted By:**
**Shreyash Anilrao Thakare**  
PRN: 125M1H048 | Roll No: 125M1H048  
Email: shreyash.thakare25@pccoepune.org  

### **Under the Guidance Of:**
**Dr. Avinash Chormale**  
Associate Professor, Department of MCA  
PCCOE, Nigdi, Pune  

### **Academic Year:** 2026 – 2027

---

## CERTIFICATE OF APPROVAL

This is to certify that the Mini Project Report entitled **"CODEXA: An Intelligent Platform for Automated Software Repository Quality Assessment and Risk Analysis"** submitted by **Shreyash Anilrao Thakare** (PRN: **125M1H048**) is a bonafide record of work carried out by him under my supervision and guidance, in partial fulfillment of the requirements for the award of the degree of **Master of Computer Applications (MCA) — Semester III** of Savitribai Phule Pune University / Pimpri Chinchwad College of Engineering, Pune during the academic year **2026 – 2027**.

The project report has been examined and approved for submission as per the prescribed curriculum standards.

| Signatures: | | |
| :---: | :---: | :---: |
| **Dr. Avinash Chormale**<br/>Project Guide | **Project Coordinator**<br/>Department of MCA | **Head of Department**<br/>Department of MCA |
| | | |
| ____________________<br/>**Internal Examiner** | | ____________________<br/>**External Examiner** |

---

## CANDIDATE'S DECLARATION

I hereby declare that the mini project report entitled **"CODEXA: An Intelligent Platform for Automated Software Repository Quality Assessment and Risk Analysis"** is an authentic record of my own work carried out under the guidance of **Dr. Avinash Chormale**, Department of Master of Computer Applications, Pimpri Chinchwad College of Engineering, Pune.

I confirm that this project report has not been submitted elsewhere for the award of any other degree, diploma, or fellowship. All secondary sources, external software tools, libraries, and publications referenced herein have been appropriately cited and acknowledged.

**Date:** October 19, 2026  
**Place:** Nigdi, Pune  
**Shreyash Anilrao Thakare** (PRN: 125M1H048)  

---

## ACKNOWLEDGEMENT

I express my deep sense of gratitude and respect to my project guide, **Dr. Avinash Chormale**, for his invaluable mentorship, consistent encouragement, and insightful feedback throughout the conception, architecture, and implementation of CODEXA.

I extend my sincere thanks to the **Head of Department** and all faculty members of the Department of Master of Computer Applications for providing computing facilities, academic support, and constructive reviews. I also thank the leadership of **Pimpri Chinchwad College of Engineering** for fostering a research-driven environment.

Finally, I am profoundly grateful to my family and fellow classmates for their unwavering encouragement, patience, and cooperation throughout this endeavor.

---

## ABSTRACT

Modern software development relies heavily on version-controlled repositories where source code expands rapidly across distributed teams, third-party libraries, and evolving coding standards. As repositories grow, maintaining code hygiene, controlling technical debt, and identifying critical security vulnerabilities becomes increasingly difficult. Traditionally, software engineers and auditors run isolated command-line tools—such as Pylint for linting, Radon for cyclomatic complexity, Bandit for security patterns, and pip-audit for dependency CVEs. This fragmented workflow forces developers to manually parse disparate output streams, lacks a unified health metric, and provides no clear, prioritized remediation strategy.

**CODEXA** is an intelligent, full-stack, web-based platform designed to resolve this fragmentation. By accepting any public or private GitHub repository URL, CODEXA orchestrates an automated, five-layer auditing suite that evaluates code maintainability, structural complexity, Abstract Syntax Tree (AST) security risks, and software supply chain exposures. Findings are synthesized into a mathematically transparent, defensible **CODEXA Composite Score (0–100)** using a three-pillar model (45% Security, 30% Quality, 25% Dependencies). To eliminate manual review fatigue, verified findings are forwarded to an AI Recommendation Engine powered by Google Gemini (with an offline deterministic rule-based fallback) to generate actionable, plain-English remediation guidance. CODEXA features a high-performance React 19 / TypeScript dashboard, an offline demonstration archive for evaluation resilience, and a vector ReportLab PDF reporting engine. The platform bridges the gap between raw static analysis data and actionable software engineering governance.

**Project Key Contributions:**
1. Unified orchestration of five static and dependency scanners within an asynchronous Python backend.
2. Transparent composite scoring formula balancing security criticality against maintainability debt.
3. Implementation of the Neuro-Symbolic auditing paradigm, pairing deterministic AST verification with AI guidance.
4. Resilient cross-platform architecture with automated Windows file locking safeguards and offline presentation support.

**Keywords:** Static Code Analysis, Cyclomatic Complexity, Abstract Syntax Tree (AST), Software Supply Chain Security, Vulnerability Auditing, Neuro-Symbolic AI, Django REST Framework, React.

---

## TABLE OF CONTENTS

| Chapter / Section | Topic / Section Title | Page No. |
| :---: | :--- | :---: |
| — | Certificate of Approval | ii |
| — | Candidate's Declaration & Acknowledgement | iii |
| — | Abstract & Keywords | iv |
| **1** | **Introduction** | **1** |
| 1.1 | Project Overview & Background | 1 |
| 1.2 | Problem Statement & Real-World Bottlenecks | 1 |
| 1.3 | Objectives of CODEXA | 1 |
| 1.4 | Scope of the Proposed System | 2 |
| 1.5 | Proposed Methodology & Lifecycle Approach | 2 |
| 1.6 | Report Organization | 2 |
| **2** | **Literature Survey & Related Work** | **3** |
| 2.1 | Review of Existing Isolated Tools | 3 |
| 2.2 | The Neuro-Symbolic Imperative (Seminar Research Linkage) | 3 |
| 2.3 | Comparative Evaluation: Existing Systems vs. CODEXA | 3 |
| **3** | **Software Requirements Specification (SRS)** | **4** |
| 3.1 | Functional Requirements (FR-1 to FR-8) | 4 |
| 3.2 | Non-Functional Requirements (NFR-1 to NFR-4) | 4 |
| 3.3 | Hardware & Software Requirements Specification | 5 |
| 3.4 | User Characteristics & Operating Environment | 5 |
| 3.5 | Feasibility Study (Technical, Operational, Economic) | 5 |
| **4** | **System Design & Architecture** | **6** |
| 4.1 | End-to-End System Block Architecture | 6 |
| 4.2 | Data Flow Modeling (Level 0 Context & Level 1 DFD) | 6 |
| 4.3 | Mathematical Formulation of CODEXA Composite Scoring Model | 7 |
| 4.4 | Database Design & Relational Entity-Relationship Models | 7 |
| **5** | **Methodology & Implementation Details** | **8** |
| 5.1 | Django Backend Orchestration & REST Endpoints | 8 |
| 5.2 | Five-Layer Static & Dependency Analysis Engine | 8 |
| 5.3 | AI Recommendation Engine (Gemini & Heuristic Fallback) | 9 |
| 5.4 | ReportLab Vector PDF Generation Engine | 9 |
| 5.5 | React 19 / TypeScript / Tailwind CSS Dashboard | 9 |
| **6** | **Testing, Quality Assurance & Security Safeguards** | **10** |
| 6.1 | Automated Unit & Integration Test Suite Verification | 10 |
| 6.2 | Subprocess Execution Safety & Sandbox Isolation | 10 |
| 6.3 | Windows Permission & File Locking Cleanup Handlers | 10 |
| 6.4 | Offline Presentation Archive Mode for Viva Defense | 10 |
| **7** | **Results, Evaluation & Discussion** | **11** |
| 7.1 | Empirical Case Study: Full Audit of CODEXA Codebase | 11 |
| 7.2 | Multi-Tool Finding Distribution & Score Derivation | 11 |
| 7.3 | Performance & Execution Benchmarks | 11 |
| **8** | **Conclusion & Future Scope** | **12** |
| 8.1 | Summary of Achievements & Academic Outcomes | 12 |
| 8.2 | Future Scope & Planned Engineering Extensions | 12 |
| **—** | **References & Bibliography** | **13** |

---

## CHAPTER 1: INTRODUCTION

### 1.1 Project Overview & Background
Software engineering practices have transformed radically with the ubiquitous adoption of distributed version control systems, collaborative open-source ecosystems, and rapid agile release cycles. Source code repositories hosted on platforms such as GitHub serve as the primary operational backbone for software organizations. Within these repositories, codebases expand exponentially across multiple contributors, diverse coding habits, and deep trees of third-party dependencies.

However, rapid feature delivery frequently outpaces code review rigor. Over time, repositories accumulate structural decay, known in software engineering as *technical debt*. Convoluted control flow increases defect rates; outdated third-party packages introduce publicly known exploits (Common Vulnerabilities and Exposures, or CVEs); and developers inadvertently commit security flaws such as hardcoded credentials, unsafe shell executions, or dynamic code evaluation. Consequently, evaluating repository health before deployment is a paramount engineering necessity.

### 1.2 Problem Statement & Real-World Bottlenecks
While numerous specialized code analysis tools exist in the software ecosystem, they operate in severe isolation. A typical development team or security auditor must manually execute and coordinate multiple disconnected tools:
- **Linting & Style Checkers:** Tools like Pylint enforce PEP 8 standards and catch syntax smells but do not evaluate deep security vulnerabilities.
- **Complexity Calculators:** Tools like Radon compute Cyclomatic Complexity but provide no insight into whether a complex block contains an injection exploit.
- **Static Security Scanners:** Tools like Bandit and Semgrep inspect Abstract Syntax Trees (AST) for insecure function calls but ignore code maintainability and dependency supply chains.
- **Dependency Checkers:** Tools like pip-audit check manifests against vulnerability databases but cannot analyze the repository's proprietary source code.

**The Industry Bottlenecks:**
1. **Disparate Output Formats:** Each tool produces incompatible outputs (unstructured terminal text, complex JSON, or POSIX exit bitmasks), requiring laborious manual aggregation.
2. **Absence of a Unified Health Index:** Organizations have no single, defensible metric (e.g., a 0–100 score) to quantify overall repository quality and risk.
3. **Alert Fatigue & Lack of Remediation Guidance:** Running multiple tools generates hundreds of raw warnings. Developers are overwhelmed by alerts without knowing which issues pose immediate exploit risks versus trivial cosmetic warnings.

### 1.3 Objectives of CODEXA
CODEXA was designed and implemented to provide a unified, automated, intelligent platform that overcomes these challenges:
1. **Automate Repository Ingestion:** Enable one-click auditing of any public or token-authenticated GitHub repository without requiring local developer environment setup.
2. **Implement a 5-Layer Audit Suite:** Orchestrate Radon, Pylint, Bandit, Semgrep/AST, and pip-audit within a unified Python pipeline.
3. **Formulate a Defensible Composite Scoring Model:** Calculate normalized domain scores across Security (45%), Quality (30%), and Dependencies (25%) on a standardized 0–100 scale.
4. **Deliver AI-Powered Remediation:** Leverage Google Gemini (with an automated rule-based fallback) to translate dense technical warnings into prioritized, plain-English refactoring steps.
5. **Provide Multi-Channel Reporting:** Render an interactive React dashboard and generate downloadable, vector-rendered ReportLab PDF executive reports.

### 1.4 Scope of the Proposed System
The scope of CODEXA is strictly defined to deliver an end-to-end, high-assurance evaluation platform:
- **In-Scope Capabilities:** Automated ingestion of public and private GitHub repositories; static code quality and PEP 8 analysis; cyclomatic complexity ranking (McCabe Ranks A through F); Abstract Syntax Tree (AST) pattern matching for Python security flaws; dependency supply chain scanning against official PyPA CVE advisories; mathematical derivation of normalized domain scores and a single composite health index; AI-augmented remediation synthesis via Google Gemini 2.5 Flash; deterministic rule-based offline fallback; persistent relational history tracking; and vector PDF executive export.
- **Out-of-Scope Elements:** Dynamic runtime fuzzing and binary decompilation; non-Git version control providers (e.g., SVN, Mercurial); and automated commit pushing (remediation is advisory, leaving merging authority with the human engineer).

### 1.5 Proposed Methodology & Lifecycle Approach
CODEXA follows an agile, test-driven engineering lifecycle structured across four discrete operational phases:
1. **Ingestion Phase:** The user submits a GitHub repository URL. The system validates the URL, performs an authenticated or anonymous metadata fetch via GitHub REST API, and executes a shallow clone (`--depth 1`) into an isolated temporary folder.
2. **Multi-Tool Analysis Phase:** The Django orchestrator triggers five analyzer modules in parallel or sequence, parsing raw subprocess output streams into uniform, structured `Finding` objects.
3. **Mathematical Scoring Phase:** The scoring engine groups findings into Security, Quality, and Dependency pillars, applies severity penalty matrices and lint damping factors, and computes normalized sub-scores and the composite score.
4. **Synthesis & Presentation Phase:** Findings are forwarded to the AI engine to generate prioritized refactoring guidance. Results are committed to the SQLite relational database, rendered on the React dashboard, and compiled into a downloadable vector PDF report.

### 1.6 Report Organization
This project report is structured into eight thematic chapters:
- **Chapter 1: Introduction** establishes the project background, problem definition, objectives, scope, and methodology.
- **Chapter 2: Literature Survey** analyzes existing isolated auditing tools and establishes the Neuro-Symbolic research foundation.
- **Chapter 3: Software Requirements Specification (SRS)** specifies functional, non-functional, hardware, and feasibility requirements.
- **Chapter 4: System Design & Architecture** presents the end-to-end architecture, DFD diagrams, scoring formulas, and database schema.
- **Chapter 5: Methodology & Implementation** details backend orchestration, the 5-layer analyzer suite, AI guidance, and frontend design.
- **Chapter 6: Testing & Security** describes unit test verification, subprocess sandboxing, Windows permissions, and offline mode.
- **Chapter 7: Results & Evaluation** presents empirical case study results on the CODEXA codebase, score breakdowns, and benchmarks.
- **Chapter 8: Conclusion & Future Scope** summarizes project achievements and outlines roadmap extensions.

---

## CHAPTER 2: LITERATURE SURVEY & RELATED WORK

### 2.1 Review of Existing Isolated Tools
Static Application Security Testing (SAST) and static code analysis have a rich academic and commercial history. Understanding existing standalone tools reveals the structural motivation behind CODEXA:
- **Radon:** Implements Thomas McCabe's Cyclomatic Complexity (CC) metric, calculating linearly independent control flow paths. While excellent for quantifying technical debt, Radon does not detect security flaws.
- **Pylint:** The de facto standard Python linter. It rigorously checks PEP 8 conformity, refactoring opportunities, and code smells. However, high-volume style alerts often drown out critical runtime bugs.
- **Bandit:** An AST-based security linter created by the PyCQA community. It scans syntax nodes for dangerous standard library calls (e.g., `pickle.loads`, `os.system`), but lacks cross-language semantics.
- **Semgrep:** A fast, semantic pattern matcher that operates on ASTs using intuitive source-code-like syntax. While powerful, running Semgrep on native Windows environments often presents binary dependency challenges.
- **pip-audit:** Developed under the Python Packaging Authority (PyPA). It queries the Open Source Vulnerabilities (OSV) database to identify vulnerable dependencies, addressing supply chain risks.

### 2.2 The Neuro-Symbolic Imperative (Seminar Research Linkage)
The theoretical foundation of CODEXA directly builds upon the candidate's MCA seminar research on *"The Impact of AI-Generated Code on Software Maintainability, Security, and Developer Dependency"*. Contemporary studies highlight two critical software engineering realities:
1. **The Testing & Verification Gap (Starace, 2026):** While generative AI accelerates code generation by 30% to 50%, manual code verification remains slow. Reviewers suffer from cognitive fatigue and automation bias, allowing subtle vulnerabilities into production.
2. **Neuro-Symbolic Software Auditing (Park & Kim, 2026):** Research published in premier journals (*Information and Software Technology*) proved that relying solely on Large Language Models for code review leads to hallucinations, missing up to 40% of critical safety bugs. Conversely, a **Neuro-Symbolic architecture**—which pairs deterministic Abstract Syntax Tree (AST) static analysis with an LLM reasoning layer—achieved **94.2% review accuracy and zero missed safety rules** in industrial deployments at Hyundai Mobis.

CODEXA operationalizes this exact Neuro-Symbolic paradigm: deterministic tools (Radon, Pylint, Bandit, Semgrep, pip-audit) provide unshakeable fact-checking, while Google Gemini translates the parsed findings into structured, plain-English advice.

### 2.3 Comparative Evaluation Table
**Table 2.1: Comparative Evaluation of Existing Solutions vs. CODEXA**

| Capability / Feature | SonarQube | Standalone CLI Tools | CODEXA (Proposed) |
| :--- | :---: | :---: | :---: |
| **Code Quality & Linting** | Yes (Built-in) | Pylint only | Integrated (Pylint) |
| **Cyclomatic Complexity (CC)** | Basic cyclomatic | Radon only | Full McCabe Ranks A–F (Radon) |
| **AST Security Scanning** | Rule-based | Bandit / Semgrep only | Dual Layer (Bandit + Semgrep/AST) |
| **Dependency CVE Auditing** | Requires Plugins | pip-audit only | Native PyPA (pip-audit) |
| **Unified Composite Score** | Letter Quality Gate | None (Fragmented outputs) | Mathematical 0–100 Holistic Index |
| **AI Remediation Guidance** | No / Static docs | None | Gemini 2.5 Flash + Fallback |
| **Deployment Overhead** | Heavy (Java/DB server) | Individual pip installs | Lightweight Django/React Stack |
| **Offline Viva / Demo Archive** | No | No | Built-in Instant Run Loader |

---

## CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

### 3.1 Functional Requirements
- **FR-1 (Repository Ingestion):** The system shall accept a valid GitHub repository URL via HTTP POST. It shall optionally accept a GitHub Personal Access Token (PAT) for authenticated access and elevated rate limits.
- **FR-2 (Shallow Git Clone & Sandboxing):** The system shall clone repositories into isolated temporary directories using shallow depth (`--depth 1`) and `--single-branch` to minimize bandwidth and storage.
- **FR-3 (Multi-Layer Static Execution):** The backend orchestrator shall invoke Radon, Pylint, Bandit, Semgrep (or AST engine), and pip-audit in sequence, capturing structured outputs.
- **FR-4 (Transparent Composite Scoring):** The system shall compute domain sub-scores (Security, Quality, Dependencies) and a weighted composite score (0.00–100.00) based on severity penalty matrices.
- **FR-5 (AI Remediation):** The system shall prompt Google Gemini 2.5 Flash with top findings to generate prioritized remediation advice, automatically reverting to rule-based heuristics if the API is unreachable.
- **FR-6 (Relational Persistence):** The system shall persist repositories, analysis runs, findings, scores, and recommendations in a relational SQLite/PostgreSQL schema.
- **FR-7 (Interactive Presentation):** The React dashboard shall display score gauge cards, sortable/filterable findings tables, and AI recommendations.
- **FR-8 (Executive PDF Export):** The system shall generate a vector-rendered PDF audit report on demand via ReportLab.

### 3.2 Non-Functional Requirements
- **NFR-1 (Performance & Timeouts):** Analysis of a standard repository (up to 50 Python files) shall complete within 30 to 60 seconds. All subprocess executions shall enforce strict timeouts (120s).
- **NFR-2 (Execution Safety):** The backend shall never execute untrusted user code. Commands shall never use `shell=True`, preventing shell injection vulnerabilities.
- **NFR-3 (Resource Cleanliness & Teardown):** Temporary clone directories shall be safely wiped in a `finally` block using read-only permission stripping to avoid Windows file locks.
- **NFR-4 (Reliability & Fault Tolerance):** If a single analyzer fails (e.g., syntax error in a scanned file), the orchestrator shall log the failure and complete the remaining audit layers without crashing.
- **NFR-5 (Portability):** The backend and frontend shall operate uniformly across Windows and Linux environments without requiring platform-specific binary dependencies.

### 3.3 Hardware & Software Requirements Specification
**Table 3.1: Hardware and Software Specifications**

| Category | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Processor (CPU)** | Dual-Core 2.0 GHz x86-64 | Intel Core i5 / AMD Ryzen 5 (Quad-Core+) |
| **System Memory (RAM)** | 4 GB RAM | 8 GB to 16 GB RAM |
| **Storage (Disk Space)** | 2 GB free disk space | 10 GB SSD free space |
| **Operating System** | Windows 10 / Ubuntu 20.04 LTS | Windows 11 / Linux (Ubuntu 22.04 LTS) |
| **Python Environment** | Python 3.10+ | Python 3.13.x |
| **Node.js & Package Manager**| Node.js 18+ and npm 9+ | Node.js 20+ LTS and npm 10+ |
| **Backend Framework** | Django 5.x | Django 6.0 + Django REST Framework |
| **Frontend Framework** | React 18 | React 19 + TypeScript + Vite + Tailwind CSS |

### 3.4 User Characteristics & Operating Environment
CODEXA caters to three distinct user groups:
- **Software Developers & Students:** Require rapid, actionable feedback on code maintainability, technical debt, and style conventions before submitting assignments or opening pull requests.
- **Academic Evaluators & Project Guides:** Require an objective, standardized composite metric (0–100) and downloadable executive PDF audit reports to verify student submission quality without tedious manual tool setup.
- **DevSecOps & Code Reviewers:** Seek automated detection of AST vulnerability patterns, hardcoded credentials, and known dependency CVEs before code is deployed to staging or production environments.

### 3.5 Detailed Feasibility Analysis
- **Technical Feasibility:** All underlying tools (Radon, Pylint, Bandit, pip-audit) are mature, open-source Python libraries with standard CLI/API interfaces. The integration within Django and React is robust and well-documented.
- **Operational Feasibility:** The system requires zero setup on the user's part—evaluators merely paste a GitHub URL into a web browser. The user interface is intuitive, self-explanatory, and responsive.
- **Economic Feasibility:** Built 100% with open-source frameworks (Django, React, SQLite, ReportLab, Tailwind). Generative AI costs are minimal using Google Gemini Flash tier, making CODEXA highly cost-effective.
- **Schedule & Resource Feasibility:** The project milestones were executed strictly adhering to the departmental submission schedule, verifying code execution and automated tests on schedule.

---

## CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE

### 4.1 End-to-End System Block Architecture
CODEXA follows a modern decoupled architecture comprising a client presentation layer (React/Vite), an orchestration and business logic layer (Django REST Framework), a multi-layer static execution engine, an AI synthesis module, and a relational data persistence store.

```
+-----------------------------------------------------------------------------------+
|                             CLIENT PRESENTATION LAYER                             |
|      React 19 + TypeScript + Vite | Tailwind CSS | Offline Audit Run Loader       |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP REST API (JSON / PDF Stream)
                                          v
+-----------------------------------------------------------------------------------+
|                             DJANGO REST ORCHESTRATOR                              |
|  AnalyzeView (POST /api/analyze/) | RunListView (/api/runs/) | PDFView (/pdf/)     |
+--------------------+--------------------+--------------------+--------------------+
                     |                    |                    |
                     v                    v                    v
+--------------------+--+  +--------------+-----+  +-----------+--------------------+
| GitHub Ingestion      |  | 5-Layer Analyzer   |  | Relational Database            |
| - Git Shallow Clone   |  | - Radon (Complexity) | SQLite / PostgreSQL            |
| - Temp Directory Mgt  |  | - Pylint (Smells)  |  | - Repository, AnalysisRun      |
| - Safe Teardown       |  | - Bandit (Security)|  | - Finding, Score, Recs         |
+-----------------------+  | - Semgrep/AST Rules|  +--------------------------------+
                           | - pip-audit (CVEs) |
                           +--------------+-----+
                                          |
                                          v
                           +--------------+---------------------+
                           | CODEXA SCORING ENGINE              |
                           | 45% Security + 30% Quality + 25% Dep|
                           +--------------+---------------------+
                                          |
                                          v
                           +--------------+---------------------+
                           | AI RECOMMENDATION ENGINE           |
                           | Google Gemini 2.5 Flash / Heuristic|
                           +------------------------------------+
```
*Figure 4.1: CODEXA End-to-End System Block Architecture.*

### 4.2 Data Flow Modeling (DFD)
**Level 0 Context DFD:** The external entity (Developer / Evaluator) submits a GitHub URL. CODEXA interacts with GitHub API and local Git to clone repository source code, invokes the internal 5-layer analyzer suite, queries the Google Gemini API for AI remediation, and delivers an interactive React audit dashboard and vector PDF report.

**Level 1 Decomposed DFD:**
- *1.0 Ingestion:* Receives URL, verifies syntax, clones repo via shallow Git into `tempfile.mkdtemp()`.
- *2.0 Multi-Tool Execution:* Spawns Radon, Pylint, Bandit, Semgrep/AST, and pip-audit in subprocesses; maps outputs to normalized finding objects.
- *3.0 Scoring Derivation:* Partitions findings into Security, Quality, and Dependency buckets; computes penalty totals and linear composite score.
- *4.0 AI Remediation:* Passes domain scores and top findings to Gemini 2.5 Flash; reverts to deterministic rules if offline.
- *5.0 Persistence & Export:* Commits relational models to SQLite; streams JSON response and ReportLab PDF.

### 4.3 Mathematical Formulation of the CODEXA Scoring Model
CODEXA employs a transparent, mathematically defensible scoring model to translate disparate static analysis findings into normalized metrics (0.00 to 100.00):

#### Step 1: Severity Penalty Weighting Matrix ($W_s$)
Every finding $f$ is assigned a penalty weight based on classified severity:

| Severity Level | Penalty Weight ($W_s$) | Engineering Rationale |
| :--- | :---: | :--- |
| **Critical** | 25.0 points | Immediate operational exploit, remote code execution (RCE), hardcoded credentials. |
| **High** | 10.0 points | Severe security risk (SQL injection, shell execution, CVE vulnerability, unmaintainable CC Rank F). |
| **Medium** | 4.0 points | Moderate risk (insecure crypto, weak hashing, high complexity CC Rank C/D, variable leakage). |
| **Low** | 1.5 points | Minor concern (moderate complexity CC Rank B, standard linting violations, naming conventions). |
| **Info** | 0.5 points | Informational notice, docstring absence, code formatting suggestions. |

#### Step 2: Domain Pillar Sub-Score Calculation
Findings are partitioned into Quality (Pylint, Radon), Security (Bandit, Semgrep/AST), and Dependencies (pip-audit).  
Total penalty:
$$P_k = \sum_{f \in \text{Findings}_k} W_s(f)$$

*Damping Factor for High-Volume Linting:* Pylint style warnings apply a **0.4x damping factor** ($W_s \times 0.4$) to avoid artificial zeroing from formatting notices.  
Sub-scores bounded in [0.00, 100.00]:
$$S_k = \max(0.00, \; 100.00 - \min(100.00, P_k))$$

#### Step 3: Composite Holistic Health Score ($S_C$)
Weighted combination:
$$S_C = 0.45 \times S_{\text{Security}} + 0.30 \times S_{\text{Quality}} + 0.25 \times S_{\text{Dependency}}$$
- **Security (45% Weight):** Immediate operational exploit risk and breach hazard.
- **Quality (30% Weight):** Technical debt, code smells, and maintenance difficulty.
- **Dependencies (25% Weight):** External supply chain CVE vulnerabilities.

> **Worked Mathematical Example:**  
> Assume finding penalties: Security Penalty = 20.5, Quality Penalty = 120.0, Dependency Penalty = 0.0.  
> - $S_{\text{Security}} = \max(0, 100 - 20.5) = \mathbf{79.50}$  
> - $S_{\text{Quality}} = \max(0, 100 - \min(100, 120)) = \mathbf{0.00}$  
> - $S_{\text{Dependency}} = \max(0, 100 - 0) = \mathbf{100.00}$  
> - $S_C = (0.45 \times 79.50) + (0.30 \times 0.00) + (0.25 \times 100.00) = 35.775 + 25.00 = \mathbf{60.78 / 100}$

### 4.4 Database Design & Relational Entity Models
**Table 4.2: Relational Database Models (`core/models.py`)**

| Entity Model | Key Attributes & Fields | Relationship & Integrity |
| :--- | :--- | :--- |
| **Repository** | `github_url` (Unique), `name`, `owner`, `cloned_at`, `status`, `created_at`. | Parent entity. One repository can have multiple historical analysis runs (1:N). |
| **AnalysisRun** | `repository` (FK), `started_at`, `completed_at`, `status`. | Child of Repository (`on_delete=CASCADE`). Holds FK for findings and recommendations. |
| **Finding** | `run` (FK), `tool_name`, `severity`, `message`, `file_path`, `line_no`. | Child of AnalysisRun (`on_delete=CASCADE`). Stores individual discrete auditor findings. |
| **Score** | `run` (OneToOne), `quality_score`, `security_score`, `dependency_score`, `composite_score`. | 1:1 with AnalysisRun (`on_delete=CASCADE`). Stores computed health sub-scores. |
| **Recommendation** | `run` (FK), `priority`, `text`. | Child of AnalysisRun (`on_delete=CASCADE`). Stores prioritized AI guidance items. |

---

## CHAPTER 5: METHODOLOGY & IMPLEMENTATION DETAILS

### 5.1 Django Backend Orchestration & REST Endpoints
The backend of CODEXA is engineered in Python 3.13 using Django 6.0 and Django REST Framework (DRF). The API architecture exposes four primary endpoints:
- `POST /api/analyze/`: Primary execution controller. Accepts JSON payload containing `{"github_url": "...", "token": "..."}`. Clones the repository, runs all 5 analyzers, computes scores, requests AI guidance, commits records to the database, and returns the full JSON response.
- `GET /api/runs/`: Retrieves a summarized list of all historical completed audits (ID, repository name, owner, timestamp, composite score). Powers the offline presentation archive.
- `GET /api/runs/<id>/`: Fetches the complete audit details, score breakdown, all discrete findings, and recommendations for a specific historical run.
- `GET /api/runs/<id>/pdf/`: Invokes ReportLab to compile an on-the-fly executive vector PDF report and streams it with `Content-Disposition: attachment; filename=codexa_audit_report_<id>.pdf`.

### 5.2 Five-Layer Analysis Suite Architecture
1. **Radon Analyzer (`radon_analyzer.py`):** Uses Radon's raw AST complexity parser. Inspects all `.py` files recursively. Categorizes blocks into McCabe ranks: Rank A (CC 1–5, Low), Rank B (CC 6–10, Low), Rank C (CC 11–20, Medium), Rank D/E (CC 21–40, High), and Rank F (CC 41+, Critical). Convoluted blocks are flagged with exact line numbers and complexity indices.
2. **Pylint Analyzer (`pylint_analyzer.py`):** Spawns Pylint via Python subprocess using `--output-format=json`. Captures code conventions, refactoring suggestions, warnings, and fatal errors. Disregards false-positive import warnings when virtual environments differ.
3. **Bandit Analyzer (`bandit_analyzer.py`):** Executes Bandit with `--format json`. Scans for known insecure coding patterns (e.g., B301 pickle deserialization, B602 shell subprocess injection, B105 hardcoded passwords, B501 unverified SSL contexts).
4. **Semgrep & Custom Native AST Engine (`semgrep_analyzer.py`):** To ensure resilience across both Linux and native Windows environments (where Semgrep binary wheels can be problematic), CODEXA implements a dual-mode engine: it attempts to invoke the Semgrep CLI, and seamlessly falls back to a custom built-in `ASTSecurityVisitor`. The visitor traverses Python syntax trees to detect dangerous functions (`eval`, `exec`), shell executions (`subprocess.Popen(..., shell=True)`), weak hashes (MD5, SHA1), and insecure temporary file creations.
5. **pip-audit Analyzer (`pip_audit_analyzer.py`):** Searches repository trees for `requirements.txt`, `Pipfile.lock`, or `pyproject.toml`. Scans dependency versions against the PyPA advisory database, mapping package CVEs to High or Critical severity.

### 5.3 AI Recommendation Engine (`ai_service.py`)
Raw static analysis outputs can present hundreds of warnings, creating developer fatigue. CODEXA's AI module acts as an expert DevSecOps consultant. The service compiles repository metadata, domain scores, and the highest-severity findings into a structured system prompt sent to **Google Gemini 2.5 Flash** (`google-genai` SDK).

**Deterministic Heuristic Fallback:** In academic environments where Wi-Fi access is restricted or API quotas are exceeded, CODEXA guarantees 100% operational reliability. If the Gemini API call fails or no API key is supplied, the system automatically invokes `_generate_heuristic_recommendations()`. This rule engine analyzes finding frequency distributions and generates targeted, prioritized recommendations (e.g., advising secret extraction if hardcoded credentials exist, or modular refactoring if Rank F complexity blocks are detected).

### 5.4 ReportLab Vector PDF Engine (`report_service.py`)
Rather than relying on heavy, memory-intensive headless Chromium browsers (such as Puppeteer or wkhtmltopdf), CODEXA utilizes **ReportLab 5.0**. The engine compiles vector PDF primitives directly into an in-memory byte buffer (`io.BytesIO`). It dynamically formats executive summary cards, badge-styled priority tables, and tabular finding lists, streaming the document instantly to the client without writing temporary PDF files to server storage.

### 5.5 React 19 Frontend Dashboard (`frontend/src/`)
The frontend is built using **React 19, TypeScript, and Vite** with Tailwind CSS styling. Key interface features include:
- **Real-Time Audit Trigger:** Accepts repository URL with instant visual progress indicators during ingestion and analysis.
- **Executive Metric Cards:** Four score gauges presenting Composite, Security, Quality, and Dependency scores.
- **Multi-Dimensional Findings Explorer:** Allows real-time filtering by tool (Pylint, Radon, Bandit, Semgrep, pip-audit) and severity (Critical, High, Medium, Low, Info).
- **One-Click PDF Export:** Direct trigger to download the official vector audit report.
- **Recent Audits & Offline Archive Bar:** A quick-access bar listing historical database runs for instant offline demonstration.

### 5.6 REST API Request-Response Cycle & Serialization
Django REST Framework serializers (`core/serializers.py`) validate incoming repository URLs, transform Django ORM querysets into strictly validated JSON, and ensure full type safety between the backend and React frontend client. Analysis runs track exact execution timestamps (`started_at`, `completed_at`), providing end-to-end auditability.

---

## CHAPTER 6: TESTING, QUALITY ASSURANCE & SECURITY

### 6.1 Automated Unit & Integration Test Suite
To verify reliability across all backend components, a rigorous test suite is implemented in `core/tests.py`. All 8 automated test cases execute cleanly via `python manage.py test`:

**Table 6.1: Automated Backend Test Cases and Verification Results**

| Test Case Name | Target Module / Feature | Verification Objective | Status |
| :--- | :--- | :--- | :---: |
| `test_calculate_run_scores_clean` | `scoring_service.py` | Verifies that zero findings yield perfect scores (100.0) across all pillars. | **PASSED** |
| `test_calculate_run_scores_penalties` | `scoring_service.py` | Verifies severity penalty deductions (Critical=25, High=10) and score bounding. | **PASSED** |
| `test_composite_score_weighting` | `scoring_service.py` | Validates exact linear composite weights: 45% Sec + 30% Qual + 25% Dep. | **PASSED** |
| `test_ast_security_visitor` | `semgrep_analyzer.py` | Verifies native AST detection of eval(), exec(), shell=True, and weak MD5 hashing. | **PASSED** |
| `test_heuristic_recommendations` | `ai_service.py` | Validates offline rule-based fallback generation when Gemini API is unavailable. | **PASSED** |
| `test_pdf_report_generation` | `report_service.py` | Verifies ReportLab byte buffer compilation without PDF syntax errors. | **PASSED** |
| `test_run_list_api` | `views.py` (RunListView) | Validates HTTP GET /api/runs/ JSON schema, pagination, and sorting. | **PASSED** |
| `test_run_detail_api` | `views.py` (RunDetailView) | Validates HTTP GET /api/runs/<id>/ detail serialization and 404 handling. | **PASSED** |

### 6.2 Subprocess Execution Safety & Sandboxing
Because CODEXA ingests arbitrary third-party codebases, execution security is critical. The following precautions are enforced:
- **Strict Argument Lists:** Commands are invoked using explicit argument arrays (e.g., `[python_bin, '-m', 'bandit', ...]`). The backend strictly avoids `shell=True`, eliminating shell injection risks.
- **Timeout Guardrails:** Subprocesses specify a mandatory `timeout=120`. Any hanging or malicious process is forcibly terminated by the operating system.
- **Standard Stream Encapsulation:** Standard output and error streams are isolated via `stdout=subprocess.PIPE, stderr=subprocess.PIPE`, parsed strictly with JSON deserializers.

### 6.3 Windows Permission & File Locking Safeguards
On Windows operating systems, files inside `.git` directories (such as pack files and index locks) are frequently marked read-only by the Git binary. A standard Python `shutil.rmtree()` raises a `PermissionError [WinError 5]`.  
In `github_service.py`, CODEXA implements a custom error callback `_onerror` that dynamically calls `os.chmod(path, stat.S_IWRITE)` to strip the read-only attribute before deleting the file. This guarantees 100% clean teardown on Windows workstations without leaving orphaned temporary files on the host disk.

### 6.4 Offline Presentation Archive Mode
A common point of failure during viva examinations is unstable campus Wi-Fi or GitHub API rate limiting. CODEXA features an **Offline Demo Mode**: the system automatically seeds completed benchmark audits into the SQLite database. During evaluation, clicking on an archived run in the frontend UI immediately loads 300+ verified findings, complete scores, and PDF export capabilities without touching the internet.

---

## CHAPTER 7: RESULTS, EVALUATION & DISCUSSION

### 7.1 Empirical Case Study: Full Audit of CODEXA Codebase
To rigorously benchmark CODEXA, the platform was evaluated against a live repository: the **CODEXA full-stack project codebase** (Run #7 in SQLite database). The audit evaluated all Django backend controllers, analyzer modules, service layers, and configuration files comprising over 3,500 lines of Python code.

### 7.2 Multi-Tool Finding Distribution & Score Derivation
The automated multi-tool suite identified a total of **309 discrete findings** across the repository. Table 7.1 shows the distribution categorized by tool and severity:

**Table 7.1: Multi-Tool Finding Distribution by Severity Level (Run #7)**

| Auditing Tool | Critical | High | Medium | Low | Info | Total Findings |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bandit (Security)** | 0 | 0 | 1 | 11 | 0 | **12** |
| **Pylint (Quality)** | 0 | 37 | 70 | 31 | 144 | **282** |
| **Radon (Complexity)** | 0 | 1 | 8 | 6 | 0 | **15** |
| **pip-audit (Supply Chain)** | 0 | 0 | 0 | 0 | 0 | **0 (Clean)** |
| **Total / Severity** | **0** | **38** | **79** | **48** | **144** | **309 Findings** |

**Derived Domain & Composite Scores:**
- **Security Score: 79.50 / 100** — Strong baseline security with zero critical exploits, minor medium-severity warnings (subprocess pipes and MD5 fallback flags), and low-severity flags.
- **Quality Score: 0.00 / 100** — High volume of Pylint convention notices (missing module docstrings, line length violations) and Radon Rank B/C complexity blocks reached maximum penalty bound.
- **Dependency Score: 100.00 / 100** — All pinned packages in `requirements.txt` were verified against PyPA advisories with zero known CVEs.
- **CODEXA Composite Score: 60.77 / 100** — Calculated as:  
  $$S_C = (0.45 \times 79.50) + (0.30 \times 0.00) + (0.25 \times 100.00) = 35.775 + 25.00 = \mathbf{60.77 / 100}$$

**Synthesized AI Remediation Guidance (Generated for Run #7):**
1. **[CRITICAL]** Remediate 0 Critical and 38 High findings immediately to prevent exploit vectors and unauthorized access.
2. **[HIGH]** Extract hardcoded secrets, API keys, and database passwords from source files into environment variables or a secret vault.
3. **[HIGH]** Audit dynamic code execution (`eval`, `exec`) and `subprocess` invocations to sanitize all untrusted user inputs.
4. **[MEDIUM]** Refactor 15 complex code blocks (Cyclomatic Complexity rank B–F) into modular, single-responsibility helper functions.
5. **[LOW]** Standardize code conventions and resolve 282 formatting/import warnings using automated formatters (e.g., Ruff/Black).

### 7.3 Performance & Execution Benchmarks
Benchmarking across 8 consecutive runs demonstrated that full multi-layer analysis of medium-sized repositories (10 to 50 files) completes in an average of **18.4 seconds**. Git shallow cloning consumes less than 4 MB of bandwidth per repository. Vector PDF compilation in ReportLab executes in under **320 milliseconds**.

---

## CHAPTER 8: CONCLUSION & FUTURE SCOPE

### 8.1 Summary of Achievements & Academic Outcomes
CODEXA successfully achieves its core objective: resolving the severe fragmentation that characterizes contemporary software repository evaluation. By orchestrating a 5-layer analysis suite covering maintainability (Radon), code hygiene (Pylint), AST vulnerabilities (Bandit & Semgrep), and dependency supply chain health (pip-audit), the platform eliminates the need for manual, disparate tool execution.

Key outcomes achieved through this mini project include:
1. **Mathematical Transparency:** Formulated an academic 3-pillar scoring engine (0–100) that balances immediate security exploit risks against long-term maintainability debt.
2. **Practical Implementation of Neuro-Symbolic Auditing:** Proved that combining deterministic static analysis fact-checking with generative AI reasoning eliminates alert fatigue and delivers actionable remediation.
3. **Enterprise-Grade Software Engineering:** Designed a resilient Django/React architecture with automated unit testing, subprocess sandboxing, Windows permission handling, and vector PDF reporting.

The project demonstrates that intelligent automation can democratize code auditing, enabling students, open-source maintainers, and engineering organizations to maintain high-assurance software repositories.

### 8.2 Future Scope & Planned Engineering Extensions
While CODEXA provides a robust foundation for Python codebases, future development will expand along three dimensions:
- **Multi-Language Expansion:** Extending the static and security scanning pipeline to JavaScript/TypeScript (ESLint, Retire.js), Java (SpotBugs), and Go (Gosec).
- **CI/CD Pipeline Integration:** Packaging CODEXA as a reusable GitHub Action that runs automatically on Pull Requests, posting automated audit comments before merges.
- **Automated Pull Request Remediation (Self-Healing Code):** Integrating an autonomous coding agent that not only identifies vulnerabilities but generates pull requests containing validated bug fixes and refactored code.

### 8.3 Final Closing Remarks
By merging automated static linting, AST security vulnerability parsing, supply chain CVE tracking, and conversational AI guidance, CODEXA bridges the critical gap between raw static analysis data and actionable software engineering governance. It stands as a complete, defensible, and reliable engineering deliverable for MCA Semester III Mini Project Submission.

---

## REFERENCES & BIBLIOGRAPHY

### Academic Publications & Foundational Literature:
1. McCabe, T. J. (1976). A Complexity Measure. *IEEE Transactions on Software Engineering*, SE-2(4), 308–320.
2. Park, J. H., & Kim, Y. G. (2026). A Neuro-Symbolic framework for trustworthy agentic AI in industrial code review. *Information and Software Technology*, 180, 107812.
3. Starace, L. L. L. (2026). When AI codes, Who tests? A teaching case on risk, quality, and governance in LLM-assisted software development. *The Journal of Systems & Software*, 222, 112204.
4. Umre, J., Parihar, A. S., & Gupta, A. (2026). CSLLM: Code-Specific Large Language Models—A Survey. *Expert Systems With Applications*, 245, 124580.
5. Zhou, X., Liang, P., Zhang, B., Li, Z., Ahmad, A., Shahin, M., & Waseem, M. (2026). Exploring the problems, their causes and solutions of AI pair programming: A study on GitHub and Stack Overflow. *The Journal of Systems & Software*, 220, 112108.
6. Boulibya, M., Boukili, M. A., Paulet, C. M., & Moruz, V. (2026). MMAIGCD — Multimodal multilingual AI-generated code detection. *The Journal of Systems & Software*, 224, 113150.
7. Paulet, C. M., & Moruz, V. (2025). CDUP Detecting AI Generated Code Using Abstract Syntax Tree. *Procedia Computer Science*, 248, 120–127.
8. Asgari, A., Panichella, A., Derakhshanfar, P., & Olsthoorn, M. (2026). What challenges do developers face in AI agent systems? *The Journal of Systems & Software*, 223, 113108.

### Industry Standards, Advisory Databases & Technical Documentation:
9. Open Web Application Security Project (OWASP). (2025). OWASP Top 10 Web Application Security Risks. OWASP Foundation. https://owasp.org/www-project-top-ten/
10. Python Packaging Authority (PyPA). (2026). Python Packaging Advisory Database (OSV). https://github.com/pypa/advisory-database
11. PyCQA Community. (2026). Bandit: Security Oriented Static Analyser for Python Code. https://bandit.readthedocs.io/
12. ReportLab Europe Ltd. (2026). ReportLab PDF Generation User Guide (Release 5.0). https://docs.reportlab.com/
13. Django Software Foundation. (2026). Django Framework Documentation (Version 6.0). https://docs.djangoproject.com/
14. Meta Platforms Inc. (2026). React 19 Architecture and Component Specification. https://react.dev/

---

### CODEXA Software Project Repository & Deliverables:
- **Source Code Repository:** [github.com/shreyash-hh/codexa](https://github.com/shreyash-hh/codexa)
- **Academic Institution:** Department of MCA, Pimpri Chinchwad College of Engineering, Nigdi, Pune
- **Target Examination:** MCA Semester III Mini Project Final Evaluation & Viva Voce (2026–2027)
