import calendar
from datetime import date, datetime, time, timedelta
from .models import SalaryOfEveryPerson , EmployeeRegistration , Attandence ,employeeRecordEveryMonth ,Department







class AttandenceService:


    def get_employee_attendance_current_month(self,employee_id): 
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


    def countOfLateDays(self,attendance_records,departmentId):
        department = Department.objects.get(pk = departmentId)
        target_time = department.intime
        late_count = 0
        
        for attendance in attendance_records:
            if attendance.singInTime and attendance.singInTime > target_time:  
                late_count += 1
        return late_count


    # monthDate = models.DateField(default=datetime.date(datetime.date.today().year,datetime.date.today().month,1))
    # absentDueTolate = models.FloatField(default=0)
    # lateDays = models.IntegerField(default=0)
    # halfDays = models.IntegerField(default=0)
    # earlyOuts = models.IntegerField(default=0)
    # allowedLeaveTakens = models.IntegerField(default=0)
    # earlyRelifeDays
    


    def halfdays(self,month,employee):
        
        today = month
        monthDate = date(date.today().year,date.today().month,1)
        current_year = today.year
        current_month = today.month
        employee_list = []
        

        attended_days = Attandence.objects.filter(
            emp=employee,
            date__year=current_year,
            date__month=current_month
        )
        for dayattendence in  attended_days :
            working_hours = ""
            six_hours = ""
            if dayattendence.singInTime and dayattendence.singoutTime :
                signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                working_hours = signInOut -signInTime 
                six_hours = timedelta(hours=6)

                if working_hours <= six_hours :
                    employee_list.append(dayattendence)
    
        record, created = employeeRecordEveryMonth.objects.get_or_create(
        employee=employee,
        monthDate=monthDate
            ) 
        if created:
            record.halfDays = len(employee_list)
        else:
            record.halfDays = len(employee_list)
             
        return employee_list 
    

    def earlyOut(self,month,employee,attendance_records,departmentId):
        today = month
        monthDate = date(date.today().year,date.today().month,1)
        department = Department.objects.get(pk = departmentId)
        target_time = department.outTIme
        early_out = 0
        for attendance in attendance_records:
            if attendance.singInTime and attendance.singInTime > target_time and :  
                early_out += 1

        record, created = employeeRecordEveryMonth.objects.get_or_create(
        employee=employee,
        monthDate=monthDate
            )
        if created:
            record.earlyOuts = early_out
        else:
            record.earlyOuts = early_out 
        return early_out




                    # signInTime = datetime.combine(date.today(), dayattendence.singInTime)
                    # signInOut = datetime.combine(date.today(), dayattendence.singoutTime)
                    # working_hours = signInOut -signInTime 
                    # seven_hours = timedelta(hours=6)


     