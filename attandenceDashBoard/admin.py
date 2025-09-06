from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from attandenceDashBoard.models import Attandence, CustomUserFace, StoreFaces, EmployeeRegistration ,Department,employeeRecordEveryMonth,SalaryOfEveryPerson,LeaveManagement,Failedattandence

@admin.register(CustomUserFace)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('department','phonenumber')}),
    )
    
    
admin.site.register(StoreFaces)
admin.site.register(Attandence)
admin.site.register(EmployeeRegistration)
admin.site.register(Department)
admin.site.register(employeeRecordEveryMonth)
admin.site.register(SalaryOfEveryPerson)
admin.site.register(LeaveManagement)
admin.site.register(Failedattandence)
