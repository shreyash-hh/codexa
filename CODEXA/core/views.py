import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone
from django.http import HttpResponse, Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Repository, AnalysisRun, Finding, Score, Recommendation
from .serializers import (
    AnalyzeRequestSerializer,
    RepositorySerializer,
    FindingSerializer,
    ScoreSerializer,
    RecommendationSerializer,
    AnalysisRunSerializer,
    AnalysisRunListSerializer
)
from .services.github_service import (
    clone_github_repo,
    cleanup_cloned_repo,
    GitHubServiceError
)
from .services.scoring_service import compute_and_save_score
from .services.ai_service import generate_gemini_recommendations
from .services.report_service import generate_pdf_report
from .analyzers.pylint_analyzer import run_pylint
from .analyzers.bandit_analyzer import run_bandit
from .analyzers.radon_analyzer import run_radon
from .analyzers.semgrep_analyzer import run_semgrep
from .analyzers.pip_audit_analyzer import run_pip_audit

logger = logging.getLogger(__name__)

# Number of source lines shown above/below a finding for inline code context
SNIPPET_CONTEXT_LINES = 3
MAX_SNIPPET_CHARS = 2000


def extract_code_snippet(target_dir: str, file_path: str, line_no, context: int = SNIPPET_CONTEXT_LINES) -> str:
    """
    Reads a few lines around a finding's location from the cloned repository so the
    UI can show inline code context. Returns an empty string when unavailable.
    """
    if not file_path or not line_no:
        return ''

    abs_path = os.path.join(target_dir, file_path)
    if not os.path.isfile(abs_path):
        return ''

    try:
        with open(abs_path, 'r', encoding='utf-8', errors='replace') as fh:
            lines = fh.readlines()
    except Exception:
        return ''

    start = max(1, line_no - context)
    end = min(len(lines), line_no + context)
    width = len(str(end))

    rendered = []
    for num in range(start, end + 1):
        marker = '>' if num == line_no else ' '
        text = lines[num - 1].rstrip('\n')
        rendered.append(f"{marker} {str(num).rjust(width)} | {text}")

    return "\n".join(rendered)[:MAX_SNIPPET_CHARS]


class AnalyzeView(APIView):
    """
    POST /api/analyze/
    Accepts a GitHub URL, clones the repository, runs full analyzer suite,
    calculates composite and domain scores, generates AI recommendations,
    persists all records to SQLite, and returns comprehensive JSON results.
    """
    def post(self, request, *args, **kwargs):
        serializer = AnalyzeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        github_url = serializer.validated_data['github_url']
        token = serializer.validated_data.get('token', None) or None

        clone_result = None
        try:
            # 1. Clone repository & fetch metadata
            clone_result = clone_github_repo(github_url=github_url, token=token)
            clone_path = clone_result['clone_path']

            # 2. Save / Update Repository in DB
            repo, _ = Repository.objects.update_or_create(
                github_url=github_url,
                defaults={
                    'name': clone_result['name'],
                    'owner': clone_result['owner'],
                    'cloned_at': clone_result['cloned_at'],
                    'status': 'cloned',
                }
            )

            # 3. Create initial AnalysisRun
            run = AnalysisRun.objects.create(
                repository=repo,
                status='running'
            )

            # 4. Execute Analyzers concurrently.
            #    Each analyzer is subprocess/IO bound, so running the five tools in
            #    parallel bounds wall-clock time to the slowest single analyzer
            #    instead of the sum of all five.
            analyzer_jobs = {
                'pylint': run_pylint,
                'bandit': run_bandit,
                'radon': run_radon,
                'semgrep': run_semgrep,
                'pip_audit': run_pip_audit,
            }

            raw_results = {}
            with ThreadPoolExecutor(max_workers=len(analyzer_jobs)) as executor:
                future_to_name = {
                    executor.submit(fn, clone_path): name
                    for name, fn in analyzer_jobs.items()
                }
                for future in as_completed(future_to_name):
                    name = future_to_name[future]
                    try:
                        raw_results[name] = future.result()
                    except Exception as e:
                        logger.exception(f"Analyzer '{name}' failed: {e}")
                        raw_results[name] = []

            pylint_findings = raw_results.get('pylint', [])
            bandit_findings = raw_results.get('bandit', [])
            radon_findings = raw_results.get('radon', [])
            semgrep_findings = raw_results.get('semgrep', [])
            pip_audit_findings = raw_results.get('pip_audit', [])

            # Persist every finding in a single bulk insert (thread-safe on SQLite),
            # capturing inline source context for each located finding.
            all_raw_findings = (
                pylint_findings
                + bandit_findings
                + radon_findings
                + semgrep_findings
                + pip_audit_findings
            )
            findings_to_create = [
                Finding(
                    run=run,
                    tool_name=item['tool_name'],
                    severity=item['severity'],
                    message=item['message'],
                    file_path=item['file_path'],
                    line_no=item['line_no'],
                    snippet=extract_code_snippet(clone_path, item['file_path'], item['line_no']),
                )
                for item in all_raw_findings
            ]
            if findings_to_create:
                Finding.objects.bulk_create(findings_to_create)

            # 5. Compute & Persist Multi-Dimensional Health & Security Scores
            score_obj = compute_and_save_score(run=run)

            # 6. Generate AI Remediation Recommendations (Gemini API / Heuristic)
            recommendations = generate_gemini_recommendations(run=run)

            # 7. Mark Run as Completed
            run.status = 'completed'
            run.completed_at = timezone.now()
            run.save(update_fields=['status', 'completed_at'])

            findings_qs = Finding.objects.filter(run=run)
            findings_data = FindingSerializer(findings_qs, many=True).data
            recs_data = RecommendationSerializer(recommendations, many=True).data

            return Response(
                {
                    "success": True,
                    "message": f"Successfully analyzed repository '{repo.owner}/{repo.name}'",
                    "repository": RepositorySerializer(repo).data,
                    "analysis_run": {
                        "id": run.id,
                        "status": run.status,
                        "started_at": run.started_at,
                        "completed_at": run.completed_at,
                        "total_findings": len(findings_data),
                        "summary_by_tool": {
                            "pylint": len(pylint_findings),
                            "bandit": len(bandit_findings),
                            "radon": len(radon_findings),
                            "semgrep": len(semgrep_findings),
                            "pip_audit": len(pip_audit_findings),
                        }
                    },
                    "score": ScoreSerializer(score_obj).data,
                    "recommendations": recs_data,
                    "findings": findings_data,
                    "metadata": clone_result.get('metadata', {}),
                },
                status=status.HTTP_201_CREATED
            )

        except GitHubServiceError as e:
            logger.error(f"GitHub Service Error: {e}")
            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception("Unexpected error during analysis execution")
            return Response(
                {
                    "success": False,
                    "error": f"Internal server error: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if clone_result and clone_result.get('clone_path'):
                cleanup_cloned_repo(clone_result['clone_path'])


class AnalysisRunListView(APIView):
    """
    GET /api/runs/
    Lists recent completed analysis runs for quick access and historical comparison.
    """
    def get(self, request, *args, **kwargs):
        runs = AnalysisRun.objects.select_related('repository', 'score').filter(status='completed').order_by('-started_at')[:20]
        serializer = AnalysisRunListSerializer(runs, many=True)
        return Response({
            "success": True,
            "runs": serializer.data
        })


class AnalysisRunDetailView(APIView):
    """
    GET /api/runs/<run_id>/
    Retrieves full details for a specific analysis run, matching dashboard schema.
    """
    def get(self, request, run_id, *args, **kwargs):
        try:
            run = AnalysisRun.objects.select_related('repository', 'score').prefetch_related('findings', 'recommendations').get(pk=run_id)
        except AnalysisRun.DoesNotExist:
            return Response({"success": False, "error": "Analysis run not found"}, status=status.HTTP_404_NOT_FOUND)

        findings_qs = list(run.findings.all())
        findings_data = FindingSerializer(findings_qs, many=True).data
        recs_data = RecommendationSerializer(run.recommendations.all(), many=True).data

        summary_by_tool = {
            "pylint": 0,
            "bandit": 0,
            "radon": 0,
            "semgrep": 0,
            "pip_audit": 0
        }
        for f in findings_qs:
            tool_key = f.tool_name.lower().replace('-', '_')
            summary_by_tool[tool_key] = summary_by_tool.get(tool_key, 0) + 1

        return Response({
            "success": True,
            "message": f"Retrieved run #{run.id} for '{run.repository.owner}/{run.repository.name}'",
            "repository": RepositorySerializer(run.repository).data,
            "analysis_run": {
                "id": run.id,
                "status": run.status,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "total_findings": len(findings_data),
                "summary_by_tool": summary_by_tool,
            },
            "score": ScoreSerializer(run.score).data if hasattr(run, 'score') and run.score else None,
            "recommendations": recs_data,
            "findings": findings_data,
            "metadata": {
                "description": f"Automated audit archive for {run.repository.owner}/{run.repository.name}",
                "default_branch": "main",
                "language": "Python",
                "stargazers_count": 0,
                "forks_count": 0,
                "open_issues_count": 0
            }
        })


class AnalysisRunPDFReportView(APIView):
    """
    GET /api/runs/<run_id>/pdf/
    Downloads ReportLab executive PDF report for the specified run.
    """
    def get(self, request, run_id, *args, **kwargs):
        try:
            run = AnalysisRun.objects.select_related('repository', 'score').prefetch_related('findings', 'recommendations').get(pk=run_id)
        except AnalysisRun.DoesNotExist:
            raise Http404("Analysis run not found")

        pdf_buffer = generate_pdf_report(run)
        filename = f"CODEXA_Report_{run.repository.name}_Run{run.id}.pdf"

        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
