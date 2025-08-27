# apps/reporting/urls.py
"""
URL маршрути для модуля звітності
"""

from django.urls import path
from .views import (
    ReportDashboardView,
    StaffingReportView,
    PersonnelStatisticsView,
    ContractReportView,
    ServiceHistoryReportView,
    ExportReportView,
    ComparisonReportView,
)

app_name = 'reporting'

urlpatterns = [
    # Головна сторінка звітності
    path('', ReportDashboardView.as_view(), name='dashboard'),

    # Звіти
    path('staffing/', StaffingReportView.as_view(), name='staffing-report'),
    path('personnel/', PersonnelStatisticsView.as_view(), name='personnel-statistics'),
    path('contracts/', ContractReportView.as_view(), name='contract-report'),
    path('service-history/', ServiceHistoryReportView.as_view(), name='service-history-report'),
    path('comparison/', ComparisonReportView.as_view(), name='comparison-report'),

    # Експорт
    path('export/<str:report_type>/', ExportReportView.as_view(), name='export-report'),
]