from django.urls import path
from django.contrib.auth.views import LogoutView
from website import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('memberships/login', views.LoginSignupView.as_view(), name='login'),
    path('memberships/logout', LogoutView.as_view(), name='logout'),
    path('memberships/my-memberships/', views.MembershipView.as_view(), name='my-memberships'),
]

htmx_urlpatterns = []

urlpatterns += htmx_urlpatterns
