import os
import sys
import json
import logging
import subprocess
from typing import List, Dict, Any, Optional
from core.models import AnalysisRun, Finding

logger = logging.getLogger(__name__)

SEVERITY_MAP = {
    'error': 'high',
    'warning': 'medium',
    'info': 'low',
    'inventory': 'info'
}


def find_semgrep_executable(python_executable: Optional[str] = None) -> str:
    """
    Finds semgrep executable in Python virtual environment or system PATH.
    """
    python_bin = python_executable or sys.executable
    venv_dir = os.path.dirname(python_bin)
    
    # Windows: venv\Scripts\semgrep.exe
    win_semgrep = os.path.join(venv_dir, "semgrep.exe")
    if os.path.exists(win_semgrep):
        return win_semgrep
        
    # Unix: venv/bin/semgrep
    unix_semgrep = os.path.join(venv_dir, "semgrep")
    if os.path.exists(unix_semgrep):
        return unix_semgrep

    return "semgrep"


def run_semgrep(target_dir: str, python_executable: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Executes Semgrep security analysis with JSON output on target directory.
    """
    if not os.path.exists(target_dir):
        logger.error(f"Target directory does not exist: {target_dir}")
        return []

    semgrep_bin = find_semgrep_executable(python_executable)

    # Exclude common non-source directories
    exclude_args = [
        "--exclude", "venv",
        "--exclude", ".venv",
        "--exclude", "node_modules",
        "--exclude", ".git",
        "--exclude", "__pycache__",
        "--exclude", "dist",
        "--exclude", "build"
    ]

    cmd = [
        semgrep_bin,
        "scan",
        "--config", "p/python",
        "--json",
        "--disable-version-check",
        "--metrics=off",
        "-q",
        *exclude_args,
        target_dir
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
            output = result.stderr.strip()
            if not output:
                return []

        # Find valid JSON object start
        json_start = output.rfind('{"version"')
        if json_start == -1:
            json_start = output.find('{')
        if json_start != -1:
            output = output[json_start:]

        data = json.loads(output)
        raw_results = data.get('results', [])
        findings = []

        for item in raw_results:
            extra = item.get('extra', {})
            raw_severity = extra.get('severity', 'WARNING').lower()
            severity = SEVERITY_MAP.get(raw_severity, 'medium')
            check_id = item.get('check_id', '')
            message_text = extra.get('message', '')
            formatted_msg = f"[{check_id}] {message_text}" if check_id else message_text

            raw_path = item.get('path', '')
            if os.path.isabs(raw_path):
                rel_path = os.path.relpath(raw_path, target_dir)
            else:
                rel_path = raw_path

            start_line = item.get('start', {}).get('line')

            findings.append({
                'tool_name': 'semgrep',
                'severity': severity,
                'message': formatted_msg,
                'file_path': rel_path.replace('\\', '/'),
                'line_no': start_line,
            })

        return findings

    except subprocess.TimeoutExpired:
        logger.error(f"Semgrep execution timed out for {target_dir}")
        return [{
            'tool_name': 'semgrep',
            'severity': 'high',
            'message': 'Semgrep analysis timed out after 120 seconds.',
            'file_path': '',
            'line_no': None
        }]
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Semgrep JSON output: {e}. Raw: {output[:200] if 'output' in locals() else ''}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error running Semgrep: {e}")
        return []


def analyze_and_save_semgrep(run: AnalysisRun, target_dir: str) -> List[Finding]:
    """
    Runs Semgrep on target_dir, persists findings tagged with tool_name='semgrep',
    and returns created Finding instances.
    """
    raw_findings = run_semgrep(target_dir)
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
