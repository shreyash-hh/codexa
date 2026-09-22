import os
import sys
import json
import logging
import subprocess
from typing import List, Dict, Any, Optional
from core.models import AnalysisRun, Finding

logger = logging.getLogger(__name__)

SEVERITY_MAP = {
    'high': 'high',
    'medium': 'medium',
    'low': 'low',
    'critical': 'critical',
    'info': 'info'
}


def run_bandit(target_dir: str, python_executable: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Executes Bandit security scanner recursively over target_dir and returns parsed findings.
    """
    if not os.path.exists(target_dir):
        logger.error(f"Target directory does not exist: {target_dir}")
        return []

    python_bin = python_executable or sys.executable

    # Exclude common non-source and virtual environment directories
    excluded_paths = "*/venv/*,*/.venv/*,*/node_modules/*,*/.git/*,*/__pycache__/*,*/dist/*,*/build/*"

    cmd = [
        python_bin,
        "-m",
        "bandit",
        "-r",
        target_dir,
        "-f",
        "json",
        "-x",
        excluded_paths,
        "-q"
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=target_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout.strip()
        if not output:
            # Fallback if bandit output printed to stderr or empty
            output = result.stderr.strip()
            if not output:
                return []

        # Find start of JSON object
        json_start = output.find('{')
        if json_start != -1:
            output = output[json_start:]

        data = json.loads(output)
        raw_results = data.get('results', [])
        findings = []

        for item in raw_results:
            raw_severity = item.get('issue_severity', 'medium').lower()
            severity = SEVERITY_MAP.get(raw_severity, 'medium')
            test_id = item.get('test_id', '')
            issue_text = item.get('issue_text', '')
            confidence = item.get('issue_confidence', 'MEDIUM')
            formatted_msg = f"[{test_id}][Confidence: {confidence}] {issue_text}" if test_id else issue_text

            raw_path = item.get('filename', '')
            if os.path.isabs(raw_path):
                rel_path = os.path.relpath(raw_path, target_dir)
            else:
                rel_path = raw_path

            findings.append({
                'tool_name': 'bandit',
                'severity': severity,
                'message': formatted_msg,
                'file_path': rel_path.replace('\\', '/'),
                'line_no': item.get('line_number'),
            })

        return findings

    except subprocess.TimeoutExpired:
        logger.error(f"Bandit execution timed out for {target_dir}")
        return [{
            'tool_name': 'bandit',
            'severity': 'high',
            'message': 'Bandit security scan timed out after 120 seconds.',
            'file_path': '',
            'line_no': None
        }]
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Bandit JSON output: {e}. Raw: {result.stdout[:200]}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error running Bandit: {e}")
        return []


def analyze_and_save_bandit(run: AnalysisRun, target_dir: str) -> List[Finding]:
    """
    Runs Bandit on target_dir, creates Finding instances in DB associated with run,
    and returns created Finding objects.
    """
    raw_findings = run_bandit(target_dir)
    created_findings = []

    for item in raw_findings:
        finding = Finding(
            run=run,
            tool_name=item['tool_name'],
            severity=item['severity'],
            message=item['message'],
            file_path=item['file_path'],
            line_no=item['line_no']
        )
        created_findings.append(finding)

    if created_findings:
        Finding.objects.bulk_create(created_findings)

    return created_findings
