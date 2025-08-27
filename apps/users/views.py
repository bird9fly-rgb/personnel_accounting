# apps/users/views.py
"""
Views для автентифікації та управління користувачами
"""

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
    PasswordChangeView as BasePasswordChangeView,
    PasswordResetView as BasePasswordResetView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, ListView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import User
from apps.auditing.models import AuditLog, SecurityEvent


class LoginView(BaseLoginView):
    """Кастомний view для входу в систему"""
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Логування успішного входу"""
        response = super().form_valid(form)

        # Логуємо успішний вхід
        SecurityEvent.objects.create(
            event_type='LOGIN_SUCCESS',
            user=self.request.user,
            ip_address=self.get_client_ip(),
            details={
                'username': self.request.user.username,
                'timestamp': timezone.now().isoformat(),
            }
        )

        AuditLog.log_action(
            user=self.request.user,
            action='LOGIN',
            request=self.request,
            notes=f"Вхід в систему: {self.request.user.username}"
        )

        messages.success(self.request, f'Вітаємо, {self.request.user.get_full_name() or self.request.user.username}!')

        return response

    def form_invalid(self, form):
        """Логування невдалої спроби входу"""
        username = form.cleaned_data.get('username', 'unknown')

        # Логуємо невдалий вхід
        SecurityEvent.objects.create(
            event_type='LOGIN_FAILED',
            user=None,
            ip_address=self.get_client_ip(),
            details={
                'attempted_username': username,
                'timestamp': timezone.now().isoformat(),
            }
        )

        return super().form_invalid(form)

    def get_client_ip(self):
        """Отримання IP адреси клієнта"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(BaseLogoutView):
    """Кастомний view для виходу з системи"""
    next_page = 'users:login'

    def dispatch(self, request, *args, **kwargs):
        """Логування виходу"""
        if request.user.is_authenticated:
            AuditLog.log_action(
                user=request.user,
                action='LOGOUT',
                request=request,
                notes=f"Вихід з системи: {request.user.username}"
            )
            messages.info(request, 'Ви успішно вийшли з системи.')

        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """View для перегляду профілю користувача"""
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Отримуємо інформацію про військовослужбовця якщо є
        if hasattr(user, 'serviceman'):
            context['serviceman'] = user.serviceman
            context['position'] = user.serviceman.position
            context['contracts'] = user.serviceman.contracts.all()

        # Групи користувача
        context['user_groups'] = user.groups.all()

        # Останні дії користувача
        context['recent_actions'] = AuditLog.objects.filter(
            user=user
        ).order_by('-timestamp')[:10]

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """View для редагування профілю"""
    model = User
    template_name = 'users/profile_edit.html'
    fields = ['first_name', 'last_name', 'middle_name', 'email']
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        """Логування зміни профілю"""
        old_values = {
            'first_name': self.object.first_name,
            'last_name': self.object.last_name,
            'middle_name': self.object.middle_name,
            'email': self.object.email,
        }

        response = super().form_valid(form)

        new_values = {
            'first_name': self.object.first_name,
            'last_name': self.object.last_name,
            'middle_name': self.object.middle_name,
            'email': self.object.email,
        }

        AuditLog.log_action(
            user=self.request.user,
            action='UPDATE',
            obj=self.object,
            changes={'old': old_values, 'new': new_values},
            request=self.request,
            notes="Оновлення профілю користувача"
        )

        messages.success(self.request, 'Профіль успішно оновлено!')

        return response


class PasswordChangeView(LoginRequiredMixin, BasePasswordChangeView):
    """View для зміни пароля"""
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        """Логування зміни пароля"""
        response = super().form_valid(form)

        SecurityEvent.objects.create(
            event_type='PASSWORD_CHANGE',
            user=self.request.user,
            ip_address=self.get_client_ip(),
            details={
                'timestamp': timezone.now().isoformat(),
            }
        )

        AuditLog.log_action(
            user=self.request.user,
            action='UPDATE',
            request=self.request,
            severity='WARNING',
            notes="Зміна пароля користувача"
        )

        messages.success(self.request, 'Пароль успішно змінено!')

        return response

    def get_client_ip(self):
        """Отримання IP адреси клієнта"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class UserListView(LoginRequiredMixin, ListView):
    """View для перегляду списку користувачів (для адміністраторів)"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        """Фільтрація користувачів"""
        queryset = super().get_queryset()

        # Фільтр по групі
        group = self.request.GET.get('group')
        if group:
            queryset = queryset.filter(groups__name=group)

        # Пошук
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Додаємо групи для фільтра
        from django.contrib.auth.models import Group
        context['groups'] = Group.objects.all()
        context['selected_group'] = self.request.GET.get('group')
        context['search_query'] = self.request.GET.get('search')

        return context


class SecurityDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard безпеки для адміністраторів"""
    template_name = 'users/security_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Останні події безпеки
        context['recent_security_events'] = SecurityEvent.objects.all()[:20]

        # Статистика входів
        today = timezone.now().date()
        context['login_stats'] = {
            'today_success': SecurityEvent.objects.filter(
                event_type='LOGIN_SUCCESS',
                timestamp__date=today
            ).count(),
            'today_failed': SecurityEvent.objects.filter(
                event_type='LOGIN_FAILED',
                timestamp__date=today
            ).count(),
        }

        # Підозріла активність
        context['suspicious_activities'] = SecurityEvent.objects.filter(
            event_type='SUSPICIOUS_ACTIVITY',
            is_resolved=False
        )

        return context