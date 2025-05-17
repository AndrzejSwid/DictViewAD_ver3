"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from myapp.views import *

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Main Page
    path("", main_view, name="main_view"),
    # Accounts
    path("accounts/", include("accounts.urls")),
    # Database
    path("database/", database_view, name="database_view"),
    # Files
    path("excel/", excel_view, name="excel_view"),
    path("upload/", upload_view, name="upload"),
    path("download/", download_view, name="download"),
    # Games
    path("database/play/", play_view, name="play"),
    path("database/test/", test_view, name="test"),
    # Details
    path("text/<int:text_id>/", text_details_view, name="text_details_view"),
    path(
        "meaning/<int:meaning_id>/", meaning_details_view, name="meaning_details_view"
    ),
    path("save-scores", save_scores, name="save_scores"),
]
