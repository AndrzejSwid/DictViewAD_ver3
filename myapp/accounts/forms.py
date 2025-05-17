from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "show_reading",
            "show_description",
            "show_translations",
            "show_sentences",
            "show_sentences_translations",
            "show_synonyms",
            "max_column",
        ]
