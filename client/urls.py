from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard,name='dashboard'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('notifications',views.notifications,name='notification'),
    path('clinics',views.clinics,name='clinic'),
    path('appointments',views.appointments,name='appointment'),
    path('support',views.support,name='support'),
    path('register',views.register_request,name='register'),
    path('login',views.login_request,name='view_login'),
    path('logout',views.logout_request,name='logout'),
    path('terms-and-conditions',views.terms_and_conditions,name='terms_and_conditions'),
    path('privacy-policy',views.privacy_policy,name='privacy_policy'),
    path('about',views.about,name='about'),
    path('forgot-password',views.forgot_password,name='view_forgot_password'),
    path('search',views.search,name='search'),
    path('medicalrecords',views.medicalrecords,name='medicalrecords'),
    path('consultations',views.consultations,name='consultations'),
]