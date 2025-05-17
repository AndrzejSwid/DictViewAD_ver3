from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Meaning
    show_reading = models.BooleanField(default=True)
    show_description = models.BooleanField(default=True)
    show_translations = models.BooleanField(default=True)
    show_sentences = models.BooleanField(default=True)
    show_sentences_translations = models.BooleanField(default=True)
    show_synonyms = models.BooleanField(default=True)

    max_column = models.IntegerField(default=4)

    def __str__(self):
        return self.user.username
