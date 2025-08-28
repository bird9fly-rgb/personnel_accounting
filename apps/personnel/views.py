from django.views.generic import ListView, DetailView, TemplateView
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

    def get_context_data(self, **kwargs):
        """Додаємо пов'язані дані до контексту."""
        context = super().get_context_data(**kwargs)
        serviceman = self.get_object()
        context['education_history'] = serviceman.education_history.all()
        context['family_members'] = serviceman.family_members.all()
        context['service_history'] = serviceman.service_history.all()
        return context


class ElectronicJournalView(TemplateView):
    """
    Представлення для "Електронного журналу обліку особового складу".
    Збирає дані з різних моделей та представляє їх у структурованому вигляді.
    """
    template_name = 'personnel/electronic_journal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Основний особовий склад (на службі)
        context['on_duty_servicemen'] = Serviceman.objects.filter(
            status=Serviceman.Status.ON_DUTY
        ).select_related('rank', 'position__unit')

        # 2. Тимчасово відсутній особовий склад
        context['temporarily_absent'] = Serviceman.objects.filter(
            status__in=[
                Serviceman.Status.ON_LEAVE,
                Serviceman.Status.SICK_LEAVE,
                Serviceman.Status.AWOL
            ]
        ).select_related('rank', 'position__unit')

        # 3. Виключені зі списків (безповоротні втрати та звільнені)
        context['excluded_servicemen'] = Serviceman.objects.filter(
            status__in=[
                Serviceman.Status.DISMISSED,
                Serviceman.Status.KIA,
                Serviceman.Status.MIA
            ]
        ).select_related('rank')  # Посади може вже не бути

        context['title'] = "Електронний журнал обліку особового складу"

        return context