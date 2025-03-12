from rest_framework.permissions import BasePermission
from .models import Teachers, Students, Classrooms
from rest_framework.exceptions import PermissionDenied

class HasAccessToGurukul(BasePermission):
    """

    Custom permission to check if the user has acess at view level
    
    """
    def has_permission(self, request, view):

        is_teacher = True if Teachers.objects.filter(user = request.user, classroom__id=view.kwargs.get('id')).exists() else False
        is_student = True if Students.objects.filter(user = request.user, classroom__id=view.kwargs.get('id')).exists() else False
        
        if is_student or is_teacher:
            print(is_student,is_teacher)
            return True

    """

    Custom permission to check if the user has access to a particular Gurukul.
    
    """
    def has_object_permission(self, request, view, obj):

        is_teacher = True if Teachers.objects.filter(user = request.user, classroom__id=obj.id).exists() else False
        is_student = True if Students.objects.filter(user = request.user, classroom__id=obj.id).exists() else False

        if is_student or is_teacher:
            print(is_student,is_teacher)
            return True
        
    

class IsGurukulTeacher(BasePermission):
    """

    Custom permission to check if the user is teacher to a given gurukul Gurukul.
    
    """

    def has_permission(self, request, view):
        is_teacher = True if Teachers.objects.filter(user = request.user, classroom__id=view.kwargs.get('id')).exists() else False
        return is_teacher
    """

    Custom permission to check if the user is teacher to a given gurukul Gurukul.
    
    """
    def has_object_permission(self, request, view, obj):

        is_teacher = True if Teachers.objects.filter(user = request.user, classroom__id=obj.id).exists() else False
        print(is_teacher)
        return is_teacher


class IsGurukulStudent(BasePermission):

    """

    Custom permission to check if the user is teacher to a given gurukul Gurukul.
    
    """
    def has_permission(self, request, view):
        is_student = True if Students.objects.filter(user = request.user, classroom__id=view.kwargs.get('id')).exists() else False
        # print(is_student)
        return is_student
    """

    Custom permission to check if the user is teacher to a given gurukul Gurukul.
    
    """
    def has_object_permission(self, request, view, obj):

        is_student = True if Students.objects.filter(user = request.user, classroom__id=obj.id).exists() else False
        print(is_student)
        return is_student


class IsOwner(BasePermission):
    """
    Custom permission to allow only owners of an object to access or edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming the object has an `owner` attribute
        return obj.creator == request.user



def method_permission(permission_class):
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            # Instantiate and check the custom permission
            permission = permission_class()
            if not permission.has_permission(request, self):
                raise PermissionDenied(detail="You do not have permission to perform this action.")
            # Call the original method if permission passes
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator
