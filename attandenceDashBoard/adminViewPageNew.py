from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
import json, datetime
from .models import MonthlyHolidays, SalaryOfEveryPerson, Department, employeeRecordEveryMonth
from .salaryServices import AdminSalaryServices, AttandenceService

class AdminViewPage:
    @csrf_exempt
    def getEmployeeListSalaryObject(request):
        AdminSalaryServices().createAllEmployeesSalary()
        
        depart_id = request.POST.get('departId') or request.GET.get('departId')
        
        if request.method == "POST" and request.POST.get('empId'):
            emp_id = request.POST.get('empId')
            salary = request.POST.get('salary')
            SalaryOfEveryPerson.objects.filter(emp__empId=emp_id).update(salaryPerMonth=salary)

        employees = SalaryOfEveryPerson.objects.all()
        if depart_id:
            employees = employees.filter(emp__deprt__id=depart_id)

        return render(request, "allEmployeeSalarylist.html", {
            'allEmployees': employees, 
            'departments': Department.objects.all()
        })

    @csrf_exempt
    def getSaleryOfEmployeeToPaid(request):
        month_str = request.POST.get('month') or datetime.date.today().strftime("%Y-%m")
        depart_id = request.POST.get('departId')
        
        if request.method == "POST":
            allow_leave = request.POST.get('leave')
            emp_id = request.POST.get('empId')
            
            if emp_id and allow_leave:
                AttandenceService().leaveTaken(month_str, emp_id, allow_leave)
            
            AdminSalaryServices().createEveryMonthRecordofAll(month_str)

        records = employeeRecordEveryMonth.objects.filter(monthDate=datetime.datetime.strptime(month_str, "%Y-%m"))
        if depart_id:
            records = records.filter(employee__deprt__id=depart_id)

        return render(request, 'employeesSalaryToPaid.html', {
            'allemployeesMonthData': records,
            'departments': Department.objects.all(),
            'month_str': month_str,
            'departId': depart_id
        })