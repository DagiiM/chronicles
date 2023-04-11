from django.shortcuts import render
from django.http import HttpResponse

def register_request(request):
    rendered = render(request, 'register.html')
    return HttpResponse(rendered)
    
def login_request(request):
    rendered = render(request, 'login.html')
    return HttpResponse(rendered)
    
def logout_request(request):
    rendered = render(request, 'login.html')
    return HttpResponse(rendered)
    
def dashboard(request):
    rendered = render(request, 'basic/dashboard.html')
    return HttpResponse(rendered)

def notifications(request):
    tabs = [
        {'id': 'tab1', 'title': 'New Notifications', 'template_name': 'notifications/new_notifications.html'},
        {'id': 'tab2', 'title': 'Read Notifications', 'template_name': 'notifications/read_notifications.html'},
        {'id': 'tab3', 'title': 'All Notifications', 'template_name': 'notifications/all_notifications.html'},
    ]
    context = {'tabs': tabs}
    rendered = render(request, 'notifications/index.html',context=context)
    return HttpResponse(rendered)

def medicalrecords(request):
    tabs = [
        {'id': 'tab1', 'title': 'About Medical Records', 'template_name': 'medicalrecords/about_medical_records.html'},
        {'id': 'tab2', 'title': 'My Medical History', 'template_name': 'medicalrecords/medical_history.html'},
        {'id': 'tab3', 'title': 'Prescription Refill', 'template_name': 'medicalrecords/prescription_refill.html'},
    ]
    context = {'tabs': tabs}
    rendered = render(request, 'medicalrecords/index.html',context=context)
    return HttpResponse(rendered)

def consultations(request):
    tabs = [
        {'id': 'tab1', 'title': 'Consult', 'template_name': 'consultations/consult.html'},
        {'id': 'tab2', 'title': 'About Consultations', 'template_name': 'consultations/about_consultations.html'},

    ]
    context = {'tabs': tabs}
    rendered = render(request, 'consultations/index.html',context=context)
    return HttpResponse(rendered)

def clinics(request):
    tabs = [
        {'id': 'tab1', 'title': 'Clinics Near Me', 'template_name': 'clinics/clinics_near_me.html'},
        {'id': 'tab2', 'title': 'New Clinics', 'template_name': 'clinics/new_clinics.html'},
        {'id': 'tab3', 'title': 'Previously Visited Clinics', 'template_name': 'clinics/visited_clinics.html'},
    ]
    context = {'tabs': tabs}
    rendered = render(request, 'clinics/index.html',context=context)
    return HttpResponse(rendered)
    
def appointments(request):
    tabs = [
        {'id': 'tab1', 'title': 'About Appointments', 'template_name': 'appointments/about_appointment.html'},
        {'id': 'tab2', 'title': 'Book Appointment', 'template_name': 'appointments/book_appointment.html'},
        {'id': 'tab3', 'title': 'My Recent Appointments', 'template_name': 'appointments/recent_appointment.html'},
    ]
    context = {'tabs': tabs}
    
    rendered = render(request, 'appointments/index.html',context)
    return HttpResponse(rendered)
    
def support(request):
    rendered = render(request, 'contact/support.html')
    return HttpResponse(rendered)
    
def about(request):
    rendered = render(request, 'contact/about.html')
    return HttpResponse(rendered)
    
def terms_and_conditions(request):
    rendered = render(request, 'contact/terms-conditions.html')
    return HttpResponse(rendered)
    
def privacy_policy(request):
    rendered = render(request, 'contact/privacy-policy.html')
    return HttpResponse(rendered)

def forgot_password(request):
    rendered = render(request, 'forgot_password.html')
    return HttpResponse(rendered)

def search(request):
    context={"data":{
        'detail':"Found Something",
        'url':"http://eleso.ltd",
    }}
    return JsonResponse(request, context)