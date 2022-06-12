import datetime
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, format_html_join
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, Row, Column, Div
from .models import SiteUser, Membership

help_texts = ("different from your email",
              "at least 8 characters",
              "not a common password",
              "not entirely numeric")

help_items = format_html(
    mark_safe(_("Your password must be:<ul>{}</ul>")),
    format_html_join('', "<li>&nbsp;&nbsp;-&nbsp;{}</li>", ((_(text),) for text in help_texts))
)


# Create your forms here.
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = SiteUser
        fields = ('email', 'password1', 'password2')

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
        fields = {"email", "password"}

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
        labels = {'reminder': "E-mail reminders"}

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
        return self.cleaned_data
