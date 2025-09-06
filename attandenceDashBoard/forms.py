from django.shortcuts import render, redirect

from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.hashers import make_password


from attandenceDashBoard.models import CustomUserFace ,Attandence, EmployeeRegistration, StoreFaces

class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUserFace
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']



class EmployeeRegistrationForm(forms.ModelForm):
    class Meta :
        model = EmployeeRegistration
        fields = ['deprt','name','empId','img','sonOf','mobile1','mobile2','adharcard','refrerName','referMob','pAddress','pcity','pState','cAddress','ccity','cState','oEmployerName','oEmpMob']



class StoreFacesForm(forms.ModelForm):  # Fixed class name
    class Meta:
        model = StoreFaces
        fields = ['front', 'right', 'left', 'emp']
        widgets = {
            'emp': forms.RadioSelect()  # Corrected field widget assignment
        }


