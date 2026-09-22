import os
import sys
import json
import logging
import subprocess
from typing import List, Dict, Any, Optional
from core.models import AnalysisRun, Finding

logger = logging.getLogger(__name__)

SEVERITY_MAP = {
    'fatal': 'critical',
    'error': 'high',
    'warning': 'medium',
    'refactor': 'low',
    'convention': 'info',
    'info': 'info'
}


def find_python_files(target_dir: str, max_files: int = 100) -> List[str]:
    """
    Finds Python source files in target directory, excluding common non-source folders.
    """
    excluded_dirs = {'.git', 'venv', '.venv', 'node_modules', '__pycache__', 'dist', 'build', '.tox', '.mypy_cache'}
    py_files = []
    
    for root, dirs, files in os.walk(target_dir):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                py_files.append(full_path)
                if len(py_files) >= max_files:
                    return py_files
    return py_files


def run_pylint(target_dir: str, python_executable: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Executes Pylint over Python files in the target directory and returns parsed findings.
    """
    if not os.path.exists(target_dir):
        logger.error(f"Target directory does not exist: {target_dir}")
        return []

    py_files = find_python_files(target_dir)
    if not py_files:
        logger.info(f"No Python files found to analyze in {target_dir}")
        return []

    python_bin = python_executable or sys.executable

    # Run pylint with JSON output
    # Note: Pylint exit code is a bitmask of message types, so non-zero return code is normal.
    cmd = [
        python_bin,
        "-m",
        "pylint",
        "--output-format=json",
        "--score=n",
        "--exit-zero",
        *py_files
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
            return []

        # Find start of JSON list if any stderr/logging was prefixed
        json_start = output.find('[')
        if json_start != -1:
            output = output[json_start:]

        raw_issues = json.loads(output)
        findings = []

        for issue in raw_issues:
            msg_type = issue.get('type', 'convention').lower()
            severity = SEVERITY_MAP.get(msg_type, 'info')
            symbol = issue.get('symbol', '')
            message_text = issue.get('message', '')
            message_id = issue.get('message-id', '')
            formatted_msg = f"[{message_id}:{symbol}] {message_text}" if symbol else message_text

            # Compute relative file path for clean reporting
            raw_path = issue.get('path', '')
            if os.path.isabs(raw_path):
                rel_path = os.path.relpath(raw_path, target_dir)
            else:
                rel_path = raw_path

            findings.append({
                'tool_name': 'pylint',
                'severity': severity,
                'message': formatted_msg,
                'file_path': rel_path.replace('\\', '/'),
                'line_no': issue.get('line'),
            })

        return findings

    except subprocess.TimeoutExpired:
        logger.error(f"Pylint execution timed out for {target_dir}")
        return [{
            'tool_name': 'pylint',
            'severity': 'high',
            'message': 'Pylint analysis timed out after 120 seconds.',
            'file_path': '',
            'line_no': None
        }]
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Pylint JSON output: {e}. Raw: {result.stdout[:200]}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error running Pylint: {e}")
        return []


def analyze_and_save_pylint(run: AnalysisRun, target_dir: str) -> List[Finding]:
    """
    Runs Pylint on target_dir, creates Finding instances in DB associated with run,
    and returns created Finding objects.
    """
    raw_findings = run_pylint(target_dir)
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
