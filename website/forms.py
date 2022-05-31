import datetime
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, format_html_join
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.safestring import mark_safe
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

    def clean(self):
        cleaned_data = super().clean()
        mem_type = cleaned_data.get('membership_type')
        date = cleaned_data.get('renewal_date')
        period = cleaned_data.get('custom_period')

        if mem_type != 'LIFETIME' and date is None:
            raise forms.ValidationError(
                _("You have selected a %(type) membership but have not set a renewal date."),
                params={'type': mem_type},
                code="missing date"
            )
        elif mem_type != 'LIFETIME':
            self.present_or_future_date("renewal", date)

        if mem_type == 'CUSTOM' and period is None:
            raise forms.ValidationError(
                _("You have selected a CUSTOM membership but have not set a custom period"),
                code="missing date"
            )

    @staticmethod
    def present_or_future_date(field, date):
        if date < datetime.date.today():
            raise forms.ValidationError(
                _("The %(field) date cannot be in the past!"),
                params={'field': field},
                code="invalid date"
            )
