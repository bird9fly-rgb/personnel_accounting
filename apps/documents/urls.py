# apps/documents/urls.py
from django.urls import path
from .views import (
    ReportListView,
    ReportDetailView,
    ReportCreateView,
    ReportUpdateView,
)

app_name = 'documents'

urlpatterns = [
    # Список рапортів (головна сторінка додатку)
    path('', ReportListView.as_view(), name='report-list'),

    # Створення нового рапорту
    path('new/', ReportCreateView.as_view(), name='report-create'),

    # Детальний перегляд рапорту
    path('<int:pk>/', ReportDetailView.as_view(), name='report-detail'),

    # Редагування рапорту
    path('<int:pk>/edit/', ReportUpdateView.as_view(), name='report-update'),
]