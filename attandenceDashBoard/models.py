from django.db import models
from django.contrib.auth.models import AbstractUser ,Group, Permission

# Create your models here.

class CustomUserFace(AbstractUser):
    department = models.TextField(max_length=100)
    phonenumber = models.TextField(max_length=10)
    
    def __str__(self):
        return self.first_name + " " + self.last_name

class Department(models.Model):
    deprtment = models.CharField(max_length=15)
    lat = models.FloatField()
    lon = models.FloatField()
    def __str__(self):
        return self.deprtment

class EmployeeRegistration(models.Model):
    deprt = models.ForeignKey(Department,on_delete=models.PROTECT,default = None,null=True)
    name = models.CharField(max_length=100,blank=False,null=False)
    empId = models.CharField(unique=True,max_length=10,blank=False,null=False)
    img = models.ImageField(upload_to='employee_images/', blank=True, null=False)
    sonOf =  models.CharField(max_length=100,blank=False,null=False)
    mobile1 =  models.IntegerField(max_length=10,blank=False,null=False)
    mobile2 =  models.IntegerField(max_length=10,blank=False,null=False)
    adharcard =  models.IntegerField(max_length=12,blank=False,null=False)
    refrerName =  models.CharField(max_length=100,blank=False,null=False)
    referMob =  models.IntegerField(max_length=10,blank=False,null=False)
    pAddress =  models.CharField(max_length=1000,blank=False,null=False)
    pcity =  models.CharField(max_length=100,blank=False,null=False)
    pState = models.CharField(max_length=100,blank=False,null=False)
    cAddress =  models.CharField(max_length=100,blank=False,null=False)
    ccity =  models.CharField(max_length=100,blank=False,null=False)
    cState = models.CharField(max_length=100,blank=False,null=False)
    oEmployerName =  models.CharField(max_length=100,blank=False,null=False)
    oEmpMob =  models.IntegerField(max_length=10,blank=False,null=False)

    
    def __str__(self):
        return self.name

class StoreFaces(models.Model):
    front = models.ImageField(upload_to='profile_photos', blank=True, null=True)
    right = models.ImageField(upload_to='profile_photos', blank=True, null=True)
    left = models.ImageField(upload_to='profile_photos', blank=True, null=True)
    emp = models.ForeignKey(EmployeeRegistration, on_delete=models.CASCADE)
    def __str__(self):
        return self.emp.name
    
class Attandence(models.Model):
    emp = models.ForeignKey(EmployeeRegistration, on_delete=models.CASCADE)
    date = models.DateField(default=None)
    singInTime = models.TimeField(default=None,null=True)
    singoutTime =  models.TimeField(default=None,null=True)
    mark = models.BooleanField(choices=[(True, 'Present'), (False, 'Absent')],default=False)
    siginImage = models.ImageField(upload_to='static/signin/',default=None)
    location = models.CharField(max_length=300,default=None,null=True)
   
    def __str__(self):
        return f"{self.emp.name} - {self.date} - {'Present' if self.mark else 'Absent'}"   

