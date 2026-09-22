from django.db import models


class Repository(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cloned', 'Cloned'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    github_url = models.URLField(max_length=500)
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    cloned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Repositories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.owner}/{self.name} ({self.status})"


class AnalysisRun(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        related_name='analysis_runs'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Run #{self.pk} - {self.repository.name} ({self.status})"


class Finding(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    run = models.ForeignKey(
        AnalysisRun,
        on_delete=models.CASCADE,
        related_name='findings'
    )
    tool_name = models.CharField(
        max_length=50,
        help_text="e.g. pylint, bandit, radon, semgrep, pip-audit"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='info'
    )
    message = models.TextField()
    file_path = models.CharField(max_length=1000, blank=True, null=True)
    line_no = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['run', 'severity', 'file_path', 'line_no']

    def __str__(self):
        return f"[{self.tool_name.upper()}] [{self.severity.upper()}] {self.file_path or 'General'}:{self.line_no or '-'}"


class Score(models.Model):
    run = models.OneToOneField(
        AnalysisRun,
        on_delete=models.CASCADE,
        related_name='score'
    )
    quality_score = models.FloatField(default=0.0)
    security_score = models.FloatField(default=0.0)
    dependency_score = models.FloatField(default=0.0)
    composite_score = models.FloatField(default=0.0)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score for Run #{self.run_id}: Composite={self.composite_score:.2f}"


class Recommendation(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    run = models.ForeignKey(
        AnalysisRun,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    text = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['run', 'priority', '-created_at']

    def __str__(self):
        return f"[{self.priority.upper()}] Recommendation for Run #{self.run_id}"
