from django.views.generic import FormView, TemplateView


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'