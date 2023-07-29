from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("words/", include("apps.words.urls"), name="word"),
    path("flashcards/", include("apps.flashcards.urls"), name="flashcard"),
    path("admin/", admin.site.urls, name="admin"),
]
