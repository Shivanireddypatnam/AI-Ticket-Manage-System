from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'ADMIN'
        )


class IsCustomerRole(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'CUSTOMER'
        )



class IsAgentRole(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'AGENT'
        )