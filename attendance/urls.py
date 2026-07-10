from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Teacher URLs
    path('teacher/', views.teacher_attendance_view, name='teacher_attendance'),
    path('teacher/take/<int:class_id>/', views.teacher_take_attendance, name='teacher_take_attendance'),
    path('teacher/history/<int:class_id>/', views.teacher_attendance_history, name='teacher_attendance_history'),
    path('teacher/student-attendance/<int:student_id>/', views.teacher_student_attendance, name='teacher_student_attendance'),
    path('teacher/course/', views.teacher_course_attendance, name='teacher_course_attendance'),
    # Admin URLs
    path('admin/list/', views.admin_attendance_list, name='admin_attendance_list'),
    path('admin/take/', views.take_attendance, name='admin_take_attendance'),
    path('admin/report/', views.admin_attendance_report, name='admin_attendance_report'),
    path('admin/course/', views.admin_course_attendance, name='admin_course_attendance'),
    path('admin/course/<int:course_id>/', views.admin_course_attendance_detail, name='admin_course_attendance_detail'),
    path('admin/class/', views.admin_class_attendance, name='admin_class_attendance'),
    path('admin/class/<int:class_id>/', views.admin_class_attendance_detail, name='admin_class_attendance_detail'),
    path('admin/student/<int:student_id>/', views.admin_student_attendance, name='admin_student_attendance'),
    path('admin/edit/<int:attendance_id>/', views.admin_edit_attendance, name='admin_edit_attendance'),
    path('admin/delete/<int:attendance_id>/', views.admin_delete_attendance, name='admin_delete_attendance'),
    path('admin/export/', views.admin_export_attendance, name='admin_export_attendance'),
]