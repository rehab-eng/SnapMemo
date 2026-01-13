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
    return render(request, "api/dashboard.html", {"notes": notes})
