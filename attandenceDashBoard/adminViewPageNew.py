import json
import datetime
from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from attandenceDashBoard.models import (
    MonthlyHolidays, SalaryOfEveryPerson, 
    Department, employeeRecordEveryMonth
)
from attandenceDashBoard.salaryServices import AdminSalaryServices, AttandenceService

class AdminViewPage:
    
    @staticmethod
    @csrf_exempt
    def getEmployeeListSalaryObject(request):
        """View to list and update base monthly salaries for employees."""
        service = AdminSalaryServices()
        service.createAllEmployeesSalary()  # Sync records

        # Handle Salary Update via POST
        if request.method == "POST":
            employee_id = request.POST.get('empId')
            salary_amount = request.POST.get('salary')
            
            if employee_id and salary_amount:
                SalaryOfEveryPerson.objects.filter(
                    emp__empId=employee_id
                ).update(salaryPerMonth=salary_amount)

        # Filtering logic for both GET and POST
        depart_id = request.POST.get('departId') or request.GET.get('departId')
        
        salary_query = SalaryOfEveryPerson.objects.select_related('emp', 'emp__deprt').all()
        if depart_id and depart_id != "0":
            salary_query = salary_query.filter(emp__deprt__id=depart_id)

        context = {
            'allEmployees': salary_query,
            'departments': Department.objects.all(),
            'selected_depart': depart_id
        }
        return render(request, "allEmployeeSalarylist.html", context)

    @staticmethod
    @csrf_exempt
    def getSaleryOfEmployeeToPaid(request):
        """View to calculate and list the final payable salary for a specific month."""
        month_str = request.POST.get('month')
        depart_id = request.POST.get('departId')
        
        if request.method == "POST" and month_str:
            allow_leave = request.POST.get('leave')
            emp_id = request.POST.get('empId')

            # 1. Update allowed leaves if provided
            if emp_id and allow_leave:
                AttandenceService().leaveTaken(month_str, emp_id, allow_leave)

            # 2. Process attendance logic and generate monthly records
            services = AdminSalaryServices()
            services.createEveryMonthRecordofAll(month_str)

            # 3. Filter data for display
            target_month = datetime.datetime.strptime(month_str, "%Y-%m").date()
            record_query = employeeRecordEveryMonth.objects.filter(monthDate=target_month)
            
            if depart_id and depart_id != "0":
                record_query = record_query.filter(employee__deprt__id=depart_id)
        else:
            # Default to current month for GET requests
            target_month = date(date.today().year, date.today().month, 1)
            record_query = employeeRecordEveryMonth.objects.filter(monthDate=target_month)

        context = {
            'allemployeesMonthData': record_query,
            'departments': Department.objects.all(),
            'month_str': month_str,
            'departId': depart_id
        }
        return render(request, 'employeesSalaryToPaid.html', context)

    @staticmethod
    @csrf_exempt
    def addMonthlyHoliday(request):
        """API to add a new holiday count for a specific month."""
        if request.method != "POST":
            return JsonResponse({"status": "error", "msg": "POST required"}, status=405)
            
        try:
            data = json.loads(request.body)
            month_date = date(int(data["year"]), int(data["month"]), 1)

            obj, created = MonthlyHolidays.objects.get_or_create(
                monthName=month_date,
                defaults={"holidayPerMonth": int(data["holidays"])}
            )

            if not created:
                return JsonResponse({"status": "error", "msg": "Month already exists"}, status=400)

            return JsonResponse({"