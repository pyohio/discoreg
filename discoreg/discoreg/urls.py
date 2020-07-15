from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("registrations/", include("registrations.urls")),
    path("admin/", admin.site.urls),
    ]
