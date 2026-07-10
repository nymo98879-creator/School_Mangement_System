
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    # Admin URLs - Full Access
    path('admin/students/', views.admin_student_list, name='admin_student_list'),
    path('admin/teachers/', views.admin_teacher_list, name='admin_teacher_list'),
    path('admin/classes/', views.admin_class_list, name='admin_class_list'),
    path('admin/courses/', views.admin_course_list, name='admin_course_list'),
    path('admin/attendance/', views.admin_attendance_report, name='admin_attendance_report'),
    
    # Teacher URLs - Limited Access
    path('teacher/classes/', views.teacher_class_view, name='teacher_class_view'),
    # Remove this line - attendance is handled by attendance app
    # path('teacher/attendance/', views.teacher_attendance_view, name='teacher_attendance'),
    path('teacher/students/', views.teacher_student_view, name='teacher_student_view'),
    path('teacher/student/<int:student_id>/', views.teacher_student_detail, name='teacher_student_detail'),
    path('teacher/student/<int:student_id>/attendance/', views.teacher_student_detail, name='teacher_student_attendance'),
    path('teacher/class/<int:pk>/', views.teacher_class_detail, name='teacher_class_detail'),
]