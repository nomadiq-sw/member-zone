from django.urls import path
from website import views

urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
]