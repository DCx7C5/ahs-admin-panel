from rest_framework.permissions import BasePermission


class CanReactViewTerminal(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.filter(pk=request.user.pk).exists()
