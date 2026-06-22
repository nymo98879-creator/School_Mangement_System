from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # ===== FACULTY URLs =====
    path('faculties/', views.faculty_list, name='faculty_list'),
    path('faculties/add/', views.faculty_add, name='faculty_add'),
    path('faculties/<int:pk>/edit/', views.faculty_edit, name='faculty_edit'),
    path('faculties/<int:pk>/delete/', views.faculty_delete, name='faculty_delete'),
    path('faculties/<int:pk>/toggle-status/', views.faculty_toggle_status, name='faculty_toggle_status'),
    
    # ===== DEPARTMENT URLs =====
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('departments/<int:pk>/toggle-status/', views.department_toggle_status, name='department_toggle_status'),
    
    # ===== MAJOR URLs =====
    path('majors/', views.major_list, name='major_list'),
    path('majors/add/', views.major_add, name='major_add'),
    path('majors/<int:pk>/edit/', views.major_edit, name='major_edit'),
    path('majors/<int:pk>/delete/', views.major_delete, name='major_delete'),
    path('majors/<int:pk>/toggle-status/', views.major_toggle_status, name='major_toggle_status'),
    
    # ===== COURSE URLs =====
    path('', views.course_list, name='course_list'),
    path('add/', views.course_add, name='course_add'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('<int:pk>/toggle-status/', views.course_toggle_status, name='course_toggle_status'),
    path('export/csv/', views.course_export_csv, name='course_export_csv'),
]