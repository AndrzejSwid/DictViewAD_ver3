from django.urls import path
from .views import *

urlpatterns = [
    path("login/", login_view, name="login_view"),
    path("register/", register_view, name="register_view"),
    # Preferences
    path("update_preferences/", preferences_view, name="preferences_view"),
]
