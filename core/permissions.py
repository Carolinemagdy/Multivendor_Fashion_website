from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    """
    Allows access only to vendor users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_vendor)
class IsCustomer(BasePermission):
    """
    Allows access only to customer users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_customer)