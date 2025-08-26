from django.urls import path
from .views import UnitListView, UnitDetailView

app_name = 'staffing'

urlpatterns = [
    path('', UnitListView.as_view(), name='unit-list'),
    path('<int:pk>/', UnitDetailView.as_view(), name='unit-detail'),
]