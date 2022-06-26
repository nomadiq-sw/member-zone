from django.urls import path, reverse_lazy
import django.contrib.auth.views as auth_views
from website import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('index', views.IndexView.as_view(), name='index'),
    path('memberships/login', views.LoginSignupView.as_view(), name='login'),
    path('memberships/logout', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password-reset/invalid',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_invalid.html'),
         name='password-reset-invalid'),
    path('password-reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('password-reset-complete')),
         name='password-reset-confirm'),
    path('password-reset/complete', auth_views.PasswordResetCompleteView.as_view(), name='password-reset-complete'),
    path('memberships/my-memberships', views.MembershipView.as_view(), name='my-memberships'),
    path('memberships/my-memberships/update', views.MembershipTableView.as_view(), name='update-memberships'),
    path('memberships/my-memberships/<int:pk>/toggle-reminders', views.toggle_reminders, name='toggle-reminders'),
    path('memberships/my-memberships/<int:pk>/delete', views.DeleteMembershipView.as_view(), name='delete-membership'),
    path('memberships/my-memberships/<int:pk>/edit', views.EditMembershipView.as_view(), name='edit-membership'),
]

htmx_urlpatterns = []

urlpatterns += htmx_urlpatterns
