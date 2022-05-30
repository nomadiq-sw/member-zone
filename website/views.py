from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import View, TemplateView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import BadHeaderError, send_mail
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q
from .forms import UserRegistrationForm, UserLoginForm
from .models import SiteUser


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'


class MembershipView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'memberships.html'


class LoginSignupView(View):

    def get(self, request):
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
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'MemberZone',
                        'protocol': 'http',
                    }
                    html_content = html_temp.render(c)
                    try:
                        send_mail(subject, html_content, "admin@member-zone.com", [user.email])
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
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'MemberZone',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    html_content = html_temp.render(c)
                    try:
                        send_mail(subject, html_content, "admin@member-zone.com", [user.email])
                        return HttpResponseRedirect(reverse('password-reset-done'))
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
            else:
                return HttpResponseRedirect(reverse('password-reset-invalid'))
        else:
            return HttpResponseRedirect(reverse('login'))
