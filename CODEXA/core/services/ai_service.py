import os
import json
import logging
from typing import List, Dict, Any, Optional
from core.models import AnalysisRun, Finding, Score, Recommendation

logger = logging.getLogger(__name__)


def generate_heuristic_recommendations(run: AnalysisRun, findings: List[Finding], score: Optional[Score] = None) -> List[Dict[str, str]]:
    """
    Generates deterministic, actionable security and quality recommendations
    when Gemini API key is not configured or during offline execution.
    """
    recommendations = []
    tools_seen = {f.tool_name for f in findings}
    severities = [f.severity.lower() for f in findings]

    # Security recommendations
    if 'critical' in severities or 'high' in severities:
        crit_count = severities.count('critical')
        high_count = severities.count('high')
        recommendations.append({
            'priority': 'critical',
            'text': f"Remediate {crit_count} Critical and {high_count} High security findings immediately to prevent exploit vectors and unauthorized access."
        })

    if 'bandit' in tools_seen:
        bandit_findings = [f for f in findings if f.tool_name == 'bandit']
        if any('hardcoded' in f.message.lower() or 'password' in f.message.lower() for f in bandit_findings):
            recommendations.append({
                'priority': 'high',
                'text': "Extract hardcoded secrets, API keys, and database passwords from source files into environment variables or a secure secret manager."
            })
        if any('subprocess' in f.message.lower() or 'eval' in f.message.lower() for f in bandit_findings):
            recommendations.append({
                'priority': 'high',
                'text': "Audit dynamic code execution (`eval`, `exec`) and `subprocess` invocations to sanitize all untrusted user inputs."
            })

    if 'pip-audit' in tools_seen:
        pip_findings = [f for f in findings if f.tool_name == 'pip-audit']
        if pip_findings:
            recommendations.append({
                'priority': 'high',
                'text': f"Upgrade {len(pip_findings)} vulnerable dependency package(s) identified in requirement manifests to patched versions."
            })

    if 'radon' in tools_seen:
        radon_findings = [f for f in findings if f.tool_name == 'radon']
        if radon_findings:
            recommendations.append({
                'priority': 'medium',
                'text': f"Refactor {len(radon_findings)} complex code block(s) (Cyclomatic Complexity rank B–F) into modular, single-responsibility helper functions."
            })

    if 'pylint' in tools_seen:
        pylint_findings = [f for f in findings if f.tool_name == 'pylint']
        if len(pylint_findings) > 10:
            recommendations.append({
                'priority': 'low',
                'text': f"Standardize code conventions and resolve {len(pylint_findings)} formatting/import warnings using automated linters (e.g., Ruff/Black)."
            })

    if not recommendations:
        recommendations.append({
            'priority': 'low',
            'text': "Repository demonstrates strong code hygiene and security posture. Maintain automated continuous integration scanning."
        })

    return recommendations


def generate_gemini_recommendations(run: AnalysisRun) -> List[Recommendation]:
    """
    Sends consolidated findings and metrics to Gemini API for prioritized,
    expert-level remediation guidance, falling back to heuristic engine if needed.
    """
    findings = list(run.findings.all())
    score = getattr(run, 'score', None)
    
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    raw_recs = []

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            # Summarize top findings for prompt efficiency
            findings_summary = [
                {
                    "tool": f.tool_name,
                    "severity": f.severity,
                    "file": f.file_path,
                    "line": f.line_no,
                    "message": f.message[:150]
                }
                for f in findings[:40] # cap sample
            ]

            prompt = f"""
You are CODEXA AI, a Senior DevSecOps & Security Architect.
Analyze the following code analysis findings and health scores for repository '{run.repository.name}':

Health Scores:
- Composite Score: {score.composite_score if score else 'N/A'}/100
- Quality Score: {score.quality_score if score else 'N/A'}/100
- Security Score: {score.security_score if score else 'N/A'}/100
- Dependency Score: {score.dependency_score if score else 'N/A'}/100

Total Findings: {len(findings)}
Sample Findings:
{json.dumps(findings_summary, indent=2)}

Task: Provide 3 to 6 prioritized, concrete, and highly actionable remediation recommendations.
Output MUST be a valid JSON array of objects with exact keys:
[
  {{
    "priority": "critical" | "high" | "medium" | "low",
    "text": "Specific, actionable remediation instruction..."
  }}
]
Do not include markdown fences, return ONLY the raw JSON array.
"""

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )

            text_resp = response.text.strip()
            if text_resp.startswith("```"):
                lines = text_resp.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                text_resp = "\n".join(lines).strip()

            parsed = json.loads(text_resp)
            if isinstance(parsed, list):
                raw_recs = parsed
        except Exception as e:
            logger.warning(f"Gemini API invocation encountered an issue, using fallback heuristic recommendations: {e}")
            raw_recs = []

    if not raw_recs:
        raw_recs = generate_heuristic_recommendations(run, findings, score)

    # Persist recommendation rows in DB
    created_recs = []
    for item in raw_recs:
        priority = item.get('priority', 'medium').lower()
        if priority not in ['low', 'medium', 'high', 'critical']:
            priority = 'medium'
        rec = Recommendation(
            run=run,
            text=item.get('text', ''),
            priority=priority
        )
        created_recs.append(rec)

    if created_recs:
        Recommendation.objects.bulk_create(created_recs)

    return created_recs
