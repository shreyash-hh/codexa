# CODEXA

An automated, AI-augmented code analysis and security auditing platform.

## 🛠 Tech Stack

- **Frontend:** React.js, TypeScript, Tailwind CSS
- **Backend:** Django, Python
- **Database:** SQLite
- **Static Code Analysis:** Radon, Pylint
- **Security Analysis:** Bandit, Semgrep
- **Dependency Analysis:** pip-audit
- **AI Module:** Gemini API
- **Reporting:** ReportLab
- **Version Control:** Git & GitHub

## 📂 Project Architecture

- **`frontend/`**: React + TypeScript + Tailwind CSS dashboard UI for file upload, analysis visualization, and report downloads.
- **`backend/`**: Django REST framework core handling analysis orchestration, tool invocation, database logging, and ReportLab PDF generation.
- **`ai_engine/`**: Gemini API integration for code explanation, vulnerability remediation tips, and executive summary generation.
- **`analyzers/`**: Static, security, and dependency audit runners (Radon, Pylint, Bandit, Semgrep, pip-audit).
