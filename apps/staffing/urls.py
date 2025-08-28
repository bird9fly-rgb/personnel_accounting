from django.urls import path
from .views import UnitListView, UnitDetailView, StaffingTableView

app_name = 'staffing'

urlpatterns = [
    # Загальна структура підрозділів (дерево)
    path('', UnitListView.as_view(), name='unit-list'),

    # Новий маршрут для штатно-посадового обліку (таблиця)
    path('table/', StaffingTableView.as_view(), name='staffing-table'),

    # Детальний перегляд підрозділу
    path('<int:pk>/', UnitDetailView.as_view(), name='unit-detail'),
]