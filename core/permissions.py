from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    """
    Allows access only to vendor users and superuser.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_vendor )
    
class IsCustomer(BasePermission):
    """
    Allows access only to customer users and superuser.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_customer )
    
class IsSuperuser(BasePermission):
    """
    Allows access only to Superuser.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
    
class IsSuperuserOrVendor(BasePermission):
    """
    Allows access to Superuser and vendors.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_superuser or request.user.is_vendor))
class IsSuperuserOrCustomer(BasePermission):
    """
    Allows access to Superuser and customers.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_superuser or request.user.is_customer))
class IsVendorOrCustomer(BasePermission):
    """
    Allows access to Superuser and customers.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_vendor or request.user.is_customer))
