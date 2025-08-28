from django.views.generic import ListView, DetailView
from .models import Unit, Position


class UnitListView(ListView):
    model = Unit
    template_name = 'staffing/unit_list.html'
    context_object_name = 'units'


class UnitDetailView(DetailView):
    model = Unit
    template_name = 'staffing/unit_detail.html'
    context_object_name = 'unit'


class StaffingTableView(ListView):
    """
    Представлення для відображення штатно-посадового обліку (ШПО).
    Генерує повний список посад, згрупованих по підрозділах.
    """
    model = Position
    template_name = 'staffing/staffing_table.html'
    context_object_name = 'positions'

    def get_queryset(self):
        """
        Отримуємо всі посади, відсортовані за структурою підрозділів,
        а потім за індексом посади. Також одразу завантажуємо пов'язані дані.
        """
        return Position.objects.select_related(
            'unit',
            'specialty',
            'serviceman',
            'serviceman__rank'
        ).order_by('unit__tree_id', 'unit__lft', 'position_index')

    def get_context_data(self, **kwargs):
        """
        Групуємо посади за підрозділами для зручного відображення в шаблоні.
        """
        context = super().get_context_data(**kwargs)

        # Створюємо словник, де ключ - це підрозділ, а значення - список його посад
        units_with_positions = {}
        for position in context['positions']:
            if position.unit not in units_with_positions:
                units_with_positions[position.unit] = []
            units_with_positions[position.unit].append(position)

        context['units_with_positions'] = units_with_positions
        context['page_title'] = "Штатно-посадовий облік"
        return context