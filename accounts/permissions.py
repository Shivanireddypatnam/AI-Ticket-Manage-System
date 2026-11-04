from rest_framework.permissions import BasePermission


def user_has_role(user, role):
    if not user or not user.is_authenticated:
        return False
    profile = getattr(user, "profile", None)
    return profile is not None and profile.role == role


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, "ADMIN")


class IsAgentRole(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, "AGENT")


class IsCustomerRole(BasePermission):
    def has_permission(self, request, view):
        return user_has_role(request.user, "CUSTOMER")


class IsAdminOrAgentRole(BasePermission):
    def has_permission(self, request, view):
        return (
            user_has_role(request.user, "ADMIN")
            or user_has_role(request.user, "AGENT")
        )
