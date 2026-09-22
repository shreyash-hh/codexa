import os
import sys
import json
import logging
import subprocess
from typing import List, Dict, Any, Optional
from core.models import AnalysisRun, Finding

logger = logging.getLogger(__name__)

# Radon Cyclomatic Complexity Rank to Severity
CC_RANK_SEVERITY = {
    'A': 'info',      # 1-5 (Simple, low risk)
    'B': 'low',       # 6-10 (Low risk)
    'C': 'medium',    # 11-20 (Moderate risk)
    'D': 'high',      # 21-30 (High risk)
    'E': 'critical',  # 31-40 (Very high risk)
    'F': 'critical'   # 41+ (Extremely complex)
}


def run_radon(target_dir: str, python_executable: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Executes Radon Cyclomatic Complexity (cc) analysis with JSON output on target directory.
    """
    if not os.path.exists(target_dir):
        logger.error(f"Target directory does not exist: {target_dir}")
        return []

    python_bin = python_executable or sys.executable
    excluded_dirs = "*/venv/*,*/.venv/*,*/node_modules/*,*/.git/*,*/__pycache__/*,*/dist/*,*/build/*"

    cmd = [
        python_bin,
        "-m",
        "radon",
        "cc",
        "-j",
        "-s",
        "-e",
        excluded_dirs,
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
            return []

        json_start = output.find('{')
        if json_start != -1:
            output = output[json_start:]

        data = json.loads(output)
        findings = []

        # Data structure: { "filepath": [ { "type": "function", "name": "...", "complexity": 12, "rank": "C", "lineno": 45 }, ... ] }
        for file_path, items in data.items():
            if not isinstance(items, list):
                continue

            rel_path = os.path.relpath(file_path, target_dir) if os.path.isabs(file_path) else file_path
            rel_path = rel_path.replace('\\', '/')

            for item in items:
                rank = item.get('rank', 'A')
                complexity = item.get('complexity', 1)
                name = item.get('name', 'anonymous')
                item_type = item.get('type', 'block')
                line_no = item.get('lineno')

                # Report all blocks with rank >= B (complexity >= 6) or noteworthy complexity
                if rank in ['B', 'C', 'D', 'E', 'F']:
                    severity = CC_RANK_SEVERITY.get(rank, 'medium')
                    message = (
                        f"[Radon:CC] High cyclomatic complexity (Rank {rank}, Score: {complexity}) "
                        f"in {item_type} '{name}'"
                    )
                    findings.append({
                        'tool_name': 'radon',
                        'severity': severity,
                        'message': message,
                        'file_path': rel_path,
                        'line_no': line_no,
                    })

        return findings

    except subprocess.TimeoutExpired:
        logger.error(f"Radon execution timed out for {target_dir}")
        return [{
            'tool_name': 'radon',
            'severity': 'high',
            'message': 'Radon complexity analysis timed out after 120 seconds.',
            'file_path': '',
            'line_no': None
        }]
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Radon JSON output: {e}. Raw: {result.stdout[:200]}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error running Radon: {e}")
        return []


def analyze_and_save_radon(run: AnalysisRun, target_dir: str) -> List[Finding]:
    """
    Runs Radon on target_dir, persists findings tagged with tool_name='radon',
    and returns created Finding instances.
    """
    raw_findings = run_radon(target_dir)
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
