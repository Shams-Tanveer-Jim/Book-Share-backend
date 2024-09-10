from rest_framework.permissions import BasePermission
from account.models import CustomUser

class BookReadWriteUpdatePermission(BasePermission):

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            
            if request.method == 'GET':
                return True
            else:
                if request.user.role != CustomUser.ROLE.USER:
                    return True
                else:
                    return False
        return False
        
        
