import os
import sys
import json
import logging
import subprocess
from typing import List, Dict, Any, Optional
from core.models import AnalysisRun, Finding

logger = logging.getLogger(__name__)


def find_requirements_files(target_dir: str) -> List[str]:
    """
    Finds Python dependency manifest files in target directory.
    """
    manifest_names = {
        'requirements.txt', 'requirements-dev.txt', 'requirements_dev.txt',
        'dev-requirements.txt', 'Pipfile.lock', 'pyproject.toml'
    }
    found = []
    for root, dirs, files in os.walk(target_dir):
        # Prune non-source directories
        dirs[:] = [d for d in dirs if d not in {'.git', 'venv', '.venv', 'node_modules', '__pycache__'}]
        for file in files:
            if file in manifest_names or (file.startswith('requirements') and file.endswith('.txt')):
                found.append(os.path.join(root, file))
    return found


def run_pip_audit(target_dir: str, python_executable: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Executes pip-audit dependency vulnerability scanner over manifest files in target_dir.
    """
    if not os.path.exists(target_dir):
        logger.error(f"Target directory does not exist: {target_dir}")
        return []

    req_files = find_requirements_files(target_dir)
    python_bin = python_executable or sys.executable
    findings = []

    if not req_files:
        logger.info(f"No requirements/manifest files found in {target_dir} for pip-audit.")
        return []

    for req_file in req_files:
        rel_path = os.path.relpath(req_file, target_dir).replace('\\', '/')
        cmd = [
            python_bin,
            "-m",
            "pip_audit",
            "-r",
            req_file,
            "-f",
            "json",
            "--desc"
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
                    continue

            json_start = output.find('{')
            if json_start == -1:
                json_start = output.find('[')
            if json_start != -1:
                output = output[json_start:]

            data = json.loads(output)
            
            # Format can be { "dependencies": [ ... ] } or list of dependencies
            deps = data.get('dependencies', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

            for dep in deps:
                dep_name = dep.get('name', 'Unknown')
                dep_version = dep.get('version', '')
                vulns = dep.get('vulns', [])

                for vuln in vulns:
                    vuln_id = vuln.get('id', '')
                    aliases = ", ".join(vuln.get('aliases', []))
                    id_label = f"{vuln_id} ({aliases})" if aliases else vuln_id
                    description = vuln.get('description', 'Known vulnerability')
                    fix_versions = ", ".join(vuln.get('fix_versions', [])) or "None available"

                    message = (
                        f"[pip-audit:{dep_name}=={dep_version}] {id_label}: {description} "
                        f"| Fix versions: {fix_versions}"
                    )

                    findings.append({
                        'tool_name': 'pip-audit',
                        'severity': 'high',
                        'message': message,
                        'file_path': rel_path,
                        'line_no': None,
                    })

        except subprocess.TimeoutExpired:
            logger.error(f"pip-audit timed out for {req_file}")
            findings.append({
                'tool_name': 'pip-audit',
                'severity': 'high',
                'message': f'pip-audit scan timed out for {rel_path}',
                'file_path': rel_path,
                'line_no': None
            })
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse pip-audit JSON for {req_file}: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error running pip-audit on {req_file}: {e}")

    return findings


def analyze_and_save_pip_audit(run: AnalysisRun, target_dir: str) -> List[Finding]:
    """
    Runs pip-audit on target_dir, persists findings tagged with tool_name='pip-audit',
    and returns created Finding instances.
    """
    raw_findings = run_pip_audit(target_dir)
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
