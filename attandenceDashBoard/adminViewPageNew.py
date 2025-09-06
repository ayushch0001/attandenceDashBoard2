from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from attandenceDashBoard.models import SalaryOfEveryPerson ,Department , employeeRecordEveryMonth
from attandenceDashBoard.salaryServices import AdminSalaryServices, AttandenceService
import datetime  

class AdminViewPage:

    def getEmployeeListSalaryObject(request):
        service = AdminSalaryServices()
        service.createAllEmployeesSalary()  # Ensure salaries are created before queries

        if request.method == "POST":
        
            employeeId = request.POST.get('empId')
            salary = request.POST.get('salary')
            departId = request.POST.get('departId')
            

            empSalary = SalaryOfEveryPerson.objects.filter(emp__empId=employeeId).first()
            print('ye bhi hai ',empSalary.emp.name)
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
        # print(allemployeesalary)
        departments = Department.objects.all()
        return render(
            request,
            "allEmployeeSalarylist.html",
            {'allEmployees': allemployeesalary, 'departments': departments}
        )

    def getSaleryOfEmployeeToPaid(request):
        if request.method == "POST":
            month_str = request.POST.get('month')
            allowLeave = request.POST.get('leave')
            empId = request.POST.get('empId')
            departId = request.POST.get('departId')
            print(empId,'- ',departId,' -',allowLeave)

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


            

