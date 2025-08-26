from django.views.generic import ListView, DetailView
from .models import Serviceman

class ServicemanListView(ListView):
    model = Serviceman
    template_name = 'personnel/serviceman_list.html'
    context_object_name = 'servicemen'
    paginate_by = 20

class ServicemanDetailView(DetailView):
    model = Serviceman
    template_name = 'personnel/serviceman_detail.html'
    context_object_name = 'serviceman'