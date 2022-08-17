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
import os
import datetime
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, format_html_join
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.utils.safestring import mark_safe
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from .models import SiteUser, Membership

help_texts = (
	"different from your email",
	"at least 8 characters",
	"not a common password",
	"not entirely numeric"
)

help_items = format_html(
	mark_safe(_("Your password must be:<ul>{}</ul>")),
	format_html_join('', "<li>&nbsp;&nbsp;-&nbsp;{}</li>", ((_(text),) for text in help_texts))
)


# Create your forms here.
class UserRegistrationForm(UserCreationForm):
	email = forms.EmailField(required=True)
	if os.environ['DJANGO_SETTINGS_MODULE'] != 'config.test_settings':
		captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3)

	class Meta:
		model = SiteUser
		if os.environ['DJANGO_SETTINGS_MODULE'] == 'config.test_settings':
			fields = ('email', 'password1', 'password2')
		else:
			fields = ('email', 'password1', 'password2', 'captcha')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['password1'].help_text = help_items
		self.fields['password2'].help_text = _("Enter the same password again, for validation")

	def save(self, commit=True):
		user = super(UserRegistrationForm, self).save(commit=False)
		user.email = self.cleaned_data['email'].lower()
		user.set_password(self.clean_password2())
		if commit:
			user.save()
		return user


class UserLoginForm(AuthenticationForm):
	message_incorrect_login = _("Incorrect email or password. Please try again.")
	message_user_inactive = _("Your account is inactive. Please contact the site administrator.")

	class Meta:
		model = SiteUser
		fields = ('email', 'password')

	def clean(self):
		email = self.cleaned_data['username'].lower()  # Note that form returns 'username' despite model using 'email'
		password = self.cleaned_data['password']

		if email and password:
			self.user_cache = authenticate(email=email, password=password)
			if self.user_cache is None:
				raise forms.ValidationError(self.message_incorrect_login)
			if not self.user_cache.is_active:
				raise forms.ValidationError(self.message_user_inactive)
		return self.cleaned_data


class MembershipEditForm(forms.ModelForm):
	class Meta:
		model = Membership
		exclude = ['user']
		widgets = {
			'renewal_date': forms.widgets.DateInput(attrs={'type': 'date'}),
			'minimum_term': forms.widgets.DateInput(attrs={'type': 'date'}),
			'free_trial_expiry': forms.widgets.DateInput(attrs={'type': 'date'}),
		}
		labels = {'membership_type': "Subscription type", 'reminder': "E-mail reminders"}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.label_suffix = ""

	def clean(self):
		cleaned_data = super().clean()
		mem_type = cleaned_data.get('membership_type')
		renew_date = cleaned_data.get('renewal_date')
		cust_period = cleaned_data.get('custom_period')
		cust_unit = cleaned_data.get('custom_unit')
		mem_type_fmt = {
			'WEEKLY': "a weekly",
			'MONTHLY': "a monthly",
			'ANNUAL': "an annual",
			'FIXED': "a fixed-term",
			'LIFETIME': "a lifetime",
			'CUSTOM': "a custom"
		}
		validation_errors = []

		if mem_type != 'LIFETIME' and renew_date is None:
			validation_errors.append(forms.ValidationError(
				_(f"You have selected {mem_type_fmt[mem_type]} membership but have not set a renewal date."),
				code="incomplete"
			))
		elif mem_type != 'LIFETIME':
			if renew_date < datetime.date.today():
				validation_errors.append(forms.ValidationError(
					_(f"The renewal date cannot be in the past."),
					code="invalid"
				))

		if mem_type == 'CUSTOM' and (cust_period is None or cust_period == 0 or cust_unit is None):
			validation_errors.append(forms.ValidationError(
				_("You have selected a custom membership but have not set a valid custom period."),
				code="incomplete"
			))

		if validation_errors:
			raise forms.ValidationError(validation_errors)

		if mem_type == 'LIFETIME':
			cleaned_data['renewal_date'] = None
		if mem_type != 'CUSTOM':
			cleaned_data['custom_period'] = None
			cleaned_data['custom_unit'] = None
		return cleaned_data


class ContactForm(forms.Form):
	email = forms.EmailField(required=True, label="Your e-mail")
	subject = forms.CharField(required=True, max_length=50)
	message = forms.CharField(required=True, max_length=400, widget=forms.Textarea)
	if os.environ['DJANGO_SETTINGS_MODULE'] != 'config.test_settings':
		captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3)


class CaptchaPasswordResetForm(PasswordResetForm):
	if os.environ['DJANGO_SETTINGS_MODULE'] != 'config.test_settings':
		captcha = ReCaptchaField(label='', label_suffix='', widget=ReCaptchaV3)

	class Meta:
		if os.environ['DJANGO_SETTINGS_MODULE'] == 'config.test_settings':
			fields = ('email',)
		else:
			fields = ('email', 'captcha')