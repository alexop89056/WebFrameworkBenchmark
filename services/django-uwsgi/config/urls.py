from django.http import JsonResponse
from django.urls import path


def hello(request):
    return JsonResponse({"message": "hello", "framework": "django-uwsgi"})


urlpatterns = [path("", hello)]
