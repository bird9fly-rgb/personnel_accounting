from django.urls import path
from .views import ServicemanListView, ServicemanDetailView

app_name = 'personnel'

urlpatterns = [
    path('', ServicemanListView.as_view(), name='serviceman-list'),
    path('serviceman/<int:pk>/', ServicemanDetailView.as_view(), name='serviceman-detail'),
]