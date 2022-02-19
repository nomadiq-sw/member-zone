from django.urls import path
from website import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('index/', views.IndexView.as_view(), name='index'),
]

htmx_urlpatterns = [
    path('alt_index/', views.alt_index, name='alt-index')
]

urlpatterns += htmx_urlpatterns