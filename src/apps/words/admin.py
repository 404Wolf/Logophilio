from django.contrib import admin
from .models import Word, WordImage, WordImageConfig

admin.site.register(Word)
admin.site.register(WordImage)
admin.site.register(WordImageConfig)
