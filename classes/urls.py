from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # ===== BUILDING URLS =====
    path('buildings/', views.building_list, name='building_list'),
    path('buildings/add/', views.building_add, name='building_add'),
    path('buildings/edit/<int:pk>/', views.building_edit, name='building_edit'),
    path('buildings/delete/<int:pk>/', views.building_delete, name='building_delete'),
    path('buildings/toggle/<int:pk>/', views.building_toggle_status, name='building_toggle_status'),
    
    # ===== FLOOR URLS =====
    path('floors/', views.floor_list, name='floor_list'),
    path('floors/add/', views.floor_add, name='floor_add'),
    path('floors/edit/<int:pk>/', views.floor_edit, name='floor_edit'),
    path('floors/delete/<int:pk>/', views.floor_delete, name='floor_delete'),
    path('floors/toggle/<int:pk>/', views.floor_toggle_status, name='floor_toggle_status'),
    
    # ===== ROOM URLS =====
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/add/', views.room_add, name='room_add'),
    path('rooms/edit/<int:pk>/', views.room_edit, name='room_edit'),
    path('rooms/delete/<int:pk>/', views.room_delete, name='room_delete'),
    path('rooms/toggle/<int:pk>/', views.room_toggle_status, name='room_toggle_status'),
    
    # ===== TERM URLS =====
    path('terms/', views.term_list, name='term_list'),
    path('terms/add/', views.term_add, name='term_add'),
    path('terms/edit/<int:pk>/', views.term_edit, name='term_edit'),
    path('terms/delete/<int:pk>/', views.term_delete, name='term_delete'),
    path('terms/toggle/<int:pk>/', views.term_toggle_status, name='term_toggle_status'),
    path('terms/set-current/<int:pk>/', views.term_set_current, name='term_set_current'),
    
    # ===== TIME SLOT URLS =====
    path('timeslots/', views.timeslot_list, name='timeslot_list'),
    path('timeslots/add/', views.timeslot_add, name='timeslot_add'),
    path('timeslots/edit/<int:pk>/', views.timeslot_edit, name='timeslot_edit'),
    path('timeslots/delete/<int:pk>/', views.timeslot_delete, name='timeslot_delete'),
    path('timeslots/toggle/<int:pk>/', views.timeslot_toggle_status, name='timeslot_toggle_status'),
    
    # ===== CLASS ADMIN URLS =====
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    path('classes/edit/<int:pk>/', views.class_edit, name='class_edit'),
    path('classes/delete/<int:pk>/', views.class_delete, name='class_delete'),
    path('classes/toggle/<int:pk>/', views.class_toggle_status, name='class_toggle_status'),
    path('classes/<int:pk>/add-students/', views.class_add_student, name='class_add_student'),
    path('classes/<int:class_pk>/remove-student/<int:student_pk>/', views.class_remove_student, name='class_remove_student'),
    path('classes/<int:pk>/assign-courses/', views.class_assign_courses, name='class_assign_courses'),
    
    # ===== CLASS TEACHER URLS =====
    path('teacher/classes/', views.teacher_class_list, name='teacher_class_list'),
    path('teacher/class/<int:class_id>/courses/', views.class_courses_view, name='class_courses_view'),
    path('teacher/courses/', views.teacher_course_attendance_view, name='teacher_course_attendance'),
    path('teacher/course/<int:course_id>/attendance/', views.teacher_course_attendance_detail, name='teacher_course_attendance_detail'),
    
    # ===== ATTENDANCE SAVE URLS =====
    path('save-attendance/<int:class_id>/', views.save_attendance, name='save_attendance'),
    path('remark/save/<int:class_pk>/<int:student_pk>/', views.save_remark, name='save_remark'),
    path('save-course-attendance/<int:course_id>/', views.save_course_attendance, name='save_course_attendance'),
    path('course-remark/save/<int:course_pk>/<int:student_pk>/', views.save_course_remark, name='save_course_remark'),
    
    # ===== AJAX ENDPOINTS =====
    path('ajax/get-floors/<int:building_id>/', views.get_floors, name='get_floors'),
    path('ajax/get-rooms/<int:floor_id>/', views.get_rooms, name='get_rooms'),
    path('ajax/get-building-rooms/<int:building_id>/', views.get_building_rooms, name='get_building_rooms'),
    path('ajax/get-term-details/<int:term_id>/', views.get_term_details, name='get_term_details'),
    path('ajax/get-available-courses/', views.get_available_courses, name='get_available_courses'),
    path('ajax/course/<int:course_id>/students/', views.get_course_students, name='get_course_students'),
    path('ajax/class/<int:class_id>/students/', views.get_class_students, name='get_class_students'),
]