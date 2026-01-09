from django.urls import path
from .views import SaveNoteView

urlpatterns = [
    path('save-note/', SaveNoteView.as_view(), name='save_note'),
]