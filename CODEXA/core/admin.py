from django.contrib import admin
from .models import Repository, AnalysisRun, Finding, Score, Recommendation


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'status', 'cloned_at', 'created_at')
    search_fields = ('name', 'owner', 'github_url')
    list_filter = ('status',)


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'repository', 'status', 'started_at', 'completed_at')
    list_filter = ('status',)


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'tool_name', 'severity', 'file_path', 'line_no')
    list_filter = ('tool_name', 'severity')
    search_fields = ('file_path', 'message')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'quality_score', 'security_score', 'dependency_score', 'composite_score')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'priority', 'text')
    list_filter = ('priority',)
