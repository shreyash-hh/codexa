import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Repository, AnalysisRun, Finding
from .serializers import (
    AnalyzeRequestSerializer,
    RepositorySerializer,
    FindingSerializer,
    AnalysisRunSerializer
)
from .services.github_service import (
    clone_github_repo,
    cleanup_cloned_repo,
    GitHubServiceError
)
from .analyzers.pylint_analyzer import analyze_and_save_pylint

logger = logging.getLogger(__name__)


class AnalyzeView(APIView):
    """
    POST /api/analyze/
    Accepts a GitHub URL, clones the repository, saves/updates Repository record,
    runs Pylint static analysis, records findings, and returns detailed results.
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

            # 4. Run Pylint Analyzer
            created_findings = analyze_and_save_pylint(run=run, target_dir=clone_path)

            # 5. Mark Run as Completed
            run.status = 'completed'
            run.completed_at = timezone.now()
            run.save(update_fields=['status', 'completed_at'])

            findings_qs = Finding.objects.filter(run=run)
            findings_data = FindingSerializer(findings_qs, many=True).data

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
                        "pylint_findings_count": len(findings_data),
                    },
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
