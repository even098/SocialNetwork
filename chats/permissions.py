from rest_framework import permissions

from chats.models import Chat


class IsParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        return request.user in obj.participants.all()
