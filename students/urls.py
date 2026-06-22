from django.urls import path
from django.urls import reverse
from . import views

app_name = 'students'

urlpatterns = [
    # Dashboard
    path('', views.student_dashboard, name='student_dashboard'),
    path('list/', views.student_list, name='student_list'),
    
    # Student Management
    path('add/', views.student_add, name='student_add'),
    path('bulk-upload/', views.student_bulk_upload, name='student_bulk_upload'),
    path('download-template/', views.download_template, name='download_template'),
    
    # Student CRUD
    path('<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('<int:pk>/toggle-status/', views.student_toggle_status, name='student_toggle_status'),
    
    # Export
    path('export/csv/', views.student_export_csv, name='student_export_csv'),
    
    # ===== QR CODE MANAGEMENT =====
    # Generate QR for ALL students
    path('generate-all-qr/', views.generate_all_qr, name='generate_all_qr'),
    
    # Generate Registration QR (for student self-registration)
    path('generate-registration-qr/', views.generate_registration_qr, name='generate_registration_qr'),
    path('download-registration-qr/', views.download_registration_qr, name='download_registration_qr'),
    
    # Individual QR (for detail page)
    path('<int:pk>/download-qr/', views.download_qr_code, name='download_qr_code'),
    
    # Student Self-Registration via QR
    path('scan-register/', views.student_scan_register, name='scan_register'),
    path('register/<str:student_id>/', views.student_self_register, name='student_self_register'),
    path('verify-student-qr/', views.verify_student_qr, name='verify_student_qr'),
    
    # Public Registration
    path('register/', views.student_self_register_form, name='student_self_register_form'),
    path('register-success/', views.student_register_success, name='student_register_success'),
]