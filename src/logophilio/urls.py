from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path("flashcard/", include("apps.flashcards.urls"), name="flashcard"),
    path("admin/", admin.site.urls, name="admin"),
    re_path(r"^s3direct/", include("s3direct.urls")),
]
