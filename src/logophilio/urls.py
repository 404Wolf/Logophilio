from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("word/", include("apps.words.urls"), name="word"),
    path("flashcard/", include("apps.flashcards.urls"), name="flashcard"),
    path("admin/", admin.site.urls, name="admin"),
]
