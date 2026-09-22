from rest_framework import serializers
from .models import Repository, AnalysisRun, Finding, Score, Recommendation


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'github_url', 'name', 'owner', 'cloned_at', 'status', 'created_at']
        read_only_fields = ['id', 'name', 'owner', 'cloned_at', 'status', 'created_at']


class AnalyzeRequestSerializer(serializers.Serializer):
    github_url = serializers.URLField(required=True, help_text="Public or accessible GitHub repository URL")
    token = serializers.CharField(required=False, allow_blank=True, default="", help_text="Optional GitHub Personal Access Token")


class FindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finding
        fields = ['id', 'tool_name', 'severity', 'message', 'file_path', 'line_no']


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['id', 'quality_score', 'security_score', 'dependency_score', 'composite_score']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'text', 'priority']


class AnalysisRunSerializer(serializers.ModelSerializer):
    repository = RepositorySerializer(read_only=True)
    findings = FindingSerializer(many=True, read_only=True)
    score = ScoreSerializer(read_only=True)
    recommendations = RecommendationSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisRun
        fields = ['id', 'repository', 'started_at', 'completed_at', 'status', 'findings', 'score', 'recommendations']
