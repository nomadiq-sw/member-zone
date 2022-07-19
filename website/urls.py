# Copyright 2022 Owen M. Jones. All rights reserved.
#
# This file is part of MemberZone.
#
# MemberZone is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License 
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# MemberZone is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with MemberZone. If not, see <https://www.gnu.org/licenses/>.
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
	path('about', views.AboutView.as_view(), name='about'),
	path('about/terms-conditions', views.TermsAndConditionsView.as_view(), name='terms-conditions'),
	path('about/privacy-policy', views.PrivacyPolicyView.as_view(), name='privacy-policy')
]

htmx_urlpatterns = [
	path('memberships/my-memberships/update', views.MembershipTableView.as_view(), name='update-memberships'),
	path('memberships/my-memberships/<int:pk>/toggle-reminders', views.toggle_reminders, name='toggle-reminders'),
	path('memberships/my-memberships/<int:pk>/delete', views.DeleteMembershipView.as_view(), name='delete-membership'),
	path('memberships/my-memberships/<int:pk>/edit', views.EditMembershipView.as_view(), name='edit-membership'),
	path('about/submit-query', views.submit_query, name='submit-query')
]

urlpatterns += htmx_urlpatterns
