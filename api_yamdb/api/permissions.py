from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrSuperUser(BasePermission):
    """Доступ админу и суперюзеру, для эндпоинта 'users'."""

    def has_permission(self, request, view):
        return (
            not request.user.is_anonymous
            and request.user.is_admin_or_super_user
        )


class IsAdmimOrReadOnly(BasePermission):
    """У всех, кроме админа и суперюзера, права только на чтение."""
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or not request.user.is_anonymous
            and (request.user.is_admin_or_super_user)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or not request.user.is_anonymous
            and (request.user.is_admin_or_super_user)
        )


class IsAdmimOrModeratorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (
            not request.user.is_anonymous
            or request.method in SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or not request.user.is_anonymous
            and request.user.is_moderator_or_admin_or_super_user
            or obj.author == request.user
        )
