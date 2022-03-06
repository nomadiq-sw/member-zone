from django import forms
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
        user.email = self.cleaned_data['email']
        user.set_password(self.clean_password2())
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = SiteUser
        fields = {"email", "password"}
