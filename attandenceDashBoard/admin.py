from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from attandenceDashBoard.models import Attandence, CustomUserFace, StoreFaces, EmployeeRegistration ,Department

@admin.register(CustomUserFace)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('department','phonenumber')}),
    )
    
    
admin.site.register(StoreFaces)
admin.site.register(Attandence)
admin.site.register(EmployeeRegistration)
admin.site.register(Department)