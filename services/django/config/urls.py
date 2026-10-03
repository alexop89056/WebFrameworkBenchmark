from django.http import JsonResponse
from django.urls import path


def hello(request):
    return JsonResponse({"message": "hello", "framework": "django"})


urlpatterns = [path("", hello)]
