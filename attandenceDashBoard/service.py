from datetime import date, datetime, time
from .models import Attandence, EmployeeRegistration
import calendar
from django.utils.timezone import now
from datetime import datetime, timedelta

def get_employee_attendance_current_month(employee_id):
    """
    Retrieves attendance records for a given employee in the current month and year.
    
    :param employee_id: ID of the employee
    :return: QuerySet of attendance records
    """
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    

    employee = EmployeeRegistration.objects.filter(empId=employee_id).first()
    attendance_records = Attandence.objects.filter(
        emp = employee,  # Correct ForeignKey reference
        date__year=current_year,
        date__month=current_month
    ).order_by('-date')  # Orders records by date
    return attendance_records


def countOfLateDays(attendance_records):
    target_time = time(10, 30, 0)  # 10:30 AM is the late threshold
    late_count = 0

    for attendance in attendance_records:
        if attendance.singInTime and attendance.singInTime > target_time:  
            late_count += 1
    
    return late_count

def createAttandenceOfAllEmployeeOfDate(date=None):
    try:
        if not date:
            raise ValueError("Date is required to create attendance records.")

        employees = EmployeeRegistration.objects.all()
        selected_date = date

        # Fetch all employees who have attended today
        attended_employees = Attandence.objects.filter(date=selected_date).values_list('emp__empId', flat=True)

        # Employees who are not in the attended list
        nonsigninEmployees = [employee for employee in employees if employee.empId not in attended_employees]

        # print(f"Total Employees: {len(employees)}")
        # print(f"Employees Attended: {len(attended_employees)}")
        # print(f"Non-Signed-In Employees: {len(nonsigninEmployees)}")

        for employee in nonsigninEmployees:
            try:
                obj = Attandence.objects.create(emp=employee, date=selected_date)  # Ensure date is set
                print(f"Created attendance record: {obj}")
            except Exception as e:
                print(f"Error creating attendance for {employee.empId}: {str(e)}")

    except ValueError as ve:
        print(f"ValueError: {ve}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")


from datetime import datetime, timedelta
from calendar import monthrange
from .models import Attandence, EmployeeRegistration

def create_all_months_absent_objects_till_today(emp_id):
    """
    Creates attendance objects for all missing days of the current month up to today
    for a specific employee.

    :param emp_id: ID of the employee
    :return: None
    """
    try:
        today = datetime.today()
        current_year = today.year
        current_month = today.month
        last_day = today.day  # Get the last day as today

        # Get the employee object
        employee = EmployeeRegistration.objects.filter(empId=emp_id).first()
        if not employee:
            print(f"Error: No employee found with empId {emp_id}")
            return

        # Get all existing attendance dates for the employee
        attended_days = Attandence.objects.filter(
            emp=employee,
            date__year=current_year,
            date__month=current_month
        ).values_list('date', flat=True)  # Get a list of dates with existing records

        # Loop through all days of the month up to today
        for day in range(1, last_day + 1):
            current_date = datetime(current_year, current_month, day).date()

            if current_date not in attended_days:  # If no record exists, create it
                try:
                    obj = Attandence.objects.create(
                        emp=employee,
                        date=current_date,
                        mark=False  # Default as Absent
                    )
                    print(f"Created absent attendance record for {employee.empId} on {current_date}")
                except Exception as e:
                    print(f"Error creating attendance for {employee.empId} on {current_date}: {str(e)}")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")



def calculateHours(attendance_records):
    lessEightHoursCount = 0
    for attendance in attendance_records:
        working_hours = ""
        eight_hours = ""
        if attendance.singInTime and attendance.singoutTime :
            signInTime = datetime.combine(date.today(), attendance.singInTime)
            signInOut = datetime.combine(date.today(), attendance.singoutTime)
            working_hours = signInOut -signInTime 
            eight_hours = timedelta(hours=8)

            if working_hours < eight_hours :
                lessEightHoursCount += 1
                

    return lessEightHoursCount



def create_all_months_absent_objects_till_today_of_All():
    try:
        today = datetime.today()
        current_year = today.year
        current_month = today.month
        last_day = calendar.monthrange(current_year, current_month)[1]  # Get last day of the month

        employees = EmployeeRegistration.objects.all()

        for employee in employees:
            attended_days = set(Attandence.objects.filter(
                emp=employee,
                date__year=current_year,
                date__month=current_month
            ).values_list('date', flat=True))  # Fetch existing attendance records

            for day in range(1, last_day + 1):
                current_date = datetime(current_year, current_month, day).date()
                
                if current_date <= today.date() and current_date not in attended_days:
                    try:
                        Attandence.objects.create(
                            emp=employee,
                            date=current_date,
                            mark=False  # Default as Absent
                        )
                        print(f"Created absent record for {employee.empId} on {current_date}")
                    except Exception as e:
                        print(f"Error creating record for {employee.empId} on {current_date}: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    

def aboveEightHours():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    last_day = calendar.monthrange(current_year, current_month)[1]
    employees = EmployeeRegistration.objects.all()
    
    total_list = [[]]
    

    for employee in employees:
            employee_list = []
            # Get the current date
            current_date = now().date()

            # Get the first and last day of the current month
            first_day_of_month = current_date.replace(day=1)
            # last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Query to get attendance records only for the current month
            attended_days = Attandence.objects.filter(
                emp=employee,
                date__range=[first_day_of_month, current_date]  # Filters records within this month
            )
            for dayattendence in  attended_days :
                working_hours = ""
                eight_hours = ""
                if dayattendence.singInTime and dayattendence.singoutTime :
                    signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    working_hours = signInOut -signInTime 
                    eight_hours = timedelta(hours=8)

                    if working_hours > eight_hours :
                        employee_list.append(dayattendence)
        
            total_list.__add__(employee_list)
            
    return total_list
        

def lessthanEightHours():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    last_day = calendar.monthrange(current_year, current_month)[1]
    employees = EmployeeRegistration.objects.all()
    
    total_list = []
    

    for employee in employees:
            employee_list = []
            # Get the current date
            current_date = now().date()

            # Get the first and last day of the current month
            first_day_of_month = current_date.replace(day=1)
            # last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Query to get attendance records only for the current month
            attended_days = Attandence.objects.filter(
                emp=employee,
                date__range=[first_day_of_month, current_date]  # Filters records within this month
            )
            for dayattendence in  attended_days :
                working_hours = ""
                eight_hours = ""
                if dayattendence.singInTime and dayattendence.singoutTime :
                    signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    working_hours = signInOut -signInTime 
                    eight_hours = timedelta(hours=8)

                    if working_hours < eight_hours :
                        employee_list.append(dayattendence)
        
            total_list.append(employee_list)
            
    return total_list


def morethanSevenHours():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    last_day = calendar.monthrange(current_year, current_month)[1]
    employees = EmployeeRegistration.objects.all()
    
    total_list = []
    

    for employee in employees:
            employee_list = []
            # Get the current date
            current_date = now().date()

            # Get the first and last day of the current month
            first_day_of_month = current_date.replace(day=1)
            # last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Query to get attendance records only for the current month
            attended_days = Attandence.objects.filter(
                emp=employee,
                date__range=[first_day_of_month, current_date]  # Filters records within this month
            )
            for dayattendence in  attended_days :
                working_hours = ""
                sevenHours = ""
                if dayattendence.singInTime and dayattendence.singoutTime :
                    signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    working_hours = signInOut -signInTime 
                    sevenHours = timedelta(hours=7)

                    if working_hours > sevenHours :
                        employee_list.append(dayattendence)
        
            total_list.append(employee_list)
            
    return total_list

def lessThanSevenHours():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    last_day = calendar.monthrange(current_year, current_month)[1]
    employees = EmployeeRegistration.objects.all()
    
    total_list = []
    

    for employee in employees:
            employee_list = []
            # Get the current date
            current_date = now().date()

            # Get the first and last day of the current month
            first_day_of_month = current_date.replace(day=1)
            # last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Query to get attendance records only for the current month
            attended_days = Attandence.objects.filter(
                emp=employee,
                date__range=[first_day_of_month, current_date]  # Filters records within this month
            )
            for dayattendence in  attended_days :
                working_hours = ""
                sevenHours = ""
                if dayattendence.singInTime and dayattendence.singoutTime :
                    signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    working_hours = signInOut -signInTime 
                    sevenHours = timedelta(hours=7)

                    if working_hours < sevenHours :
                        employee_list.append(dayattendence)
        
            total_list.append(employee_list)
            
    return total_list

def halfdays():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    last_day = calendar.monthrange(current_year, current_month)[1]
    employees = EmployeeRegistration.objects.all()
    
    total_list = []
    

    for employee in employees:
            employee_list = []
            attended_days = Attandence.objects.filter(
                emp=employee,
                date__year=current_year,
                date__month=current_month
            )
            for dayattendence in  attended_days :
                working_hours = ""
                seven_hours = ""
                if dayattendence.singInTime and dayattendence.singoutTime :
                    signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    working_hours = signInOut -signInTime 
                    seven_hours = timedelta(hours=6)

                    if working_hours <= seven_hours :
                        employee_list.append(dayattendence)
        
            total_list.append(employee_list)
        
    return total_list




def whathourGreaterTosee(hour):
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    last_day = calendar.monthrange(current_year, current_month)[1]
    employees = EmployeeRegistration.objects.all()
    
    total_list = []
    days = []
    days.append("Employee Name")
    for day in range(1,last_day+1):
        days.append(day)
    total_list.append(days)
     
    for employee in employees:
            employee_list = []
            employee_list.append(employee.name)
            # Get the current date
            current_date = now().date()

            # Get the first and last day of the current month
            first_day_of_month = current_date.replace(day=1)
            # last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Query to get attendance records only for the current month
            attended_days = Attandence.objects.filter(
                emp=employee,
                date__range=[first_day_of_month, current_date]  # Filters records within this month
            ).order_by('date')
            for dayattendence in  attended_days :
                working_hours = ""
                eight_hours = ""
                if dayattendence.singInTime and dayattendence.singoutTime :
                    signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    working_hours = signInOut -signInTime 
                    eight_hours = timedelta(hours = hour)

                    if working_hours > eight_hours :
                        employee_list.append("Y")
                    else :
                        employee_list.append("")
                else :
                        employee_list.append("")
        
            total_list.append(employee_list)
            
    return total_list



def whathourlesserTosee(hour):
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    last_day = calendar.monthrange(current_year, current_month)[1]
    employees = EmployeeRegistration.objects.all()
    
    total_list = []
    days = []
    days.append("Employee Name")
    for day in range(1,last_day+1):
        days.append(day)
    total_list.append(days)
     
    for employee in employees:
            employee_list = []
            employee_list.append(employee.name)
            # Get the current date
            current_date = now().date()

            # Get the first and last day of the current month
            first_day_of_month = current_date.replace(day=1)
            # last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Query to get attendance records only for the current month
            attended_days = Attandence.objects.filter(
                emp=employee,
                date__range=[first_day_of_month, current_date]  # Filters records within this month
            ).order_by('date')
            for dayattendence in  attended_days :
                working_hours = ""
                eight_hours = ""
                if dayattendence.singInTime and dayattendence.singoutTime :
                    signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    working_hours = signInOut -signInTime 
                    Whours = timedelta(hours = hour)

                    if working_hours < Whours :
                        employee_list.append("Y")
                    else :
                        employee_list.append("")
                else :
                        employee_list.append("")
        
            total_list.append(employee_list)
            
    return total_list



from geopy.distance import geodesic
from django.conf import settings

def is_within_office_radius(user_lat, user_lon, max_distance=50):
    office_location = (settings.OFFICE_LATITUDE, settings.OFFICE_LONGITUDE)
    user_location = (user_lat, user_lon)
    
    distance = geodesic(office_location, user_location).meters  # Get distance in meters
    return distance <= max_distance


def getAttendenceOfEmployeesByDepartmentIdOfEveryDay(deprtment):
    listof = Attandence.objects.filter(emp__deprt=3, date=datetime.today().date())
    print(listof)
    return listof


def getAttendenceOfEmployeesByDepartmentIdForMonth(departId,month_str):
        today = datetime.strptime(month_str, "%Y-%m")
        year, month = today.year, today.month
        print(departId)
        records =  Attandence.objects.filter(date__year=year, date__month=month,emp__deprt=departId)
        # print(records)
        return records