"""
URL configuration for core project.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import (
    include,
    path,
)

def home(request):
    return JsonResponse({
        "status": "ok",
        "service": "Geospatial AI Backend"
    })


urlpatterns = [
    path("", home),

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/",
        include("core_next.urls"),
    ),

]