from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm, UserLoginForm


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
                    return HttpResponseRedirect(reverse('my-memberships'))
            context = {'register_form': register_form, 'login_form': UserLoginForm()}
            return render(request, 'registration/login.html', context)

        elif request.POST.get('submit') == 'Login':
            login_form = UserLoginForm(data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                return HttpResponseRedirect(reverse('my-memberships'))
            context = {'register_form': UserRegistrationForm(), 'login_form': login_form}
            return render(request, 'registration/login.html', context)

        return HttpResponseRedirect(reverse('login'))
