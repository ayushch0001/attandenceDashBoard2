import calendar
from datetime import date, datetime, time, timedelta
from .models import (
    LeaveManagement, MonthlyHolidays, SalaryOfEveryPerson, 
    EmployeeRegistration, Attandence, employeeRecordEveryMonth, Department
)

class AttandenceService:
    def get_employee_attendance_current_month(self, employee_id, month_str): 
        target_date = datetime.strptime(month_str, "%Y-%m")
        employee = EmployeeRegistration.objects.filter(empId=employee_id).first()
        return Attandence.objects.filter(
            emp=employee,
            date__year=target_date.year,
            date__month=target_date.month
        ).order_by('date')

    def record(self, month_str, employee):
        department = employee.deprt
        month_date = datetime.strptime(month_str, "%Y-%m")
        year, month_num = month_date.year, month_date.month
        
        attended_days = Attandence.objects.filter(
            emp=employee,
            date__year=year,
            date__month=month_num
        )

        early_out_count = 0
        late_days_count = 0
        absents = 0
        
        _, num_days_in_month = calendar.monthrange(year, month_num)
        
        for attendance in attended_days:
            if not attendance.singInTime:
                absents += 1
                continue

            # Late Arrival Logic
            if attendance.singInTime > department.intime:
                late_days_count += 1

            # Early Departure Logic
            if attendance.singInTime and attendance.singoutTime:
                # Fixed: Use absolute difference for Night Shift or cross-day logic
                start = datetime.combine(date.today(), attendance.singInTime)
                end = datetime.combine(date.today(), attendance.singoutTime)
                
                if employee.shift == "NIGHT" and end < start:
                    end += timedelta(days=1)
                
                working_hours = end - start
                required_duration = timedelta(hours=department.workingHour) - timedelta(minutes=department.earlyRelifeHour)

                if working_hours < required_duration:
                    early_out_count += 1

        # Calculate records
        record, _ = employeeRecordEveryMonth.objects.get_or_create(employee=employee, monthDate=month_date)
        
        month_cal = calendar.monthcalendar(year, month_num)
        num_sundays = sum(1 for week in month_cal if week[calendar.SUNDAY] != 0)
        
        # Unrecorded days are treated as absent
        unrecorded_days = num_days_in_month - attended_days.count()
        
        if employee.employeetype == "WEEKLY":
            record.absents = absents + unrecorded_days
        else:
            record.absents = max(0, absents + unrecorded_days - num_sundays)

        record.earlyOuts = early_out_count
        record.lateDays = late_days_count
        
        # Penalties logic
        record.halfDays = max(0, early_out_count - department.earlyRelifeDays)
        
        if late_days_count > department.lateDaysCount:
            diff = late_days_count - department.lateDaysCount
            record.halfDaysDuetolate = min(2, diff) # Assuming max 2 half days penalty
            record.absentDueTolate = max(0, diff - 2)
        else:
            record.halfDaysDuetolate = 0
            record.absentDueTolate = 0

        record.save()
        return record

    def getTrioDaysAbsent(self, employee_id, month_str):
        month_date = datetime.strptime(month_str, "%Y-%m")
        employee = EmployeeRegistration.objects.filter(empId=employee_id).first()
        if not employee: return 0

        absent_dates = list(Attandence.objects.filter(
            emp=employee, mark=False, 
            date__year=month_date.year, date__month=month_date.month
        ).order_by("date").values_list("date", flat=True))

        total_trio_days = 0
        for i in range(len(absent_dates) - 1):
            # Check for Sat/Mon gap (Trio: Fri-Sat-Sun or Sat-Sun-Mon style)
            d1, d2 = absent_dates[i], absent_dates[i+1]
            if d1.weekday() == 5 and d2.weekday() == 0 and (d2 - d1).days == 2:
                total_trio_days += 1
        return total_trio_days

    def leaveTaken(self, month_str, emp_id, number):
        month_date = datetime.strptime(month_str, "%Y-%m")
        record, _ = employeeRecordEveryMonth.objects.get_or_create(
            employee__empId=emp_id, monthDate=month_date
        ) 
        record.allowedLeaveTakens = int(number)
        record.save()

class SalaryServices:
    def makeSalary(self, employee, month_str):
        att_service = AttandenceService()
        month_date = datetime.strptime(month_str, "%Y-%m")
        
        try:
            emp_salary_conf = SalaryOfEveryPerson.objects.get(emp=employee)
            monthly_salary = emp_salary_conf.salaryPerMonth
            record = employeeRecordEveryMonth.objects.get(employee=employee, monthDate=month_date)
        except Exception:
            return []

        _, num_days_in_month = calendar.monthrange(month_date.year, month_date.month)
        holiday_obj = MonthlyHolidays.objects.filter(monthName=month_date).first()
        holidays = holiday_obj.holidayPerMonth if holiday_obj else 0

        trio_absent = 0 if employee.employeetype == "WEEKLY" else att_service.getTrioDaysAbsent(employee.empId, month_str)
        
        # Net Unpaid Calculation
        unpaid_days = (record.absents + trio_absent + (record.halfDays * 0.5)) - record.allowedLeaveTakens - holidays
        record.totalunpaidDays = max(0, unpaid_days)
        
        rate_per_day = monthly_salary / num_days_in_month
        record.totalsalary = max(0, monthly_salary - (record.totalunpaidDays * rate_per_day))
        record.save()

        # Build daily view
        days_of_month = []
        all_att = att_service.get_employee_attendance_current_month(employee.empId, month_str)
        for day in range(1, num_days_in_month + 1):
            curr_date = date(month_date.year, month_date.month, day)
            att = all_att.filter(date=curr_date).first()
            
            day_data = {
                'date': day, 
                'day_name': curr_date.strftime("%a"),
                'status': "Absent", 'sign_in': "", 'sign_out': "", 'duration': ""
            }
            
            if att and att.mark:
                day_data['status'] = "Present"
                day_data['sign_in'] = att.singInTime.strftime("%I:%M %p") if att.singInTime else ""
                day_data['sign_out'] = att.singoutTime.strftime("%I:%M %p") if att.singoutTime else ""
            days_of_month.append(day_data)
            
        return days_of_month