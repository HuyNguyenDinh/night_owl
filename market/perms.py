from rest_framework import permissions

class NightOwlPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated() and request.user.is_staff

class BusinessPermission(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated() and request.user.is_business

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user and request.user.is_authenticated()