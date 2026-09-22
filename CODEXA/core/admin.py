from django.contrib import admin
from .models import Repository, AnalysisRun, Finding, Score, Recommendation


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'status', 'cloned_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'owner', 'github_url')


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'repository', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('repository__name', 'repository__owner')


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'tool_name', 'severity', 'file_path', 'line_no')
    list_filter = ('tool_name', 'severity')
    search_fields = ('message', 'file_path', 'tool_name')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'quality_score', 'security_score', 'dependency_score', 'composite_score')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'priority', 'created_at')
    list_filter = ('priority',)
    search_fields = ('text',)
