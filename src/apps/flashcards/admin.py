from django.contrib import admin
from .models import Flashcard, FlashcardStyle, Word, WordImage

admin.site.register(Flashcard)
admin.site.register(FlashcardStyle)
admin.site.register(Word)
admin.site.register(WordImage)
