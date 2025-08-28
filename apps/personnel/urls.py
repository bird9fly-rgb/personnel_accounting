from django.urls import path
from .views import ServicemanListView, ServicemanDetailView, ElectronicJournalView

app_name = 'personnel'

urlpatterns = [
    # Список особового складу (головна сторінка додатку)
    path('', ServicemanListView.as_view(), name='serviceman-list'),

    # Детальна картка військовослужбовця
    path('serviceman/<int:pk>/', ServicemanDetailView.as_view(), name='serviceman-detail'),

    # Новий маршрут для Електронного журналу
    path('journal/', ElectronicJournalView.as_view(), name='electronic-journal'),
]