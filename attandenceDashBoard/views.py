from datetime import date, datetime ,time ,timedelta
from PIL import Image 
from django.shortcuts import render, redirect
import os
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from attandenceDashBoard.service import calculateHours, countOfLateDays, create_all_months_absent_objects_till_today, create_all_months_absent_objects_till_today_of_All, createAttandenceOfAllEmployeeOfDate, get_employee_attendance_current_month, getAttendenceOfEmployeesByDepartmentIdForMonth, whathourGreaterTosee, whathourlesserTosee
from attandenceDashBoard.faceValidation2 import ImageAuthenticationBackend
# from attandenceDashBoard.faceValidationWithEmpId import FaceAuthentication
from attandenceDashBoard.models import Attandence, Department, StoreFaces ,EmployeeRegistration
from django.core.files.base import ContentFile
import base64
from attandenceDashBoard.forms import CustomUserForm, EmployeeRegistrationForm 
from attandenceDashBoard.service import halfdays,aboveEightHours,lessthanEightHours,lessThanSevenHours,morethanSevenHours
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from geopy.distance import geodesic
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from io import BytesIO
import json
import calendar
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist


def is_admin(user):
    return user.is_superuser

def save_base64_image(data):
            if data:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                return ContentFile(base64.b64decode(imgstr), name=f"captured.{ext}")
            return None

@login_required()
@user_passes_test(is_admin)
def register(request):
    if request.method == "POST":
        try:
            form = EmployeeRegistrationForm(request.POST,request.FILES)
            if form.is_valid():
                employee = form.save(commit=False)
                employee.save()
                return redirect('success_page')
            else:
                # Form is invalid, check errors
                print(form.errors)
                return render(request, 'EmployeeSection/employeeRegistration.html', {
                    'departments': departments,
                    'form': form
                })
        except Exception as e:
            print("Error during registration:", e)
            departments = Department.objects.all()
            return render(request, 'EmployeeSection/employeeRegistration.html', {
                'departments': departments,
                'form': EmployeeRegistrationForm()
            })
    else:
        form = EmployeeRegistrationForm()
        departments = Department.objects.all()
        
        return render(request, 'EmployeeSection/employeeRegistration.html', {
            'departments': departments,
            'form': form
        })
    


@login_required()
@user_passes_test(is_admin)
def register_faces(request):
    department_id = request.GET.get('department') or request.POST.get('department')

    if request.method == 'POST':
        empId = request.POST.get('empId')
        emp = EmployeeRegistration.objects.get(empId=empId)

        # Uploaded files
        front = request.FILES.get('photo1')
        right = request.FILES.get('photo2')
        left = request.FILES.get('photo3')

        # Base64 images
        face1_base64 = request.POST.get('face1')
        face2_base64 = request.POST.get('face2')
        face3_base64 = request.POST.get('face3')

        if face1_base64:
            front = save_base64_image(face1_base64)
        if face2_base64:
            right = save_base64_image(face2_base64)
        if face3_base64:
            left = save_base64_image(face3_base64)

        StoreFaces.objects.create(emp=emp, front=front, right=right, left=left)
        return redirect('success_page')

    # For GET or non-submitting POST
    if department_id and department_id != "0":
        employees = EmployeeRegistration.objects.filter(deprt=department_id)
    else:
        employees = EmployeeRegistration.objects.all()
    
    departments = Department.objects.all()
    return render(request, 'register_faces.html', {
        'departments': departments,
        'employees': employees
    })




def success(request):
    return render(request, 'sucess.html')





def markAttandence(request): 
 
    if request.method == 'POST':
        clickedImg = request.POST.get('clickedImg')
        # print(clickedImg)
        actionType = request.POST.get('actionType')  # Get Sign In or Sign Out action
        empId = request.POST.get('empId')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        address = request.POST.get('address')
        print(latitude , longitude , "lat lon")
        print(address)
        encoded_image_data = clickedImg.split(',')[1] 
        decoded_image_data = base64.b64decode(encoded_image_data)
        image = Image.open(BytesIO(decoded_image_data))
        image1 = image.convert('RGB')
        image1.save("static/pp4.png") 

        siginImage = save_base64_image(clickedImg) 

        # name = FaceAuthentication.classify_face3('static/pp4.jpg',empId)
        # name = ImageAuthenticationBackend.authenticate("static\pp4.png",empId)
        name = EmployeeRegistration.objects.filter(empId=empId).first().name
        print(name)
        
        names = []
        if name:
            emp = EmployeeRegistration.objects.get(name = name)
            
            attendances = get_employee_attendance_current_month(empId)
            
            latecount= countOfLateDays(attendances)
            print(latecount,"late days")
            eighthourcount = calculateHours(attendances)

            emp = EmployeeRegistration.objects.get(empId= empId)
            depart = emp.deprt
       


            if actionType == 'signin':
                # Record Sign In time (only if not already marked today)
                # obj = Attandence.objects.create(emp=emp,singInTime = datetime.now().time(),mark=True)

                current_time = datetime.now().time()
                today = datetime.today().date()
                
                obj = Attandence.objects.filter(emp=emp, date=today).filter( singInTime__isnull=True).first()
                # if obj and latecount <2 or current_time < target_time :
                if obj :
                        
                    obj.singInTime = current_time
                    obj.mark = True
                    obj.siginImage = siginImage
                    obj.location = address
                    obj.save()
                    names.append(f"{name} - Signed In")

                elif Attandence.objects.filter(emp=emp, date=today).filter( singInTime__isnull=False).exists()   :
                     names.append(f"{name} - Allredy signed In")
                # elif latecount <2 or current_time < target_time:
                else :
                    
                    Attandence.objects.create(
                        emp=emp,
                        date = today,
                        singInTime=current_time,
                        location = address,
                        mark=True,
                        siginImage=siginImage 
                        )
           
                    names.append(f"{name} - Signed In")
                # else : 
                #     names.append(f"{name} -You are late ")
          
            elif actionType == 'signout':
                # Update the same day's record to mark Sign Out
                
                current_time = datetime.now().time()
                obj = Attandence.objects.filter(emp=emp, date=datetime.today().date()).first()

                current_datetime = datetime.combine(date.today(), current_time)
                sing_in_datetime = datetime.combine(date.today(), obj.singInTime)
                todayshours = current_datetime - sing_in_datetime
                eight_hours = timedelta(hours=8)
                remianing = eight_hours -  todayshours

                if obj :
                    # if (eighthourcount <2 and not obj.singoutTime) or todayshours >= eight_hours :
                    if not obj.singoutTime :
                        obj.singoutTime = datetime.now().time()  # Update time field
                        obj.save()
                        names.append(f"{name} - Signed Out")
                    # elif (eighthourcount <2 ) or todayshours >= eight_hours : 
                    else :
                        obj.singoutTime = datetime.now().time()  # Update time field
                        obj.save()
                        names.append(f"{name} - Signed Out")
                    # else : 
                    #     names.append(f"{name} 8 hours is not completed remaining {remianing}")
                else:
                    names.append(f"{name} - No Sign In record found")

        else:
            names = None

        return JsonResponse({'namesList': names})

    return render(request, 'attendence2.html')



def attendance_list(request):
    if request.method == "POST":
        print("comming")
        selected_date = request.POST.get('date')
        departId = request.POST.get('departId') 
        
        deparments =  Department.objects.all()

        if selected_date:
            try:
                selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            except ValueError:
                selected_date = datetime.today().date()  
        else:
            selected_date = datetime.today().date() 
        if str(departId) != "0":
            attendances = Attandence.objects.filter(date=selected_date,emp__deprt=departId).order_by('-singInTime')
        else :
            attendances = Attandence.objects.filter(date=selected_date).order_by('-singInTime')
        return render(request, 'attandenceList.html', {
            'attendances': attendances,
            'selected_date': selected_date,
            'deparments' : deparments,
            'no_records': not attendances.exists()
        })

    else :
        deparments =  Department.objects.all()
        selected_date = datetime.today().date() 
        attendances = Attandence.objects.filter(date=selected_date).order_by('-singInTime')
        return render(request, 'attandenceList.html', {
            'attendances': attendances,
            'selected_date': selected_date,
            'deparments' : deparments,
            'no_records': not attendances.exists()
        })




@login_required()
@user_passes_test(is_admin)
def export_attendance_to_excel(request):
    try:
        selected_date = request.GET.get('date')
        departId = request.GET.get('departId') 

        
        # Check if date is provided
        if not selected_date:
            return JsonResponse({'error': 'Please select a date before exporting.'}, status=400)

        print(f"Exporting attendance for: {selected_date}")

        # Create attendance if not already marked
        createAttandenceOfAllEmployeeOfDate(selected_date)

        # Fetch attendance records for the selected date
        if str(departId) != "0":
            records = Attandence.objects.filter(date=selected_date,emp__deprt=departId)
        else :
            records = Attandence.objects.filter(date=selected_date)

        if not records.exists():
            return JsonResponse({'error': 'No attendance records found for the selected date.'}, status=404)

        # Convert QuerySet to a list of lists (for PDF table)
        data = [['Employee', 'Date', 'Sign-in Time', 'Sign-out Time', 'Marked']]  # Table Headers
        for record in records:
            data.append([
                record.emp.name,  # Assuming 'name' is a field in EmployeeRegistration
                str(record.date),
                str(record.singInTime) if record.singInTime else '-',
                str(record.singoutTime) if record.singoutTime else '-',
                'Present' if record.mark else 'Absent'
            ])

        # Create a PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="attendance_{selected_date}.pdf"'

        # Generate PDF in memory
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        table = Table(data)

        # Add styles to table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Row background
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Table border
        ])
        table.setStyle(style)

        # Build PDF
        pdf.build([table])
        buffer.seek(0)
        response.write(buffer.read())

        return response

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Attendance data could not be retrieved.'}, status=500)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred while generating the report.'}, status=500)




# @csrf_exempt  
# def mark_attendance_api(request):
#     if request.method == 'POST':
#         try:
#             # Get the uploaded image file
#             clicked_img = request.FILES.get('clickedImg')
#             if not clicked_img:
#                 return JsonResponse({'error': 'No image file uploaded'}, status=400)

#             action_type = request.POST.get('actionType')  # 'signin' or 'signout'
#             emp_id = request.POST.get('empId')
#             user_lat = request.POST.get('latitude')
#             user_lon = request.POST.get('longitude')


#             # this is the logic for the office location validations 
#             emp = EmployeeRegistration.objects.get(empId= emp_id)
#             max_distance = 200
#             depart = emp.deprt
#             office_lat = depart.lat
#             office_lon = depart.lon
#             user_location = (user_lat, user_lon)
#             office_location = (office_lat,office_lon)
#             distance = geodesic(office_location, user_location).meters
#             # if distance <= max_distance :
#             #     print("inrange")

#             # ---------------------------


#             if not action_type or not emp_id:
#                 return JsonResponse({'error': 'Missing required fields'}, status=400)

#                 # Open the image using PIL
#             image = Image.open(clicked_img)
#             image_rgb = image.convert('RGB')
#             image_rgb.save("static/temp.jpg")
#             siginImage = clicked_img 

#                 # Perform face authentication
#             result = FaceAuthentication.classify_face3("static/temp.jpg", emp_id)
            
#             if not result:
#                 return JsonResponse({'name': None, 'Present': False , 'range': f'{distance}'})

#             emp = EmployeeRegistration.objects.get(empId=result['empId'])
#             today = datetime.today().date()
#             current_time = datetime.now().time()
                
#             attendances = get_employee_attendance_current_month(emp_id)
                
#             latecount= countOfLateDays(attendances)
#             print(latecount,"late days")
#             eighthourcount = calculateHours(attendances)
#             target_time = time(10, 30, 0)  
#             print(target_time)
#             if action_type == 'signin':
#                 obj = Attandence.objects.filter(emp=emp, date=today).filter( singInTime__isnull=True).first()
#                     # if obj and latecount <2 or current_time < target_time :
#                 if obj :
#                         obj.singInTime = current_time
#                         obj.mark = True
#                         obj.siginImage = siginImage
#                         obj.save()
#                         return JsonResponse({'name': result, 'Present': True, 'message': f'signed in and in range {distance}'})
#                 elif Attandence.objects.filter(emp=emp, date=today, singInTime__isnull=False).exists():
#                         return JsonResponse({'name': result['name'], 'Present': True, 'message': f'Already signed in and in range {distance}'})
#                     # elif latecount <2 or current_time < target_time:
#                 else :
#                         Attandence.objects.create(
#                             emp=emp,
#                             date = today,
#                             singInTime=current_time,
#                             mark=True,
#                             siginImage=siginImage 
#                             )
#                 return JsonResponse({'name': result['name'], 'Present': True })

#             elif action_type == 'signout':
#                     print(eighthourcount,"early login count")
#                     current_time = datetime.now().time()
#                     obj = Attandence.objects.filter(emp=emp, date=datetime.today().date()).first()

#                     current_datetime = datetime.combine(date.today(), current_time)
#                     sing_in_datetime = datetime.combine(date.today(), obj.singInTime)
#                     todayshours = current_datetime - sing_in_datetime
#                     eight_hours = timedelta(hours=8)
#                     remianing = eight_hours -  todayshours

#                     if obj :
#                         # if (eighthourcount <2 and not obj.singoutTime) or todayshours >= eight_hours :
#                         if not obj.singoutTime :
#                             obj.singoutTime = current_time
#                             obj.save()
#                             return JsonResponse({'name': result['name'], 'Present': True, 'message': 'Signed out in range'})
#                         # elif (eighthourcount <2 ) or todayshours >= eight_hours : 
#                         else :
#                             obj.singoutTime = datetime.now().time()  # Update time field
#                             obj.save()
#                             return JsonResponse({'name': result['name'], 'Present': True, 'message': 'Updated signed out'})
#                         # else : 
#                             # return JsonResponse({'name': result['name'],'Present': True, 'message': f'8 hours is not completed remaining {remianing}'})
#             else:
#                     return JsonResponse({'name': result['name'], 'Present': True, 'message': 'No sign-in record found'})
#             # else :
#             #         return JsonResponse({'name': 'You Are', 'Present': False, 'message': f'Not in range {distance}'})
        
#         except EmployeeRegistration.DoesNotExist as e:
#             print(e)
#             return JsonResponse({'error': 'Employee not found'}, status=404)
#         except Exception as e:
#             print(e)
#             return JsonResponse({'error': str(e)}, status=500)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt  # Allows requests without CSRF token (use carefully)
def gethistorydata(request):
    if request.method == "POST":
       
        emp_id = request.POST.get('empId')
        create_all_months_absent_objects_till_today(emp_id)
        # Validate employee ID
        if not emp_id:
            return JsonResponse({"error": "Employee ID is required"}, status=400)

     
        
        # Get attendance records for the current month
        attendances = get_employee_attendance_current_month(emp_id)
        
        # If no records found
        if not attendances.exists():
            return JsonResponse({"message": "No attendance records found"}, status=404)
        
        # Serialize data to return in JSON format
        attendance_data = [
            {
                "name" : record.emp.name,
                "date": record.date.strftime('%Y-%m-%d'),
                "day" : getdays(record.date), 
                "signInTime": record.singInTime.strftime("%I:%M") if record.singInTime else None,
                "signOutTime": record.singoutTime.strftime("%I:%M") if record.singoutTime else None,
                "mark": "Present" if record.mark else "Absent",
                "signinImage": request.build_absolute_uri(record.siginImage.url) if record.siginImage else None
            }
            for record in attendances
        ]

        return JsonResponse({"attendance": attendance_data}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def getdays(date):
    return date.strftime('%A')


@login_required()
@user_passes_test(is_admin)
def export_month_attendance_to_excel(request):
    try:
        data = json.loads(request.body.decode("utf-8"))  # Decode JSON body
        print("Received Data:", data)  # Debugging line

        month_str = data.get('month')  
        departId = data.get('departId')  
        print(departId,"id")
         # Debugging line

        if not month_str:
            return JsonResponse({'error': 'Month parameter is missing.'}, status=400)

        create_all_months_absent_objects_till_today_of_All()

        # Parse the month input
        today = datetime.strptime(month_str, "%Y-%m")
        year, month = today.year, today.month
        last_day = calendar.monthrange(year, month)[1]

        print(month_str," months")

        # Get all attendance records for the selected month
        
        if str(departId) != "0":
            records = getAttendenceOfEmployeesByDepartmentIdForMonth(departId,month_str)
        else :
            records = Attandence.objects.filter(date__year=year, date__month=month)
            print(records,"values")
        if not records.exists():
            print("no records")
            return JsonResponse({'error': 'No attendance records found for the selected date.'}, status=404)

        # Split days into two parts: 1-15 and 16-End
        first_half_days = list(range(1, min(16, last_day + 1)))  # 1 to 15
        second_half_days = list(range(16, last_day + 1))  # 16 to last day (if available)

        # Function to generate table data
        def generate_table_data(day_range):
            table_data = []
            header_row = ['Employee Name']
            for day in day_range:
                date_obj = datetime(year, month, day)
                day_name = date_obj.strftime("%a")  # Get short weekday name (Mon, Tue, etc.)
                header_row.append(f"{day} ({day_name})") 
            table_data.append(header_row)
            if str(departId) != "0":
                employees = EmployeeRegistration.objects.filter(deprt = departId)
            else :
                employees = EmployeeRegistration.objects.all()
            
            for employee in employees :
                row = [employee.name]  # Employee name only once
                for day in day_range:
                    attendance = records.filter(emp=employee, date__day=day).first()

                    if attendance and attendance.singInTime and attendance.singoutTime:
                        sign_in_time = attendance.singInTime
                        sign_out_time = attendance.singoutTime

                        # Convert time to datetime for subtraction (using a fixed date)
                        base_date = datetime.today().date()
                        sign_in_datetime = datetime.combine(base_date, sign_in_time)
                        sign_out_datetime = datetime.combine(base_date, sign_out_time)

                        # Format time in 12-hour format
                        sign_in = sign_in_datetime.strftime("%I:%M")
                        sign_out = sign_out_datetime.strftime("%I:%M")

                        # Calculate time difference
                        time_diff = sign_out_datetime - sign_in_datetime
                        if time_diff > timedelta(hours=0):  # Ensure sign-out is after sign-in
                            total_hours = time_diff.seconds // 3600  # Extract hours
                            total_minutes = (time_diff.seconds % 3600) // 60  # Extract minutes
                            work_duration = f"{total_hours}h {total_minutes}m"
                        else:
                            work_duration = "0h 0m"

                        row.append(f"{sign_in}\n{sign_out}\n{work_duration}")

                    elif attendance:  # If attendance exists but missing time data
                        sign_in = attendance.singInTime.strftime("%I:%M") if attendance.singInTime else ""
                        sign_out = attendance.singoutTime.strftime("%I:%M") if attendance.singoutTime else ""
                        row.append(f"{sign_in}\n{sign_out}\n0h 0m")
                    else:
                        row.append("")

                
                table_data.append(row)
            
            return table_data

        # Generate two tables
        first_half_table = generate_table_data(first_half_days)
        second_half_table = generate_table_data(second_half_days) if second_half_days else None  # If no second half, don't create

        # Define column widths
        num_first_half_days = len(first_half_days)
        num_second_half_days = len(second_half_days)

        first_half_col_widths = [150] + [((750 - 150) // num_first_half_days) for _ in range(num_first_half_days)]
        second_half_col_widths = [150] + [((750 - 150) // num_second_half_days) for _ in range(num_second_half_days)] if second_half_days else None

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="attendance_{month}.pdf"'

        buffer = BytesIO()
        pdf = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(letter),  # ✅ FORCE LANDSCAPE MODE
            leftMargin=30, rightMargin=30, topMargin=40, bottomMargin=40
        )

        elements = []

        # First Table (Days 1-15)
        table1 = Table(first_half_table, colWidths=first_half_col_widths)
        table1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        elements.append(table1)

        # Second Table (Days 16-End)
        if second_half_table:
            elements.append(Spacer(1, 20))  # ✅ Space Between Two Tables
            table2 = Table(second_half_table, colWidths=second_half_col_widths)
            table2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))

            elements.append(table2)

        # Build PDF
        pdf.build(elements)
        buffer.seek(0)
        response.write(buffer.read())

        return response

    except ObjectDoesNotExist:
        
        print("ObjectDoesNotExist")
        return JsonResponse({'error': 'Attendance data could not be retrieved.'}, status=500)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred while generating the report.'}, status=500)





def lateDataView(request):
    listOfEmp = []
    
    if request.method == "POST":
        hours = request.POST.get("hours")
        
        if hours == "8":
            listOfEmp = aboveEightHours()
        elif hours == "7":
            listOfEmp = lessthanEightHours()
        elif hours == "6":
            listOfEmp = morethanSevenHours()
        elif hours == "5":
            listOfEmp = lessThanSevenHours()
        elif hours == "4":
            listOfEmp = halfdays()
        
        # Convert the queryset or list to a JSON serializable format
        emp_data = [
            {
                "employee_id": atten.emp.name, 
                "duration": str(caluculateHOurs(atten.singInTime, atten.singoutTime)), 
                "date" : atten.date,
                "status": atten.mark
            } 
            for sublist in listOfEmp  # Iterate through outer list
            for atten in sublist      # Iterate through each inner list
                        ]


        return JsonResponse({"list": emp_data})

    return render(request, "hoursList.html", {"list": listOfEmp})



def caluculateHOurs(signInTime,signInOut):
        base_date = datetime.today().date()
        sign_in_datetime = datetime.combine(base_date, signInTime)
        sign_out_datetime = datetime.combine(base_date, signInOut)

        
        time_diff = sign_out_datetime - sign_in_datetime
        if time_diff > timedelta(hours=0):  # Ensure sign-out is after sign-in
            total_hours = time_diff.seconds // 3600  # Extract hours
            total_minutes = (time_diff.seconds % 3600) // 60  # Extract minutes
            work_duration = f"{total_hours}h {total_minutes}m"
        return work_duration




@csrf_exempt
def getData(request):
    if request.method == "POST":
        hours = request.POST.get("hours")
        if hours == "1" :
             months = whathourGreaterTosee(8) 
        if hours == "2" :
            months = whathourlesserTosee(8)
        if hours == "3" :
             months = whathourGreaterTosee(7) 
        if hours == "4" :
             months = whathourlesserTosee(7)
        if hours == "5" :
             months = whathourlesserTosee(5)
         # Keep your logic unchanged
        
        # Render only the table and send it as a response
        table_html = render(request, "table_partial.html", {"months": months}).content.decode("utf-8")

        return JsonResponse({"table_html": table_html})

    return render(request, "hourData.html")



@login_required()
@user_passes_test(is_admin)
@csrf_exempt
def createSuperUser(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            return redirect("success_page")
        else:
            print(form.errors)  # Only print if form is invalid
    else:
        form = CustomUserForm()
    
    return render(request, "userRegisteration.html", {"form": form})



@csrf_exempt
def login_view(request):
    
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request,username=username,password=password)
    if user is not None :
        
        login(request, user)
     
        return redirect('success_page')
    #     messages.success(request, f'Welcome, {username}!')
    #     return redirect('success_page')
    else :
        messages.error(request , 'Invalid username or password. Please try again.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('success_page')

