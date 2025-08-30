from django.views.generic import ListView, DetailView, TemplateView
from .models import Serviceman, TemporaryArrival, IrrecoverableLoss


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
    """
    template_name = 'personnel/electronic_journal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['on_duty_servicemen'] = Serviceman.objects.filter(
            status=Serviceman.Status.ON_DUTY
        ).select_related('rank', 'position__unit')

        context['temporarily_absent'] = Serviceman.objects.filter(
            status__in=[
                Serviceman.Status.ON_LEAVE,
                Serviceman.Status.SICK_LEAVE,
                Serviceman.Status.AWOL
            ]
        ).select_related('rank', 'position__unit')

        context['excluded_servicemen'] = Serviceman.objects.filter(
            status__in=[
                Serviceman.Status.DISMISSED,
                Serviceman.Status.KIA,
                Serviceman.Status.MIA
            ]
        ).select_related('rank')

        context['temporary_arrivals'] = TemporaryArrival.objects.all()

        # НОВИЙ ЗАПИТ: Отримуємо дані про безповоротні втрати
        context['irrecoverable_losses'] = IrrecoverableLoss.objects.select_related(
            'serviceman', 'serviceman__rank'
        ).all()

        context['title'] = "Електронний журнал обліку особового складу"

        return context


class TemporaryArrivalListView(ListView):
    """
    Представлення для окремої сторінки "Тимчасово прибулі".
    """
    model = TemporaryArrival
    template_name = 'personnel/temporary_arrival_list.html'
    context_object_name = 'arrivals'
    paginate_by = 20
