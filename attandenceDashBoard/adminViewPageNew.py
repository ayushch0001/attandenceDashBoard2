from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from attandenceDashBoard.models import MonthlyHolidays, SalaryOfEveryPerson ,Department , employeeRecordEveryMonth
from attandenceDashBoard.salaryServices import AdminSalaryServices, AttandenceService
import datetime  
from datetime import date
from django.http import JsonResponse
import json

class AdminViewPage:
    @csrf_exempt
    def getEmployeeListSalaryObject(request):
        service = AdminSalaryServices()
        service.createAllEmployeesSalary()  # Ensure salaries are created before queries

        if request.method == "POST":
        
            employeeId = request.POST.get('empId')
            salary = request.POST.get('salary')
            departId = request.POST.get('departId')
            

            empSalary = SalaryOfEveryPerson.objects.filter(emp__empId=employeeId).first()
            
            if empSalary:  # Only update if the record exists
                empSalary.salaryPerMonth = salary
                empSalary.save()

            allemployeesalary = SalaryOfEveryPerson.objects.filter(emp__deprt__id = departId) if departId else SalaryOfEveryPerson.objects.all()
            departments = Department.objects.all()
            return render(
                request,
                "allEmployeeSalarylist.html",
                {'allEmployees': allemployeesalary, 'departments': departments}
            )

        # GET request case
        departId = request.POST.get('departId')
        allemployeesalary = SalaryOfEveryPerson.objects.filter(emp_deprt=departId) if departId else SalaryOfEveryPerson.objects.all()
        
        departments = Department.objects.all()
        return render(
            request,
            "allEmployeeSalarylist.html",
            {'allEmployees': allemployeesalary, 'departments': departments}
        )

    @csrf_exempt
    def getSaleryOfEmployeeToPaid(request):
        if request.method == "POST":
            month_str = request.POST.get('month')
            allowLeave = request.POST.get('leave')
            empId = request.POST.get('empId')
            departId = request.POST.get('departId')
            

            if empId and allowLeave: 
                AttandenceService().leaveTaken(month_str,empId,allowLeave)

            
            services = AdminSalaryServices()
            services.createEveryMonthRecordofAll(month_str)
            month  = datetime.datetime.strptime(month_str, "%Y-%m") 
            allemployeesMonthData =  employeeRecordEveryMonth.objects.filter(monthDate = month,employee__deprt__id = departId) if departId and month_str else employeeRecordEveryMonth.objects.all()
            departments = Department.objects.all()
            return render(request,'employeesSalaryToPaid.html',{'allemployeesMonthData':allemployeesMonthData ,'departments':departments,'month_str':month_str,'departId':departId})
        

        month = datetime.date(datetime.date.today().year,datetime.date.today().month,1)
        allemployeesMonthData =  employeeRecordEveryMonth.objects.filter(monthDate = month)
        departments = Department.objects.all()
        return render(request,'employeesSalaryToPaid.html',{'allemployeesMonthData':allemployeesMonthData ,'departments':departments})


    @csrf_exempt
    def addMonthlyHoliday(request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                month = int(data["month"])   # 1–12
                year  = int(data["year"])
                holidays = int(data["holidays"])

                month_date = date(year, month, 1)

                obj, created = MonthlyHolidays.objects.get_or_create(
                    monthName=month_date,
                    defaults={"holidayPerMonth": holidays}
                )

                if not created:
                    return JsonResponse({"status": "error", "msg": "Month already exists"}, status=400)

                return JsonResponse({"status": "success", "msg": "Monthly holiday added"})

            except Exception as e:
                return JsonResponse({"status": "error", "msg": str(e)}, status=500)
    
    @csrf_exempt
    def updateMonthlyHoliday(request):
        if request.method == "PUT":
            try:
                data = json.loads(request.body)
                month = int(data["month"])
                year  = int(data["year"])
                holidays = int(data["holidays"])

                month_date = date(year, month, 1)

                obj = MonthlyHolidays.objects.filter(monthName=month_date).first()
                if not obj:
                    return JsonResponse({"status": "error", "msg": "Month not found"}, status=404)

                obj.holidayPerMonth = holidays
                obj.save()

                return JsonResponse({"status": "success", "msg": "Monthly holiday updated"})

            except Exception as e:
                return JsonResponse({"status": "error", "msg": str(e)}, status=500)
