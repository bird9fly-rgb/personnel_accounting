from django.views.generic import ListView, DetailView
from .models import Unit

class UnitListView(ListView):
    model = Unit
    template_name = 'staffing/unit_list.html'
    context_object_name = 'units'

class UnitDetailView(DetailView):
    model = Unit
    template_name = 'staffing/unit_detail.html'
    context_object_name = 'unit'