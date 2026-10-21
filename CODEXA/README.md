# CODEXA: Intelligent Software Repository Quality & Security Auditing Platform

CODEXA is an automated, AI-augmented code analysis and security auditing platform designed to evaluate software repository health, detect vulnerabilities, measure maintainability, and provide prioritized remediation recommendations.

---

## 🛠 Tech Stack

- **Frontend:** React 19, TypeScript, Tailwind CSS, Lucide Icons, Vite
- **Backend:** Django 6.0, Django REST Framework, Python 3.10+
- **Database:** SQLite (Relational ORM, PostgreSQL-compatible)
- **Static Code Analysis:** Radon (Cyclomatic Complexity), Pylint (Code Smells & PEP 8)
- **Security Analysis:** Bandit (AST Security Scanner), Semgrep / AST Security Engine
- **Dependency & Supply Chain Analysis:** pip-audit (PyPA Advisory Database)
- **AI Recommendation Engine:** Google Gemini API (2.5 Flash) with Deterministic Heuristic Fallback
- **Executive Reporting:** ReportLab (Vector PDF Generation)
- **Version Control:** Git & GitPython

---

## 📂 Project Architecture

```
mini project/
├── CODEXA/
│   ├── backend/             # Django settings, routing, ASGI/WSGI
│   │   ├── settings.py      # CORS, REST Framework, DB configuration
│   │   └── urls.py          # Root API routing
│   ├── core/                # Core analysis & orchestration application
│   │   ├── analyzers/       # 5-layer analyzer suite
│   │   │   ├── bandit_analyzer.py      # AST security scanning
│   │   │   ├── pip_audit_analyzer.py   # CVE vulnerability scanning
│   │   │   ├── pylint_analyzer.py      # Static linting & smells
│   │   │   ├── radon_analyzer.py       # Cyclomatic complexity
│   │   │   └── semgrep_analyzer.py     # Semantic AST security engine
│   │   ├── services/        # Business logic & integrations
│   │   │   ├── ai_service.py           # Gemini 2.5 Flash / Heuristic engine
│   │   │   ├── github_service.py       # Git cloning & metadata fetch
│   │   │   ├── report_service.py       # ReportLab PDF executive generation
│   │   │   └── scoring_service.py      # 3-pillar composite scoring engine
│   │   ├── models.py        # Repository, AnalysisRun, Finding, Score, Recommendation
│   │   ├── serializers.py   # REST API serializers
│   │   ├── views.py         # AnalyzeView, RunListView, RunDetailView, PDFView
│   │   ├── urls.py          # API endpoint paths
│   │   └── tests.py         # Full test suite (8 test cases)
│   ├── frontend/            # React 19 + TypeScript + Vite UI
│   │   ├── src/
│   │   │   ├── App.tsx      # Interactive dashboard, filters, history loader
│   │   │   ├── index.css    # Tailwind CSS design system & dark mode
│   │   │   └── main.tsx     # React DOM root
│   │   └── package.json     # Node dependencies & build scripts
│   ├── requirements.txt     # Python backend dependencies
│   ├── manage.py            # Django management CLI
│   └── db.sqlite3           # Pre-seeded SQLite database with sample audits
└── MINI_PROJECT_VIVA_AND_EXPLANATION_GUIDE.md # Complete viva defense guide
```

---

## 🚀 Getting Started

### 1. Backend Setup
From the `mini project/CODEXA` directory:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate

# 3. (Optional) Run automated tests
python manage.py test

# 4. Start the Django API server
python manage.py runserver 127.0.0.1:8000
```
The backend API is now live at `http://127.0.0.1:8000/`.

---

### 2. Frontend Setup
In a new terminal, navigate to `mini project/CODEXA/frontend`:
```bash
# 1. Install npm dependencies
npm install

# 2. Start the Vite development server
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze/` | Accepts `{ github_url, token? }`, clones repo, executes 5-layer audit, returns complete scores & findings. |
| `GET` | `/api/runs/` | Lists recent completed analysis runs for quick access and historical comparison. |
| `GET` | `/api/runs/<id>/` | Retrieves complete analysis details, findings, scores, and metadata for a specific run. |
| `GET` | `/api/runs/<id>/pdf/` | Generates and downloads an executive ReportLab PDF audit report. |

---

## 📊 CODEXA Multi-Dimensional Scoring Engine

The CODEXA composite score is calculated using a transparent weighted formula:

$$\text{Composite Score} = 0.45 \times \text{Security} + 0.30 \times \text{Quality} + 0.25 \times \text{Dependency}$$

- **Security (45%):** Penalties from Bandit AST vulnerabilities and Semgrep rules.
- **Quality (30%):** Penalties from Pylint style violations and Radon Cyclomatic Complexity (Rank B–F).
- **Dependencies (25%):** Penalties from pip-audit known CVEs in requirement manifests.

---

## 👨‍🎓 Candidate Details

- **Student:** Shreyash Anilrao Thakare (PRN: 125M1H048)
- **Department:** Department of Master of Computer Applications (MCA)
- **Guide:** Dr. Avinash Chormale
- **Institute:** Pimpri Chinchwad College of Engineering (PCCOE), Nigdi, Pune – 411044
- **Academic Year:** 2026 – 2027
