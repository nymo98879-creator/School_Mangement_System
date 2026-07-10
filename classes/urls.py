# # from django.urls import path
# # from . import views

# # app_name = 'classes'

# # urlpatterns = [
# #     path('', views.class_list, name='class_list'),
# #     path('create/', views.class_create, name='class_create'),
# #     path('<int:pk>/', views.class_detail, name='class_detail'),
# #     path('<int:pk>/edit/', views.class_edit, name='class_edit'),
# #     path('<int:pk>/delete/', views.class_delete, name='class_delete'),
# #     path('<int:pk>/toggle-status/', views.class_toggle_status, name='class_toggle_status'),
# #     path('<int:pk>/add-student/', views.class_add_student, name='class_add_student'),
# #     path('<int:class_pk>/remove-student/<int:student_pk>/', views.class_remove_student, name='class_remove_student'),
# #     path('<int:pk>/assign-teacher/', views.class_assign_teacher, name='class_assign_teacher'),
# #     path('attendance/toggle/<int:class_pk>/<int:student_pk>/', views.class_attendance_toggle, name='class_attendance_toggle'),
# #     path('remark/save/<int:class_pk>/<int:student_pk>/', views.save_remark, name='save_remark'),  # ← This line
# #     path('save-attendance/<int:class_id>/', views.save_attendance, name='save_attendance'),  # ← Add this line
# # ]
# from django.urls import path
# from . import views

# app_name = 'classes'

# urlpatterns = [
#     # ===== CLASS URLs =====
#     path('', views.class_list, name='class_list'),
#     path('create/', views.class_create, name='class_create'),
#     path('<int:pk>/', views.class_detail, name='class_detail'),
#     path('<int:pk>/edit/', views.class_edit, name='class_edit'),
#     path('<int:pk>/delete/', views.class_delete, name='class_delete'),
#     path('<int:pk>/toggle-status/', views.class_toggle_status, name='class_toggle_status'),
#     path('<int:pk>/add-student/', views.class_add_student, name='class_add_student'),
#     path('<int:class_pk>/remove-student/<int:student_pk>/', views.class_remove_student, name='class_remove_student'),
    
    
      
#     # ===== ATTENDANCE URLs =====
#     path('save-attendance/<int:class_id>/', views.save_attendance, name='save_attendance'),
#     path('remark/save/<int:class_pk>/<int:student_pk>/', views.save_remark, name='save_remark'),
    
#     # ===== BUILDING URLs =====
#     path('buildings/', views.building_list, name='building_list'),
#     path('buildings/add/', views.building_add, name='building_add'),
#     path('buildings/<int:pk>/edit/', views.building_edit, name='building_edit'),
#     path('buildings/<int:pk>/delete/', views.building_delete, name='building_delete'),
#     path('buildings/<int:pk>/toggle-status/', views.building_toggle_status, name='building_toggle_status'),
    
#     # ===== FLOOR URLs =====
#     path('floors/', views.floor_list, name='floor_list'),
#     path('floors/add/', views.floor_add, name='floor_add'),
#     path('floors/<int:pk>/edit/', views.floor_edit, name='floor_edit'),
#     path('floors/<int:pk>/delete/', views.floor_delete, name='floor_delete'),
#     path('floors/<int:pk>/toggle-status/', views.floor_toggle_status, name='floor_toggle_status'),
    
#     # ===== ROOM URLs =====
#     path('rooms/', views.room_list, name='room_list'),
#     path('rooms/add/', views.room_add, name='room_add'),
#     path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
#     path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),
#     path('rooms/<int:pk>/toggle-status/', views.room_toggle_status, name='room_toggle_status'),
    
#     # ===== TERM URLs =====
#     path('terms/', views.term_list, name='term_list'),
#     path('terms/add/', views.term_add, name='term_add'),
#     path('terms/<int:pk>/edit/', views.term_edit, name='term_edit'),
#     path('terms/<int:pk>/delete/', views.term_delete, name='term_delete'),
#     path('terms/<int:pk>/toggle-status/', views.term_toggle_status, name='term_toggle_status'),
#     path('terms/<int:pk>/set-current/', views.term_set_current, name='term_set_current'),
    
#     # ===== TIME SLOT URLs =====
#     path('timeslots/', views.timeslot_list, name='timeslot_list'),
#     path('timeslots/add/', views.timeslot_add, name='timeslot_add'),
#     path('timeslots/<int:pk>/edit/', views.timeslot_edit, name='timeslot_edit'),
#     path('timeslots/<int:pk>/delete/', views.timeslot_delete, name='timeslot_delete'),
#     path('timeslots/<int:pk>/toggle-status/', views.timeslot_toggle_status, name='timeslot_toggle_status'),
    
#     # ===== AJAX ENDPOINTS =====
#     path('api/get-floors/<int:building_id>/', views.get_floors, name='get_floors'),
#     path('api/get-rooms/<int:floor_id>/', views.get_rooms, name='get_rooms'),
#     path('api/get-building-rooms/<int:building_id>/', views.get_building_rooms, name='get_building_rooms'),
#     path('api/get-term-details/<int:term_id>/', views.get_term_details, name='get_term_details'),
# ]

from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    # ===== CLASS URLs =====
    path('', views.class_list, name='class_list'),
    path('create/', views.class_create, name='class_create'),
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('<int:pk>/delete/', views.class_delete, name='class_delete'),
    path('<int:pk>/toggle-status/', views.class_toggle_status, name='class_toggle_status'),
    path('<int:pk>/add-student/', views.class_add_student, name='class_add_student'),
    path('<int:class_pk>/remove-student/<int:student_pk>/', views.class_remove_student, name='class_remove_student'),
    
     # ===== NEW COURSE ATTENDANCE URLs =====
    path('class-courses/<int:class_id>/', views.class_courses_view, name='class_courses_view'),
    path('class/<int:pk>/assign-courses/', views.class_assign_courses, name='class_assign_courses'),
    path('teacher/course-attendance/', views.teacher_course_attendance_view, name='teacher_course_attendance'),
    path('teacher/course-attendance/<int:course_id>/', views.teacher_course_attendance_detail, name='teacher_course_attendance_detail'),
    
    # ===== ATTENDANCE SAVE URLs =====
    path('save-attendance/<int:class_id>/', views.save_attendance, name='save_attendance'),
    path('remark/save/<int:class_pk>/<int:student_pk>/', views.save_remark, name='save_remark'),
    # ===== BUILDING URLs =====
    path('buildings/', views.building_list, name='building_list'),
    path('buildings/add/', views.building_add, name='building_add'),
    path('buildings/<int:pk>/edit/', views.building_edit, name='building_edit'),
    path('buildings/<int:pk>/delete/', views.building_delete, name='building_delete'),
    path('buildings/<int:pk>/toggle-status/', views.building_toggle_status, name='building_toggle_status'),
    
    # ===== FLOOR URLs =====
    path('floors/', views.floor_list, name='floor_list'),
    path('floors/add/', views.floor_add, name='floor_add'),
    path('floors/<int:pk>/edit/', views.floor_edit, name='floor_edit'),
    path('floors/<int:pk>/delete/', views.floor_delete, name='floor_delete'),
    path('floors/<int:pk>/toggle-status/', views.floor_toggle_status, name='floor_toggle_status'),
    
    # ===== ROOM URLs =====
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/add/', views.room_add, name='room_add'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('rooms/<int:pk>/toggle-status/', views.room_toggle_status, name='room_toggle_status'),
    
    # ===== TERM URLs =====
    path('terms/', views.term_list, name='term_list'),
    path('terms/add/', views.term_add, name='term_add'),
    path('terms/<int:pk>/edit/', views.term_edit, name='term_edit'),
    path('terms/<int:pk>/delete/', views.term_delete, name='term_delete'),
    path('terms/<int:pk>/toggle-status/', views.term_toggle_status, name='term_toggle_status'),
    path('terms/<int:pk>/set-current/', views.term_set_current, name='term_set_current'),
    
    # ===== TIME SLOT URLs =====
    path('timeslots/', views.timeslot_list, name='timeslot_list'),
    path('timeslots/add/', views.timeslot_add, name='timeslot_add'),
    path('timeslots/<int:pk>/edit/', views.timeslot_edit, name='timeslot_edit'),
    path('timeslots/<int:pk>/delete/', views.timeslot_delete, name='timeslot_delete'),
    path('timeslots/<int:pk>/toggle-status/', views.timeslot_toggle_status, name='timeslot_toggle_status'),
    
    # ===== AJAX ENDPOINTS =====
    path('api/get-floors/<int:building_id>/', views.get_floors, name='get_floors'),
    path('api/get-rooms/<int:floor_id>/', views.get_rooms, name='get_rooms'),
    path('api/get-building-rooms/<int:building_id>/', views.get_building_rooms, name='get_building_rooms'),
    path('api/get-term-details/<int:term_id>/', views.get_term_details, name='get_term_details'),
    path('api/get-available-courses/', views.get_available_courses, name='get_available_courses'),
    
    path('teacher/course-attendance/', views.teacher_course_attendance_view, name='teacher_course_attendance'),
    path('teacher/course-attendance/<int:course_id>/', views.teacher_course_attendance_detail, name='teacher_course_attendance_detail'),
]