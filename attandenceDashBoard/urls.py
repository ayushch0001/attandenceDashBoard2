"""
URL configuration for faceAttandenceIgkv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import register,logout_view, login_view,createSuperUser,register_faces,getData,lateDataView ,success,markAttandence,attendance_list ,export_attendance_to_excel,gethistorydata,export_month_attendance_to_excel


urlpatterns = [
    path("register/", register, name="register"),
    path('registerFace/',register_faces , name='registerFaces'),
    path('attendance/', attendance_list, name='attendance_list'),
    path('attendence/',markAttandence , name='attendance'),
    path('',success , name='success_page'),
    path('export-attendance/', export_attendance_to_excel, name='export_attendance'),
    # path('markattendance/', mark_attendance_api, name='mark'),
    path('gethistorydata/', gethistorydata, name='gethistorydata'),
    path('getMonthData/', export_month_attendance_to_excel, name='getMonthData'),
    # path('month/', getmonthsData, name='month'),
    path('hoursData/', lateDataView, name='hoursData'),
    path('getData/', getData, name='getData'),
    path('createSuperUser/', createSuperUser, name='createSuperUser'),
    path('login/', login_view, name='login'),
    path('logout/',logout_view, name = 'logout'),
    
    
     

]

