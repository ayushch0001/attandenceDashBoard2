import calendar
from datetime import date, datetime, time, timedelta

from attandenceDashBoard.service import create_all_months_absent_objects_till_today_of_All


from .models import LeaveManagement, SalaryOfEveryPerson , EmployeeRegistration , Attandence ,employeeRecordEveryMonth ,Department







class AttandenceService:


    def get_employee_attendance_current_month(self,employee_id,month_str): 
 
        today = today = datetime.strptime(month_str, "%Y-%m")
        current_year = today.year
        current_month = today.month
        employee = EmployeeRegistration.objects.filter(empId=employee_id).first()
        attendance_records = Attandence.objects.filter(
            emp = employee,  # Correct ForeignKey reference
            date__year=current_year,
            date__month=current_month
        ).order_by('-date')  # Orders records by date
        return attendance_records



    def record(self,month_str,employee):
        department = employee.deprt
        today  = datetime.strptime(month_str, "%Y-%m")
       
        year, monthNum = today.year, today.month
       
        
        current_year = today.year
        current_month = today.month
        earlyOut_list = []
        lateDays_list = []

        attended_days = Attandence.objects.filter(
            emp=employee,
            date__year=current_year,
            date__month=current_month
        )
        absents = 0
        _, num_days_in_month = calendar.monthrange(year, monthNum)
        objectNotcreated = num_days_in_month - len(attended_days)


        for dayattendence in  attended_days :

        
            # if not late than for early out 
            if dayattendence.singInTime and dayattendence.singoutTime :

                if dayattendence.singInTime > department.intime :
                        lateDays_list.append(dayattendence)

                
                working_hours = ""
                duration = ""
                signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                working_hours = signInOut - signInTime 
                duration = timedelta(hours=department.workingHour) - timedelta(minutes=department.earlyRelifeHour)

                

                if working_hours <= duration :
                    earlyOut_list.append(dayattendence)

            elif dayattendence.singInTime :

                if dayattendence.singInTime > department.intime :
                        lateDays_list.append(dayattendence)

            if not dayattendence.singInTime and not dayattendence.singoutTime :
                absents = absents + 1
                 

        record, created = employeeRecordEveryMonth.objects.get_or_create(
        employee=employee,
        monthDate=today
            ) 
       
        month_cal = calendar.monthcalendar(year, monthNum)
        num_sundays = sum(1 for week in month_cal if week[calendar.SUNDAY] != 0)


        if created:

            record.absents = absents + objectNotcreated - num_sundays
            record.earlyOuts = len(earlyOut_list)
            record.lateDays = len(lateDays_list)

            if len(earlyOut_list) > department.earlyRelifeDays :
                    record.halfDays = len(earlyOut_list) - department.earlyRelifeDays
                    
            if len(lateDays_list) > department.lateDaysCount :
                 
                if len(lateDays_list) > department.lateDaysCount and len(lateDays_list) == department.lateDaysCount + 1: # for adding 2 days as half day 
                    record.halfDaysDuetolate =  1

                elif len(lateDays_list) > department.lateDaysCount and len(lateDays_list) >= department.lateDaysCount + 2: # for adding 2 days as half day 
                    record.halfDaysDuetolate =  2

                if len(lateDays_list) <= department.lateDaysCount + 2 :
                     
                     record.absentDueTolate = len(lateDays_list) - department.lateDaysCount
                elif len(lateDays_list)   >= department.lateDaysCount + 2 :
                        record.absentDueTolate  = len(lateDays_list) - (department.lateDaysCount + 2)
            record.save()         
        else:

            record.absents = absents + objectNotcreated - num_sundays
            record.save()
            
            record.earlyOuts = len(earlyOut_list)
            record.lateDays = len(lateDays_list)
         

            if len(earlyOut_list) > department.earlyRelifeDays :
                    record.halfDays = len(earlyOut_list) - department.earlyRelifeDays

            if len(lateDays_list) > department.lateDaysCount :

                if len(lateDays_list) > department.lateDaysCount and len(lateDays_list) == department.lateDaysCount + 1: # for adding 2 days as half day 
                    record.halfDaysDuetolate =  1

                elif len(lateDays_list) > department.lateDaysCount and len(lateDays_list) >= department.lateDaysCount + 2: # for adding 2 days as half day 
                    record.halfDaysDuetolate =  2

                if len(lateDays_list) <= (department.lateDaysCount + 2) :
                     record.absentDueTolate = len(lateDays_list) - department.lateDaysCount
                elif len(lateDays_list)   >= ( department.lateDaysCount + 2 ):
                        record.absentDueTolate  = len(lateDays_list) - (department.lateDaysCount + 2)

            record.save()
        return record
    
    

    def leaveTaken(self,month_str,empId,number):

        today = datetime.strptime(month_str, "%Y-%m")

        record, created = employeeRecordEveryMonth.objects.get_or_create(
        employee__empId = empId,
        monthDate=today
            ) 

        if created :
             record.allowedLeaveTakens = number
        else :
             record.allowedLeaveTakens = number
        record.save()


class SalaryServices:
    
    def makeSalary(self,employee,month_str):

        create_all_months_absent_objects_till_today_of_All()
        attService = AttandenceService() 
        
        try:
            today = datetime.strptime(month_str, "%Y-%m")
            year, month = today.year, today.month
 
            # --- 1. Get Salary and Attendance Records Safely ---
            emp_salary = SalaryOfEveryPerson.objects.get(emp=employee)
            monthly_salary = emp_salary.salaryPerMonth
            
            record = employeeRecordEveryMonth.objects.filter(employee=employee,monthDate = today).first()
            record.refresh_from_db()
        except (SalaryOfEveryPerson.DoesNotExist, employeeRecordEveryMonth.DoesNotExist):
            print(f"Missing salary or attendance record for {employee} for {month_str}.")
            return {}  # Or handle as per your business logic

        # --- 2. Determine Working Days and Unpaid Days ---
        _, num_days_in_month = calendar.monthrange(year, month)

        # Assuming Sundays are non-working days. You can also subtract Saturdays or public holidays.

        # check here sundays are working or not -----------------------------------------------------
        totaly_attandence = attService.get_employee_attendance_current_month(employee.empId,month_str)

        
        total_working_days = num_days_in_month  
       
        if total_working_days == 0:
            return {}

        
        unpaid_absences = ( record.absentDueTolate  + record.absents ) - record.allowedLeaveTakens
        
        unpaid_half_days = record.halfDaysDuetolate + record.halfDays
        
        total_unpaid_days = unpaid_absences + (unpaid_half_days / 2.0) 
        record.totalunpaidDays = total_unpaid_days
        
        rate_per_day = monthly_salary / total_working_days
        total_deductions = total_unpaid_days * rate_per_day
        final_salary = monthly_salary - total_deductions
        record.totalsalary = final_salary
        record.save()
        record.refresh_from_db()
        day_range = list(range(1,  num_days_in_month + 1))
        days_of_month = []
        
        for day in day_range:

            perDayDict = {}

            date_obj = datetime(year, month, day)
            day_name = date_obj.strftime("%a")
            
            perDayDict['date'] = day
            perDayDict['day_name'] = day_name  # day name

            attendance = totaly_attandence.filter(date__day=day).first()
            
            if attendance and attendance.singInTime and attendance.singoutTime:
                perDayDict['status'] = "Pre"
                sign_in_time = attendance.singInTime
                sign_out_time = attendance.singoutTime
                
                # Convert time to datetime for subtraction (using a fixed date)
                base_date = datetime.today().date()
                sign_in_datetime = datetime.combine(base_date, sign_in_time)
                sign_out_datetime = datetime.combine(base_date, sign_out_time)

                # Format time in 12-hour format
                sign_in = sign_in_datetime.strftime("%I:%M")
                sign_out = sign_out_datetime.strftime("%I:%M")
               
                perDayDict["sign_in"] = sign_in
                perDayDict["sign_out"] = sign_out
                

                # Calculate time difference
                time_diff = sign_out_datetime - sign_in_datetime
                
                if time_diff > timedelta(hours=0):  # Ensure sign-out is after sign-in
                    total_hours = time_diff.seconds // 3600  # Extract hours
                    total_minutes = (time_diff.seconds % 3600) // 60  # Extract minutes
                    work_duration = f"{total_hours}h {total_minutes}m"

                    perDayDict["duration"] = f"{work_duration}"

                else:
                    work_duration = "0h 0m"

            elif attendance:  # If attendance exists but missing time data
                
                sign_in = attendance.singInTime.strftime("%I:%M") if attendance.singInTime else ""
                if sign_in :
                     perDayDict['status'] = "Pre"
                     perDayDict["sign_in"] = sign_in
                sign_out = attendance.singoutTime.strftime("%I:%M") if attendance.singoutTime else ""

                perDayDict["duration"] = f"0h 0m"
            else:
                perDayDict["duration"] = ""
            
            days_of_month.append(perDayDict)
        
        return days_of_month 
    

class AdminSalaryServices:
     
    def createAllEmployeesSalary(self):
        allEmployees = EmployeeRegistration.objects.all()
        for employee in allEmployees :
            SalaryOfEveryPerson.objects.get_or_create(emp = employee)


    def createEveryMonthRecordofAll(self,month_str):
               
        today  = datetime.strptime(month_str, "%Y-%m")
        allEmployees = EmployeeRegistration.objects.all()
        for employee in allEmployees :
            record, created = employeeRecordEveryMonth.objects.get_or_create(
            employee=employee,
            monthDate=today
                )
            AttandenceService().record(month_str,employee)
            SalaryServices().makeSalary(employee,month_str)