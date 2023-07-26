from django.urls import path

from . import views

urlpatterns = [
    path("generate/<str:word>", views.Generate.as_view(), name="generate"),
]
