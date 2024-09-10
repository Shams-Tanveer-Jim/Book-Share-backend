from django.contrib import admin
from django import forms
from .models import CustomUser,User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

@admin.register(CustomUser)
class CustomUserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("password",)}),
        (("Personal info"), {"fields": ("name", "email", "phone")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),    
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "name", "phone","role")}),)
    list_display = ("email", "name", "is_staff", "is_active")  
    search_fields = ("name", "email", "phone")
    ordering = ("name", "email")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role__in=[CustomUser.ROLE.ADMISTRATIVEADMIN,CustomUser.ROLE.ADMIN]) 



@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("password",)}),
        (("Personal info"), {"fields": ("name", "email", "phone")}),
        (_("Permissions"), {"fields": ("is_active", "groups", "user_permissions")}),    
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "name", "phone")}),)
    list_display = ("email", "name",)  
    search_fields = ("name", "email", "phone")
    ordering = ("name", "email")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role=CustomUser.ROLE.USER)
   


