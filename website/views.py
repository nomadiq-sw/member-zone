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
import datetime
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import View, TemplateView, ListView
from django.views.generic.edit import DeleteView, UpdateView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import BadHeaderError, send_mail
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q
from django.db.models.functions import Lower

import config.settings
from .forms import UserRegistrationForm, UserLoginForm, MembershipEditForm, ContactForm
from .models import SiteUser, Membership


# Create your views here.
class IndexView(TemplateView):
	template_name = 'index.html'
	today = datetime.date.today()
	dummy_data = [
		{'name': "NordVPN", 'period': "Monthly", 'date': today + datetime.timedelta(days=11), 'cost': "$11.99"},
		{'name': "Netflix", 'period': "Monthly", 'date': today + datetime.timedelta(days=5), 'cost': "$14.99"},
		{'name': "LA Fitness", 'period': "Annual", 'date': today + datetime.timedelta(days=99), 'cost': "$580.00"},
		{'name': "Fight Club", 'period': "Lifetime", 'date': "--", 'cost': "$999.99"}
	]
	extra_context = {'data': dummy_data}


class MembershipView(LoginRequiredMixin, TemplateView):
	template_name = 'memberships.html'
	extra_context = {'form': MembershipEditForm()}

	def post(self, request, *args, **kwargs):
		form = MembershipEditForm(request.POST)
		success = False
		if form.is_valid():
			membership = form.save(commit=False)
			if kwargs:
				if kwargs['update']:
					membership.pk = kwargs['pk']
			membership.user = request.user
			membership.save()
			success = True
			self.request.path = reverse_lazy('my-memberships')
			form = MembershipEditForm()

		response = render(request, 'partials/modal-form.html', {'form': form})
		if success:
			response['HX-Trigger'] = 'membershipsChanged'
		return response


class MembershipTableView(LoginRequiredMixin, ListView):
	model = Membership
	template_name = 'partials/membership-table.html'

	def get_queryset(self):
		return Membership.objects.filter(Q(user=self.request.user)).order_by(Lower('membership_name'), '-renewal_date')


@login_required()
def toggle_reminders(request, pk):
	if request.method == 'PATCH':
		membership = Membership.objects.get(pk=pk)
		if membership.user == request.user:
			membership.reminder = not membership.reminder
			membership.save()


class DeleteMembershipView(LoginRequiredMixin, DeleteView):
	model = Membership

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.user == self.request.user:
			self.object.delete()
			return HttpResponse()
			# Unfortunately we cannot return status 204 or else htmx will ignore the response (see docs at htmx.org)
		return redirect('my-memberships')


class EditMembershipView(LoginRequiredMixin, UpdateView):
	model = Membership
	fields = "__all__"
	template_name = 'partials/modal-form.html'

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.user == request.user:
			return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.user == request.user:
			return MembershipView.as_view()(request, update=True, pk=self.object.pk)


class AboutView(TemplateView):
	template_name = 'about.html'

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			data = {'email': request.user.email}
		else:
			data = None
		self.extra_context = {'form': ContactForm(initial=data)}
		return super().get(request, *args, **kwargs)


def submit_query(request):
	pass


class LoginSignupView(View):

	def get(self, request):
		if request.user.is_authenticated:
			return HttpResponseRedirect(reverse('my-memberships'))
		register_form = UserRegistrationForm()
		login_form = UserLoginForm()
		context = {'register_form': register_form, 'login_form': login_form}
		return render(request, 'registration/login.html', context)

	def post(self, request):

		if request.POST.get('submit') == 'Register':
			register_form = UserRegistrationForm(request.POST)
			if register_form.is_valid():
				user = register_form.save()
				if user is not None and user.is_active:
					login(request, user)
					subject = "Welcome to MemberZone"
					html_temp = get_template('registration/user_welcome_email.html')
					c = {
						'protocol': config.settings.PROTOCOL,
						'domain': config.settings.DOMAIN,
					}
					html_content = html_temp.render(c)
					try:
						send_mail(subject, html_content, "noreply@member-zone.com", [user.email])
						return HttpResponseRedirect(reverse('my-memberships'))
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
			context = {'register_form': register_form, 'login_form': UserLoginForm()}
			return render(request, 'registration/login.html', context)

		elif request.POST.get('submit') == 'Log in':
			login_form = UserLoginForm(data=request.POST)
			if login_form.is_valid():
				login(request, login_form.get_user())
				return HttpResponseRedirect(reverse('my-memberships'))
			context = {'register_form': UserRegistrationForm(), 'login_form': login_form}
			return render(request, 'registration/login.html', context)

		return HttpResponseRedirect(reverse('login'))


class PasswordResetView(View):

	def get(self, request):
		if request.user.is_authenticated:
			return HttpResponseRedirect(reverse('logout'))
		pwd_reset_form = PasswordResetForm()
		return render(request, 'registration/password_reset.html', context={'password_reset_form': pwd_reset_form})

	def post(self, request):
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			email = password_reset_form.cleaned_data['email']
			users = SiteUser.objects.filter(Q(email=email))
			if users.exists():
				for user in users:
					subject = "Password reset requested"
					html_temp = get_template('registration/password_reset_email.html')
					c = {
						'protocol': config.settings.PROTOCOL,
						'domain': config.settings.DOMAIN,
						"uid": urlsafe_base64_encode(force_bytes(user.pk)),
						'token': default_token_generator.make_token(user),
					}
					html_content = html_temp.render(c)
					try:
						send_mail(subject, html_content, "noreply@member-zone.com", [user.email])
						return HttpResponseRedirect(reverse('password-reset-done'))
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
			else:
				return HttpResponseRedirect(reverse('password-reset-invalid'))
		else:
			return HttpResponseRedirect(reverse('login'))
