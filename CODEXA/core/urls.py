from django.urls import path
from .views import AnalyzeView, AnalysisRunListView, AnalysisRunDetailView, AnalysisRunPDFReportView

urlpatterns = [
    path('analyze/', AnalyzeView.as_view(), name='analyze_repository'),
    path('runs/', AnalysisRunListView.as_view(), name='run_list'),
    path('runs/<int:run_id>/', AnalysisRunDetailView.as_view(), name='run_detail'),
    path('runs/<int:run_id>/pdf/', AnalysisRunPDFReportView.as_view(), name='run_pdf_report'),
]
