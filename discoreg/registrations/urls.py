from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("callback", views.callback, name="callback"),
    path("link", views.link, name="link"),
    path("tito-webhook", views.tito_webhook, name="tito-webhook"),
]
