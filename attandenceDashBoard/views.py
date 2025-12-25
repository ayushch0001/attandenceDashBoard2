import json
import base64
import calendar
from io import BytesIO
from datetime import date, datetime, timedelta, time

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Local Imports
from .models import (
    Attandence, Department, SalaryOfEveryPerson, 
    employeeRecordEveryMonth, MonthlyHolidays, EmployeeRegistration
)
from .forms import EmployeeRegistrationForm
from .salaryServices import AdminSalaryServices, AttandenceService, SalaryServices
from attandenceDashBoard.service import (
    create_all_months_absent_objects_till_today,
    createAttandenceOfAllEmployeeOfDate,
    get_employee_attendance_current_month
)

# --- Helpers ---

def is_admin(user):
    return user.is_superuser

def save_base64_image(data):
    if data and ';base64,' in data:
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), name=f"captured.{ext}")
    return None

# --- Auth & User Management ---

@login_required
@user_passes_test(is_admin)
def register(request):
    departments = Department.objects.all()
    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_page')
    else:
        form = EmployeeRegistrationForm()
    
    return render(request, 'EmployeeSection/employeeRegistration.html', {
        'departments': departments,
        'form': form
    })

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        u, p = request.POST.get('username'), request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('success_page')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('success_page')

# --- Attendance Logic ---

@csrf_exempt
def markAttandence(request):
    if request.method != 'POST':
        return render(request, 'attendence2.html')

    emp_id = request.POST.get('empId')
    action = request.POST.get('actionType')
    clicked_img = request.POST.get('clickedImg')
    address = request.POST.get('address')
    
    employee = EmployeeRegistration.objects.filter(empId=emp_id).first()
    if not employee:
        return JsonResponse({'namesList': [f"No employee found with ID: {emp_id}"]})

    today = date.today()
    current_time = datetime.now().time()
    sigin_image = save_base64_image(clicked_img)

    if action == 'signin':
        attendance, created = Attandence.objects.get_or_create(
            emp=employee, date=today,
            defaults={'singInTime': current_time, 'mark': True, 'location': address, 'siginImage': sigin_image}
        )
        msg = f"{employee.name} - Signed In" if created else f"{employee.name} - Already Signed In"
        return JsonResponse({'namesList': [msg]})

    elif action == 'signout':
        target_date = today
        if employee.shift == "NIGHT" and current_time < time(12, 0):
            target_date = today - timedelta(days=1)
        
        obj = Attandence.objects.filter(emp=employee, date=target_date).first()
        if obj:
            obj.singoutTime = current_time
            obj.save()
            return JsonResponse({'namesList': [f"{employee.name} - Signed Out"]})
        return JsonResponse({'namesList': ["No Sign In record found"]})

    return JsonResponse({'namesList': ["Invalid Action"]})

# --- Salary & Admin Views ---

class AdminViewPage:
    @csrf_exempt
    def getEmployeeListSalaryObject(request):
        service = AdminSalaryServices()
        service.createAllEmployeesSalary()

        departId = request.POST.get('departId') or request.GET.get('departId')
        
        if request.method == "POST":
            employeeId = request.POST.get('empId')
            salary = request.POST.get('salary')
            if employeeId and salary:
                SalaryOfEveryPerson.objects.filter(emp__empId=employeeId).update(salaryPerMonth=salary)

        allemployeesalary = SalaryOfEveryPerson.objects.all()
        if departId:
            allemployeesalary = allemployeesalary.filter(emp__deprt__id=departId)

        return render(request, "allEmployeeSalarylist.html", {
            'allEmployees': allemployeesalary, 
            'departments': Department.objects.all()
        })

    @csrf_exempt
    def getSaleryOfEmployeeToPaid(request):
        month_str = request.POST.get('month') or date.today().strftime("%Y-%m")
        departId = request.POST.get('departId')
        
        if request.method == "POST":
            allowLeave = request.POST.get('leave')
            empId = request.POST.get('empId')
            if empId and allowLeave: 
                AttandenceService().leaveTaken(month_str, empId, allowLeave)

            AdminSalaryServices().createEveryMonthRecordofAll(month_str)

        month_dt = datetime.strptime(month_str, "%Y-%m")
        allemployeesMonthData = employeeRecordEveryMonth.objects.filter(monthDate=month_dt)
        if departId:
            allemployeesMonthData = allemployeesMonthData.filter(employee__deprt__id=departId)

        return render(request, 'employeesSalaryToPaid.html', {
            'allemployeesMonthData': allemployeesMonthData,
            'departments': Department.objects.all(),
            'month_str': month_str,
            'departId': departId
        })

# --- Holiday Management (Completed) ---

    @csrf_exempt
    def manageMonthlyHolidays(request):
        """View to list all holidays (The missing Read part)"""
        holidays = MonthlyHolidays.objects.all().order_by('-monthName')
        return render(request, 'manageHolidays.html', {'holidays': holidays})

    @csrf_exempt
    def addMonthlyHoliday(request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                month_date = date(int(data["year"]), int(data["month"]), 1)
                obj, created = MonthlyHolidays.objects.get_or_create(
                    monthName=month_date, defaults={"holidayPerMonth": int(data["holidays"])}
                )
                if not created:
                    return JsonResponse({"status": "error", "msg": "Month already exists"}, status=400)
                return JsonResponse({"status": "success", "msg": "Holiday added"})
            except Exception as e:
                return JsonResponse({"status": "error", "msg": str(e)}, status=500)

    @csrf_exempt
    def updateMonthlyHoliday(request):
        if request.method == "PUT":
            try:
                data = json.loads(request.body)
                month_date = date(int(data["year"]), int(data["month"]), 1)
                obj = MonthlyHolidays.objects.filter(monthName=month_date).first()
                if not obj:
                    return JsonResponse({"status": "error", "msg": "Month not found"}, status=404)
                obj.holidayPerMonth = int(data["holidays"])
                obj.save()
                return JsonResponse({"status": "success", "msg": "Updated"})
            except Exception as e:
                return JsonResponse({"status": "error", "msg": str(e)}, status=500)

# --- Exports & Utilities ---

@login_required
@user_passes_test(is_admin)
def export_attendance_to_excel(request):
    selected_date = request.GET.get('date')
    if not selected_date:
        return JsonResponse({'error': 'Date missing'}, status=400)

    createAttandenceOfAllEmployeeOfDate(selected_date)
    records = Attandence.objects.filter(date=selected_date)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{selected_date}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    data = [['Employee', 'Date', 'Sign-in', 'Sign-out', 'Status']]
    for r in records:
        data.append([r.emp.name, str(r.date), str(r.singInTime or '-'), str(r.singoutTime or '-'), 'Present' if r.mark else 'Absent'])
    
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    doc.build([table])
    response.write(buffer.getvalue())
    return response

@csrf_exempt
def deleteEmployee(request):
    if request.method == 'DELETE':
        data = json.loads(request.body)
        deleted, _ = EmployeeRegistration.objects.filter(empId=data.get('empId')).delete()
        return JsonResponse({"success": bool(deleted)})
    return JsonResponse({"status": "Method not allowed"}, status=405)