import os

settings_code = """
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me-now")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "snapmemo_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "snapmemo_backend.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
"""

models_code = """
from django.db import models


class Note(models.Model):
    content = models.TextField()
    device_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    user_photo = models.ImageField(upload_to="captures/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note {self.id} - {self.created_at}"
"""

serializers_code = """
from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ("id", "created_at")
"""

views_code = """
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NoteSerializer
from .models import Note


class SaveNoteView(APIView):
    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            note = serializer.save()

            # Count per device when provided; otherwise fall back to total notes.
            if note.device_id:
                count = Note.objects.filter(device_id=note.device_id).count()
            else:
                count = Note.objects.count()

            message = "Note Saved Successfully!"
            reward = False

            if count % 10 == 0:
                message = f"Congratulations! You reached {count} notes. Reward unlocked!"
                reward = True

            return Response(
                {
                    "status": "success",
                    "message": message,
                    "reward": reward,
                    "total_notes": count,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@staff_member_required
def dashboard_view(request):
    notes = Note.objects.all().order_by("-created_at")
    return render(request, "dashboard.html", {"notes": notes})
"""

api_urls_code = """
from django.urls import path
from .views import SaveNoteView

urlpatterns = [
    path("save-note/", SaveNoteView.as_view(), name="save_note"),
]
"""

main_urls_code = """
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.views import dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content.strip() + "\n")
    print(f"Created: {path}")


if __name__ == "__main__":
    write_file("snapmemo_backend/settings.py", settings_code)
    write_file("api/models.py", models_code)
    write_file("api/serializers.py", serializers_code)
    write_file("api/views.py", views_code)
    write_file("api/urls.py", api_urls_code)
    write_file("snapmemo_backend/urls.py", main_urls_code)
    print("Backend files generated successfully.")
