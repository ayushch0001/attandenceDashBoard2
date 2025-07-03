import calendar
from datetime import date, datetime ,time ,timedelta
import json
from PIL import Image 
from django.http import JsonResponse
from django.shortcuts import render, redirect
import os
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from attandenceDashBoard.service import calculateHours, countOfLateDays, create_all_months_absent_objects_till_today, create_all_months_absent_objects_till_today_of_All, createAttandenceOfAllEmployeeOfDate, get_employee_attendance_current_month, whathourGreaterTosee, whathourlesserTosee
from attandenceDashBoard.validatingFace import serv
from attandenceDashBoard.faceValidation2 import ImageAuthenticationBackend
from attandenceDashBoard.faceValidationWithEmpId import FaceAuthentication
from .models import Attandence, StoreFaces ,EmployeeRegistration
from django.core.files.base import ContentFile
import base64
from io import BytesIO
from attandenceDashBoard.forms import CustomUserForm, EmployeeRegistrationForm ,StoreFaces
# from .newFacevalidationlibrary import DeepFaceLibrary
from attandenceDashBoard.service import halfdays,aboveEightHours,lessthanEightHours,lessThanSevenHours,morethanSevenHours
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from geopy.distance import geodesic


@csrf_exempt  
def mark_attendance_api(request):
    if request.method == 'POST':
        try:
            # Get the uploaded image file
            clicked_img = request.FILES.get('clickedImg')
            if not clicked_img:
                return JsonResponse({'error': 'No image file uploaded'}, status=400)

            action_type = request.POST.get('actionType')  # 'signin' or 'signout'
            emp_id = request.POST.get('empId')
            user_lat = request.POST.get('latitude')
            user_lon = request.POST.get('longitude')


#  this is the logic for the office location validations 
            emp = EmployeeRegistration.objects.get(empId= emp_id)
            max_distance = 200
            depart = emp.deprt
            office_lat = depart.lat
            office_lon = depart.lon
            user_location = (user_lat, user_lon)
            office_location = (office_lat,office_lon)
            distance = geodesic(office_location, user_location).meters
            if distance <= max_distance :
                print("inrange")

# ---------------------------


                if not action_type or not emp_id:
                    return JsonResponse({'error': 'Missing required fields'}, status=400)

                    # Open the image using PIL
                image = Image.open(clicked_img)
                image_rgb = image.convert('RGB')
                image_rgb.save("static/temp.jpg")
                siginImage = clicked_img 

                    # Perform face authentication
                result = FaceAuthentication.classify_face3("static/temp.jpg", emp_id)
                
                if not result:
                    return JsonResponse({'name': None, 'Present': False , 'range': f'{distance}'})

                emp = EmployeeRegistration.objects.get(empId=result['empId'])
                today = datetime.today().date()
                current_time = datetime.now().time()
                    
                attendances = get_employee_attendance_current_month(emp_id)
                    
                latecount= countOfLateDays(attendances)
                print(latecount,"late days")
                eighthourcount = calculateHours(attendances)
                target_time = time(10, 30, 0)  
                print(target_time)
                if action_type == 'signin':
                    obj = Attandence.objects.filter(emp=emp, date=today).filter( singInTime__isnull=True).first()
                        # if obj and latecount <2 or current_time < target_time :
                    if obj :
                            obj.singInTime = current_time
                            obj.mark = True
                            obj.siginImage = siginImage
                            obj.save()
                    elif Attandence.objects.filter(emp=emp, date=today, singInTime__isnull=False).exists():
                            return JsonResponse({'name': result['name'], 'Present': True, 'message': f'Already signed in and in range {distance}'})
                        # elif latecount <2 or current_time < target_time:
                    else :
                            Attandence.objects.create(
                                emp=emp,
                                date = today,
                                singInTime=current_time,
                                mark=True,
                                siginImage=siginImage 
                                )
                    return JsonResponse({'name': result['name'], 'Present': True })

                elif action_type == 'signout':
                        print(eighthourcount,"early login count")
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
                                obj.singoutTime = current_time
                                obj.save()
                                return JsonResponse({'name': result['name'], 'Present': True, 'message': 'Signed out in range'})
                            # elif (eighthourcount <2 ) or todayshours >= eight_hours : 
                            else :
                                obj.singoutTime = datetime.now().time()  # Update time field
                                obj.save()
                                return JsonResponse({'name': result['name'], 'Present': True, 'message': 'Updated signed out'})
                            # else : 
                                # return JsonResponse({'name': result['name'],'Present': True, 'message': f'8 hours is not completed remaining {remianing}'})
                else:
                        return JsonResponse({'name': result['name'], 'Present': True, 'message': 'No sign-in record found'})
            else :
                    return JsonResponse({'name': 'You Are', 'Present': False, 'message': f'Not in range {distance}'})
        
        except EmployeeRegistration.DoesNotExist as e:
            print(e)
            return JsonResponse({'error': 'Employee not found'}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
