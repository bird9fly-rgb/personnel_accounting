# apps/users/urls.py
"""
URL маршрути для модуля користувачів
"""

from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .views import (
    LoginView,
    LogoutView,
    ProfileView,
    ProfileEditView,
    PasswordChangeView,
    UserListView,
    SecurityDashboardView,
)

app_name = 'users'

urlpatterns = [
    # Автентифікація
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Профіль
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile-edit'),

    # Зміна пароля
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),

    # Скидання пароля
    path('password/reset/',
         PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             success_url='/users/password/reset/done/'
         ),
         name='password-reset'),
    path('password/reset/done/',
         PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password-reset-done'),
    path('password/reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url='/users/password/reset/complete/'
         ),
         name='password-reset-confirm'),
    path('password/reset/complete/',
         PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password-reset-complete'),

    # Адміністративні
    path('list/', UserListView.as_view(), name='user-list'),
    path('security/', SecurityDashboardView.as_view(), name='security-dashboard'),
]