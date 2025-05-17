from django.contrib import admin
from .models import *
from accounts.models import UserProfile

# Register your models here.
admin.site.register(Language)
admin.site.register(Dialect)
admin.site.register(Word)
admin.site.register(SpeechCategory)
admin.site.register(Meaning)
admin.site.register(GrammarNote)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Sentence)
admin.site.register(Text)
admin.site.register(Synonym)
admin.site.register(Meaning_Translation)
admin.site.register(Sentence_Translation)
admin.site.register(UserProfile)
admin.site.register(Scores)
