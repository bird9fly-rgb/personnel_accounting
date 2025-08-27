# apps/reporting/views.py
"""
Views для звітності та аналітики
"""

from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .services import (
    StaffingReportService,
    PersonnelReportService,
    ContractReportService,
    ExportService
)
from apps.staffing.models import Unit
from apps.auditing.models import AuditLog, DataExportLog
import json


class ReportDashboardView(LoginRequiredMixin, TemplateView):
    """Головна сторінка звітності"""
    template_name = 'reporting/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Швидка статистика
        personnel_stats = PersonnelReportService.get_personnel_statistics()
        contract_status = ContractReportService.get_contracts_status()

        context.update({
            'total_servicemen': personnel_stats['total_servicemen'],
            'contracts_ending_soon': contract_status['ending_30_days']['count'],
            'expired_contracts': contract_status['expired']['count'],
            'last_update': timezone.now(),
        })

        return context


class StaffingReportView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Звіт по укомплектованості"""
    template_name = 'reporting/staffing_report.html'
    permission_required = 'reporting.view_report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        unit_id = self.request.GET.get('unit_id')

        if unit_id:
            report = StaffingReportService.get_unit_staffing_report(int(unit_id))
            context['report'] = report

            # Логуємо перегляд звіту
            AuditLog.log_action(
                user=self.request.user,
                action='VIEW',
                changes={'report_type': 'staffing', 'unit_id': unit_id},
                request=self.request,
                notes=f"Переглянуто звіт по укомплектованості {report['unit_name']}"
            )
        else:
            # Показуємо зведений звіт по всіх батальйонах
            context['summary'] = StaffingReportService.get_brigade_staffing_summary()

        # Список підрозділів для вибору
        context['units'] = Unit.objects.filter(level__lte=2)  # Тільки бригада та батальйони

        return context


class PersonnelStatisticsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Статистика особового складу"""
    template_name = 'reporting/personnel_statistics.html'
    permission_required = 'reporting.view_report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        statistics = PersonnelReportService.get_personnel_statistics()
        context['statistics'] = statistics

        # Підготовка даних для графіків
        context['rank_chart_data'] = json.dumps(statistics['by_rank'])
        context['age_chart_data'] = json.dumps(
            [{'group': k, 'count': v} for k, v in statistics['by_age'].items()]
        )

        return context


class ContractReportView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Звіт по контрактах"""
    template_name = 'reporting/contract_report.html'
    permission_required = 'reporting.view_report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['contract_status'] = ContractReportService.get_contracts_status()
        context['forecast'] = ContractReportService.get_contract_renewal_forecast()

        return context


class ServiceHistoryReportView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Звіт по історії служби"""
    template_name = 'reporting/service_history_report.html'
    permission_required = 'reporting.view_report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отримуємо дати з параметрів або використовуємо останній місяць
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        if self.request.GET.get('start_date'):
            start_date = datetime.strptime(self.request.GET['start_date'], '%Y-%m-%d').date()
        if self.request.GET.get('end_date'):
            end_date = datetime.strptime(self.request.GET['end_date'], '%Y-%m-%d').date()

        context['report'] = PersonnelReportService.get_service_history_report(start_date, end_date)
        context['start_date'] = start_date
        context['end_date'] = end_date

        return context


class ExportReportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View для експорту звітів"""
    permission_required = 'reporting.export_report'

    def get(self, request, report_type):
        """Експорт звіту в різні формати"""
        format = request.GET.get('format', 'excel')

        # Отримуємо дані звіту
        report_data = self._get_report_data(report_type, request)

        if format == 'excel':
            # Експорт в Excel
            file_content = ExportService.export_to_excel(report_data, report_type)
            response = HttpResponse(
                file_content,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response[
                'Content-Disposition'] = f'attachment; filename="{report_type}_{timezone.now().strftime("%Y%m%d")}.xlsx"'

            # Логуємо експорт
            DataExportLog.objects.create(
                user=request.user,
                model_name=report_type,
                format='EXCEL',
                records_count=len(report_data.get('data', [])),
                ip_address=self._get_client_ip(request)
            )

            return response

        elif format == 'json':
            # Експорт в JSON
            response = JsonResponse(report_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
            response[
                'Content-Disposition'] = f'attachment; filename="{report_type}_{timezone.now().strftime("%Y%m%d")}.json"'

            # Логуємо експорт
            DataExportLog.objects.create(
                user=request.user,
                model_name=report_type,
                format='JSON',
                records_count=len(report_data.get('data', [])),
                ip_address=self._get_client_ip(request)
            )

            return response

        return HttpResponse("Невідомий формат", status=400)

    def _get_report_data(self, report_type, request):
        """Отримання даних для експорту залежно від типу звіту"""
        if report_type == 'staffing':
            unit_id = request.GET.get('unit_id')
            if unit_id:
                return StaffingReportService.get_unit_staffing_report(int(unit_id))
            else:
                return {'data': StaffingReportService.get_brigade_staffing_summary()}

        elif report_type == 'personnel':
            return PersonnelReportService.get_personnel_statistics()

        elif report_type == 'contracts':
            return ContractReportService.get_contracts_status()

        return {}

    def _get_client_ip(self, request):
        """Отримання IP адреси клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ComparisonReportView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """Порівняльний звіт між підрозділами"""
    template_name = 'reporting/comparison_report.html'
    permission_required = 'reporting.view_report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отримуємо всі батальйони для порівняння
        battalions_data = []
        battalions = Unit.objects.filter(name__contains='батальйон')

        for battalion in battalions:
            report = StaffingReportService.get_unit_staffing_report(battalion.id)
            battalions_data.append({
                'name': battalion.name,
                'data': report['summary']
            })

        context['battalions_comparison'] = battalions_data

        return context