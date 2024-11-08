from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):
    """
    Allows access only to super users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsStaffOrReadOnly(BasePermission):
    """
    The request is staff member, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsDashboard(BasePermission):
    """
    Users must be authenticated and can only request info about them selves
    Except for admin
    """

    def has_permission(self, request, view):
        if str(request.user) == 'admin':
            return True
        else:
            return bool(str(request.user) == str(request.GET.get('name', None)))

# kholase :
# faghat staff mitonan unsafe method befrestan
# faghat superuser mitone student_list ro bebine
# faghat khode user mitone object student khodesh ro bebine & admin mitone har object ro bebine
