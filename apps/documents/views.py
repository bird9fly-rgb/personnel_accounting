# apps/documents/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import ServicemanReport
from .forms import ServicemanReportForm, ReportResolutionForm


class ReportListView(LoginRequiredMixin, ListView):
    """
    Представлення для відображення списку всіх рапортів.
    (спрощена логіка, оскільки всі користувачі - діловоди)
    """
    model = ServicemanReport
    template_name = 'documents/report_list.html'
    context_object_name = 'reports'
    paginate_by = 15

    def get_queryset(self):
        # Діловоди бачать абсолютно всі рапорти
        return ServicemanReport.objects.select_related('author', 'author__rank').all()


class ReportDetailView(LoginRequiredMixin, FormMixin, DetailView):
    """
    Представлення для детального перегляду рапорту.
    """
    model = ServicemanReport
    template_name = 'documents/report_detail.html'
    context_object_name = 'report'
    form_class = ReportResolutionForm

    def get_success_url(self):
        return reverse_lazy('documents:report-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resolution_form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        report = self.get_object()
        report.resolution = form.cleaned_data['resolution']
        report.status = form.cleaned_data['status']
        report.reviewed_by = self.request.user  # Фіксуємо, який діловод додав резолюцію
        report.save()
        messages.success(self.request, 'Резолюцію успішно додано.')
        return super().form_valid(form)


class ReportCreateView(LoginRequiredMixin, CreateView):
    """
    Представлення для створення (реєстрації) нового рапорту діловодом.
    """
    model = ServicemanReport
    form_class = ServicemanReportForm
    template_name = 'documents/report_form.html'
    success_url = reverse_lazy('documents:report-list')

    def form_valid(self, form):
        messages.success(self.request, f"Рапорт №{form.instance.registration_number} успішно зареєстровано.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Реєстрація нового рапорту"
        return context


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представлення для редагування існуючого рапорту.
    """
    model = ServicemanReport
    form_class = ServicemanReportForm
    template_name = 'documents/report_form.html'

    def get_success_url(self):
        return reverse_lazy('documents:report-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Рапорт №{self.object.registration_number} успішно оновлено.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Редагування рапорту №{self.object.registration_number}"
        return context