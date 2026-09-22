import logging
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
    AnalysisRunSerializer
)
from .services.github_service import (
    clone_github_repo,
    cleanup_cloned_repo,
    GitHubServiceError
)
from .services.scoring_service import compute_and_save_score
from .services.ai_service import generate_gemini_recommendations
from .services.report_service import generate_pdf_report
from .analyzers.pylint_analyzer import analyze_and_save_pylint
from .analyzers.bandit_analyzer import analyze_and_save_bandit
from .analyzers.radon_analyzer import analyze_and_save_radon
from .analyzers.semgrep_analyzer import analyze_and_save_semgrep
from .analyzers.pip_audit_analyzer import analyze_and_save_pip_audit

logger = logging.getLogger(__name__)


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

            # 4. Execute Analyzers
            pylint_findings = analyze_and_save_pylint(run=run, target_dir=clone_path)
            bandit_findings = analyze_and_save_bandit(run=run, target_dir=clone_path)
            radon_findings = analyze_and_save_radon(run=run, target_dir=clone_path)
            semgrep_findings = analyze_and_save_semgrep(run=run, target_dir=clone_path)
            pip_audit_findings = analyze_and_save_pip_audit(run=run, target_dir=clone_path)

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


class AnalysisRunDetailView(APIView):
    """
    GET /api/runs/<run_id>/
    Retrieves full details for a specific analysis run.
    """
    def get(self, request, run_id, *args, **kwargs):
        try:
            run = AnalysisRun.objects.select_related('repository', 'score').prefetch_related('findings', 'recommendations').get(pk=run_id)
        except AnalysisRun.DoesNotExist:
            return Response({"success": False, "error": "Analysis run not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "success": True,
            "data": AnalysisRunSerializer(run).data
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
