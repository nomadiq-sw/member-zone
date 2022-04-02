from django import forms
from django.contrib.auth import authenticate
from django.utils.html import format_html, format_html_join
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.safestring import mark_safe

from .models import SiteUser

help_texts = ("different from your email",
              "at least 8 characters",
              "not a common password",
              "not entirely numeric")

help_items = format_html(
    mark_safe("Your password must be:<ul>{}</ul>"),
    format_html_join('', "<li>&nbsp;&nbsp;-&nbsp;{}</li>", ((text,) for text in help_texts))
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
        self.fields['password2'].help_text = "Enter the same password again, for validation"

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.set_password(self.clean_password2())
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    message_incorrect_login = "Incorrect email or password. Please try again."
    message_user_inactive = "Your account is inactive. Please contact the site administrator."

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
