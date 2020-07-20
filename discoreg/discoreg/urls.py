from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView


urlpatterns = [
    path(
        "registrations/",
        include(("registrations.urls", "registrations"), namespace="registrations"),
    ),
    path("admin/", admin.site.urls),
    path(
        "",
        RedirectView.as_view(pattern_name="registrations:index", permanent=False),
        name="registrations-redirect",
    ),
]
