# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import login, authenticate, logout
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Q, Count
# from datetime import datetime, date, timedelta

# from .forms import UserRegistrationForm, UserLoginForm
# from .decorators import admin_required, teacher_required, teacher_or_admin_required

# # Import models from their correct apps
# from students.models import Student
# from teachers.models import Teacher
# from attendance.models import Attendance
# from attendance.utils import attendance_rate_percent
# from courses.models import Course, Faculty, Department, Major
# from classes.models import Class

# # ==================== AUTHENTICATION VIEWS ====================

# def register(request):
#     if request.user.is_authenticated:
#         return redirect('accounts:dashboard')
    
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
            
#             # Auto-create profile based on role
#             if user.role == 'teacher':
#                 from teachers.models import Teacher
#                 Teacher.objects.create(
#                     user=user,
#                     teacher_id=f'TCH-{user.id:04d}',
#                     first_name=user.first_name or 'Teacher',
#                     last_name=user.last_name or 'User',
#                     date_of_birth='2000-01-01',
#                     gender='M',
#                     phone='',
#                     email=user.email,
#                     address='',
#                     qualification='',
#                     specialization='',
#                     is_active=True
#                 )
#                 messages.success(request, f'Teacher account created successfully! Please complete your profile.')
            
#             elif user.role == 'student':
#                 from students.models import Student
#                 Student.objects.create(
#                     user=user,
#                     student_id=f'STU-{user.id:04d}',
#                     first_name=user.first_name or 'Student',
#                     last_name=user.last_name or 'User',
#                     date_of_birth='2000-01-01',
#                     gender='M',
#                     phone='',
#                     email=user.email,
#                     address='',
#                     guardian_name='',
#                     guardian_phone='',
#                     is_active=True
#                 )
#                 messages.success(request, f'Student account created successfully! Please complete your profile.')
            
#             login(request, user)
#             messages.success(request, f'Account created successfully! Welcome {user.username}!')
#             return redirect('accounts:dashboard')
#     else:
#         form = UserRegistrationForm()
    
#     return render(request, 'auth/register.html', {'form': form})

# def user_login(request):
#     if request.user.is_authenticated:
#         return redirect('accounts:dashboard')
    
#     if request.method == 'POST':
#         form = UserLoginForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.success(request, f'Welcome back, {user.username}!')
#                 next_url = request.GET.get('next')
#                 if next_url:
#                     return redirect(next_url)
#                 return redirect('accounts:dashboard')
#         else:
#             messages.error(request, 'Invalid username or password.')
#     else:
#         form = UserLoginForm()
    
#     return render(request, 'auth/login.html', {'form': form})

# @login_required
# def user_logout(request):
#     logout(request)
#     messages.info(request, 'You have been logged out successfully.')
#     return redirect('accounts:login')


# # ==================== DASHBOARD VIEWS ====================
# @login_required
# def dashboard(request):
#     user = request.user
#     context = {'user': user}
    
#     # Check Teacher model FIRST
#     if Teacher.objects.filter(user=user).exists():
#         # ===== TEACHER DASHBOARD =====
#         try:
#             teacher = Teacher.objects.get(user=user)
#             classes = Class.objects.filter(teacher=teacher).distinct()
#             # Get students using ManyToMany
#             students = Student.objects.filter(classes_enrolled__in=classes, is_active=True).distinct()
            
#             # Get course IDs from classes
#             # course_ids = [c.course.id for c in classes if c.course]
#             # Get all course IDs from all classes (flatten the list)
#             course_ids = []
#             for c in classes:
#                 for course in c.courses.all():  # Changed from 'course' to 'courses.all()'
#                     course_ids.append(course.id)
                
#             today = date.today()
#             # FIX: Use course instead of class_obj
#             today_attendance = Attendance.objects.filter(
#                 course_id__in=course_ids,  # Changed from class_obj__in
#                 date=today
#             ) if course_ids else []
            
#             present_today = (
#                 today_attendance.filter(status='present')
#                 .values('student_id')
#                 .distinct()
#                 .count()
#                 if today_attendance else 0
#             )
            
#         except Teacher.DoesNotExist:
#             teacher = None
#             classes = []
#             students = []
#             today_attendance = []
#             present_today = 0
        
#         if isinstance(students, list):
#             total_students = len(students)
#         else:
#             total_students = students.count()
        
#         attendance_rate = 0
#         if total_students > 0:
#             attendance_rate = attendance_rate_percent(present_today, total_students)
        
#         context.update({
#             'teacher': teacher,
#             'my_classes': classes,
#             'my_students': students,
#             'total_students': total_students,
#             'today_attendance': len(today_attendance) if today_attendance else 0,
#             'present_today': present_today,
#             'attendance_rate': f"{attendance_rate}%",
#             'current_date': today,
#             'current_time': datetime.now(),
#             'recent_activities': [],
#             'is_teacher': True,
#             'user_role': 'teacher',
#         })
#         return render(request, 'Backend/dashboard/teacher_dashboard.html', context)
    
#     # Check Student model SECOND
#     elif Student.objects.filter(user=user).exists():
#         # ===== STUDENT DASHBOARD =====
#         try:
#             student = Student.objects.get(user=user)
#         except Student.DoesNotExist:
#             student = None
        
#         # Get all classes the student is enrolled in
#         my_classes = []
#         if student:
#             my_classes = student.classes_enrolled.filter(is_active=True)
        
#         context.update({
#             'student': student,
#             'my_classes': my_classes,
#             'current_date': date.today(),
#             'current_time': datetime.now(),
#             'is_student': True,
#             'user_role': 'student',
#         })
#         return render(request, 'Backend/dashboard/student_dashboard.html', context)
    
#     else:
#         # ===== ADMIN DASHBOARD (FALLBACK) =====
#         today = date.today()

#         # ── Attendance figures scoped BY COURSE ────────────────────────────────
#         from courses.models import Course as CourseModel
#         from django.db.models import Count, Q

#         active_courses = CourseModel.objects.filter(is_active=True).order_by('code')

#         today_by_course = []
#         total_present_today   = 0
#         total_absent_today    = 0
#         total_late_today      = 0
#         total_excused_today   = 0
#         total_today_records   = 0

#         for course in active_courses:
#             qs = Attendance.objects.filter(course=course, date=today)
#             present  = qs.filter(status='present').count()
#             absent   = qs.filter(status='absent').count()
#             late     = qs.filter(status='late').count()
#             excused  = qs.filter(status='excused').count()
#             total    = qs.count()

#             if total == 0:
#                 continue  # Skip courses with no attendance today

#             total_present_today  += present
#             total_absent_today   += absent
#             total_late_today     += late
#             total_excused_today  += excused
#             total_today_records  += total

#             rate = attendance_rate_percent(present, total)

#             today_by_course.append({
#                 'course'  : course,
#                 'present' : present,
#                 'absent'  : absent,
#                 'late'    : late,
#                 'excused' : excused,
#                 'total'   : total,
#                 'rate'    : rate,
#             })

#         # Overall attendance rate across all courses today
#         total_students = Student.objects.count()
#         attendance_percentage = attendance_rate_percent(total_present_today, total_students)

#         # ── Other counts ───────────────────────────────────────────────────────
#         total_attendances  = Attendance.objects.count()
#         total_faculties    = Faculty.objects.count()
#         total_departments  = Department.objects.count()
#         total_majors       = Major.objects.count()
#         total_courses      = CourseModel.objects.count()
#         total_teachers     = Teacher.objects.count()
#         total_classes      = Class.objects.count()

#         context.update({
#             # University Structure Counts
#             'total_faculties'   : total_faculties,
#             'total_departments' : total_departments,
#             'total_majors'      : total_majors,
#             'total_courses'     : total_courses,

#             # Main Counts
#             'total_students'    : total_students,
#             'total_teachers'    : total_teachers,
#             'total_classes'     : total_classes,
#             'total_attendances' : total_attendances,

#             # Today's Attendance — course-level breakdown
#             'today_by_course'       : today_by_course,
#             'today_attendance'      : total_today_records,
#             'present_today'         : total_present_today,
#             'absent_today'          : total_absent_today,
#             'late_today'            : total_late_today,
#             'excused_today'         : total_excused_today,
#             'attendance_percentage' : attendance_percentage,
#             'attendance_rate'       : f"{attendance_percentage}%",

#             # Date/Time
#             'current_date'      : today,
#             'current_time'      : datetime.now(),
#             'recent_activities' : get_recent_activities(),
#             'is_admin'          : True,
#             'user_role'         : 'admin',
#         })
#         return render(request, 'Backend/dashboard/admin_dashboard.html', context)

    
    
# def get_recent_activities():
#     """Get recent activities for admin dashboard"""
#     activities = []
    
#     # Get recent attendance records
#     recent_attendances = Attendance.objects.order_by('-created_at')[:5]
#     for att in recent_attendances:
#         status_display = att.get_status_display() if hasattr(att, 'get_status_display') else att.status
#         # FIX: Use course instead of class_obj
#         course_name = att.course.name if att.course else 'Unknown'  # Changed from class_obj
#         student_name = att.student.get_full_name() if att.student else 'Unknown'
        
#         activities.append({
#             'title': f'Attendance marked for {student_name}',
#             'description': f'Status: {status_display} in {course_name}',
#             'time': att.created_at,
#             'type': 'success' if att.status == 'present' else 'warning' if att.status == 'late' else 'danger',
#             'icon': 'fa-check-circle' if att.status == 'present' else 'fa-clock' if att.status == 'late' else 'fa-times-circle',
#             'icon_color': 'green' if att.status == 'present' else 'orange' if att.status == 'late' else 'red',
#             'status': att.status,
#             'status_display': status_display
#         })
    
#     # Get recent student additions
#     recent_students = Student.objects.order_by('-created_at')[:3]
#     for student in recent_students:
#         activities.append({
#             'title': f'New student enrolled: {student.get_full_name()}',
#             'description': f'Student ID: {student.student_id}',
#             'time': student.created_at,
#             'type': 'success',
#             'icon': 'fa-user-plus',
#             'icon_color': 'blue'
#         })
    
#     # Sort by time (most recent first)
#     activities.sort(key=lambda x: x['time'], reverse=True)
    
#     return activities[:10]

# # ==================== ADMIN VIEWS ====================

# @login_required
# @admin_required
# def admin_student_list(request):
#     students = Student.objects.all()
#     return render(request, 'Backend/admin/student/student_list.html', {'students': students})

# @login_required
# @admin_required
# def admin_teacher_list(request):
#     teachers = Teacher.objects.all()
#     return render(request, 'Backend/admin/teacher/teacher_list.html', {'teachers': teachers})

# @login_required
# @admin_required
# def admin_class_list(request):
#     classes = Class.objects.all()
#     return render(request, 'Backend/admin/class/class_list.html', {'classes': classes})

# @login_required
# @admin_required
# def admin_course_list(request):
#     courses = Course.objects.all()
#     return render(request, 'Backend/admin/course/course_list.html', {'courses': courses})

# @login_required
# @admin_required
# def admin_attendance_report(request):
#     attendances = Attendance.objects.all()
#     return render(request, 'Backend/attendance/attendance_report.html', {'attendances': attendances})


# # ==================== TEACHER VIEWS ====================

# @login_required
# @teacher_required
# def teacher_class_view(request):
#     """Teacher's class view - shows classes assigned to teacher"""
#     try:
#         teacher = Teacher.objects.get(user=request.user)
#         classes = Class.objects.filter(teacher=teacher).distinct()
#         courses = Course.objects.filter(classes__in=classes, is_active=True).distinct()
#         today = date.today()
        
#         # Get students for each class using ManyToMany
#         for class_obj in classes:
#             class_obj.students = class_obj.enrolled_students.filter(is_active=True)
#             class_obj.student_count = class_obj.students.count()
            
#             if class_obj.course:
#                 present_today_count = Attendance.objects.filter(
#                     course=class_obj.course, 
#                     date=today, 
#                     status='present',
#                     student_id__in=class_obj.students.values_list('id', flat=True)
#                 ).values('student_id').distinct().count()
#                 class_obj.present_today = min(present_today_count, class_obj.student_count)
#             else:
#                 class_obj.present_today = 0
            
#         # Calculate today's attendance count across courses
#         course_ids = [c.id for c in courses]
#         today_attendance = Attendance.objects.filter(date=today, course_id__in=course_ids) if course_ids else []
#         today_attendance_count = today_attendance.count()
        
#         # Calculate total students across classes using ManyToMany
#         total_students = Student.objects.filter(classes_enrolled__in=classes, is_active=True).distinct()
#         total_students_count = total_students.count()
        
#         # Calculate attendance rate
#         attendance_rate = 0
#         if total_students_count > 0:
#             present_today = (
#                 today_attendance.filter(status='present')
#                 .values('student_id')
#                 .distinct()
#                 .count()
#             )
#             attendance_rate = attendance_rate_percent(present_today, total_students_count)
        
#         context = {
#             'classes': classes,
#             'teacher': teacher,
#             'total_students': total_students_count,
#             'today_attendance': today_attendance_count,
#             'attendance_rate': f"{attendance_rate}%",
#             'current_date': today,
#             'current_time': datetime.now(),
#         }
#         return render(request, 'Backend/teacher/class/teacher_class_list.html', context)
        
#     except Teacher.DoesNotExist:
#         messages.error(request, 'Teacher profile not found.')
#         return redirect('accounts:dashboard')
#     except Exception as e:
#         messages.error(request, f'Error loading classes: {str(e)}')
#         return redirect('accounts:dashboard')


# @login_required
# @teacher_or_admin_required
# def teacher_student_view(request):
#     """Teachers can only view students in their assigned classes"""
#     if request.user.role == 'admin':
#         students = Student.objects.filter(is_active=True)
#         classes_count = Class.objects.count()
#     else:
#         try:
#             teacher = Teacher.objects.get(user=request.user)
#             classes = Class.objects.filter(teacher=teacher).distinct()
#             # FIX: Use the new ManyToMany relationship
#             students = Student.objects.filter(
#                 classes_enrolled__in=classes,
#                 is_active=True
#             ).distinct()
#             classes_count = classes.count()
#         except Teacher.DoesNotExist:
#             students = []
#             classes_count = 0
    
#     # Calculate counts correctly
#     total_students = students.count() if hasattr(students, 'count') else len(students)
#     active_students = students.filter(is_active=True).count() if hasattr(students, 'filter') else len([s for s in students if s.is_active])
    
#     context = {
#         'students': students,
#         'classes_count': classes_count,
#         'total_students': total_students,
#         'active_students': active_students,
#     }
#     return render(request, 'Backend/teacher/student/student_list.html', context)


# @login_required
# @teacher_or_admin_required
# def teacher_student_detail(request, student_id):
#     """Teachers can view student details and attendance history"""
#     student = get_object_or_404(Student, id=student_id)
    
#     if request.user.role != 'admin':
#         try:
#             teacher = Teacher.objects.get(user=request.user)
#             # FIX: Check if student is enrolled in any of teacher's classes
#             teacher_classes = Class.objects.filter(teacher=teacher).distinct()
#             if not student.classes_enrolled.filter(id__in=teacher_classes).exists():
#                 messages.error(request, 'You do not have permission to view this student.')
#                 return redirect('accounts:teacher_student_view')
#         except Teacher.DoesNotExist:
#             messages.error(request, 'Teacher profile not found.')
#             return redirect('accounts:teacher_student_view')
    
#     attendances = Attendance.objects.filter(student=student).order_by('-date')
    
#     total = attendances.count()
#     present = attendances.filter(status='present').count()
#     absent = attendances.filter(status='absent').count()
#     late = attendances.filter(status='late').count()
#     excused = attendances.filter(status='excused').count()
    
#     attendance_rate = 0
#     if total > 0:
#         attendance_rate = attendance_rate_percent(present, total)
    
#     context = {
#         'student': student,
#         'attendances': attendances,
#         'total': total,
#         'present': present,
#         'absent': absent,
#         'late': late,
#         'excused': excused,
#         'attendance_rate': attendance_rate,
#     }
#     return render(request, 'Backend/teacher/attendance/student_attendance_detail.html', context)


# @login_required
# @teacher_required
# def teacher_class_detail(request, pk):
#     """View details of a specific class for teacher"""
#     try:
#         teacher = Teacher.objects.get(user=request.user)
#         class_obj = get_object_or_404(Class, teacher=teacher, pk=pk)
        
#         # Get students using the new ManyToMany relationship
#         students = class_obj.enrolled_students.filter(is_active=True)
        
#         today = date.today()
#         for student in students:
#             if class_obj.course:
#                 att = Attendance.objects.filter(
#                     student=student, 
#                     course=class_obj.course, 
#                     date=today
#                 ).first()
#             else:
#                 att = None
#             student.attendance_status = att.status if att else None
        
#         context = {
#             'class': class_obj,
#             'students': students,
#             'total_students': students.count(),
#             'today': today,
#         }
#         return render(request, 'Backend/teacher/class/class_detail.html', context)
        
#     except Teacher.DoesNotExist:
#         messages.error(request, 'Teacher profile not found.')
#         return redirect('accounts:dashboard')
#     except Class.DoesNotExist:
#         messages.error(request, 'Class not found.')
#         return redirect('accounts:teacher_class_view')
    

# @login_required
# def settings_view(request):
#     user = request.user
    
#     # Detect role and set layout
#     if Teacher.objects.filter(user=user).exists():
#         user_role = 'teacher'
#         is_teacher = True
#         is_admin = False
#         is_student = False
#         layout = 'Backend/layouts/teacher_layout.html'
#     elif Student.objects.filter(user=user).exists():
#         user_role = 'student'
#         is_teacher = False
#         is_admin = False
#         is_student = True
#         layout = 'Backend/layouts/student_layout.html'
#     else:
#         user_role = 'admin'
#         is_teacher = False
#         is_admin = True
#         is_student = False
#         layout = 'Backend/layouts/admin_layout.html'
    
#     context = {
#         'title': 'Settings',
#         'user_role': user_role,
#         'layout': layout,
#         'role_label': {
#             'admin': 'Administrator',
#             'teacher': 'Teacher',
#             'student': 'Student'
#         }.get(user_role, 'Student'),
#         'is_admin': is_admin,
#         'is_teacher': is_teacher,
#         'is_student': is_student,
#         'user': user,
#     }
    
#     return render(request, 'Backend/setting/settings.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, date, timedelta

from .forms import UserRegistrationForm, UserLoginForm
from .decorators import admin_required, teacher_required, teacher_or_admin_required

# Import models from their correct apps
from students.models import Student
from teachers.models import Teacher
from attendance.models import Attendance
from attendance.utils import attendance_rate_percent
from courses.models import Course, Faculty, Department, Major
from classes.models import Class

# ==================== AUTHENTICATION VIEWS ====================

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-create profile based on role
            if user.role == 'teacher':
                from teachers.models import Teacher
                Teacher.objects.create(
                    user=user,
                    teacher_id=f'TCH-{user.id:04d}',
                    first_name=user.first_name or 'Teacher',
                    last_name=user.last_name or 'User',
                    date_of_birth='2000-01-01',
                    gender='M',
                    phone='',
                    email=user.email,
                    address='',
                    qualification='',
                    specialization='',
                    is_active=True
                )
                messages.success(request, f'Teacher account created successfully! Please complete your profile.')
            
            elif user.role == 'student':
                from students.models import Student
                Student.objects.create(
                    user=user,
                    student_id=f'STU-{user.id:04d}',
                    first_name=user.first_name or 'Student',
                    last_name=user.last_name or 'User',
                    date_of_birth='2000-01-01',
                    gender='M',
                    phone='',
                    email=user.email,
                    address='',
                    guardian_name='',
                    guardian_phone='',
                    is_active=True
                )
                messages.success(request, f'Student account created successfully! Please complete your profile.')
            
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome {user.username}!')
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# ==================== DASHBOARD VIEWS ====================
@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    # Check Teacher model FIRST
    if Teacher.objects.filter(user=user).exists():
        # ===== TEACHER DASHBOARD =====
        try:
            teacher = Teacher.objects.get(user=user)
            
            # Get classes assigned to this teacher
            classes = Class.objects.filter(teacher=teacher, is_active=True).distinct()

            # Get course IDs from classes assigned to this teacher
            class_course_ids = list(
                Course.objects.filter(class_offerings__in=classes, is_active=True)
                .values_list('id', flat=True)
                .distinct()
            )

            # Also include courses directly assigned to this teacher
            direct_course_ids = list(
                Course.objects.filter(teacher=teacher, is_active=True)
                .values_list('id', flat=True)
                .distinct()
            )

            course_ids = list(set(class_course_ids) | set(direct_course_ids))

            # Get courses for this teacher from both class assignments and direct course assignments
            courses = Course.objects.filter(id__in=course_ids, is_active=True).distinct()

            # Get students (union of class enrollment and course enrollment)
            from django.db.models import Q
            students = Student.objects.filter(
                Q(classes_enrolled__in=classes) | Q(courses__in=courses),
                is_active=True
            ).distinct()

            today = date.today()

            # Get today's attendance for all courses
            today_attendance = Attendance.objects.filter(
                course__in=courses,
                date=today
            ) if courses.exists() else Attendance.objects.none()
            
            # Get present students today
            present_today = (
                today_attendance.filter(status='present')
                .values('student_id')
                .distinct()
                .count()
            )
            
            # Get total attendance records today
            total_attendance_today = today_attendance.count()
            
            # Calculate attendance rate
            total_students = students.count()
            attendance_rate = 0
            if total_students > 0:
                attendance_rate = attendance_rate_percent(present_today, total_students)
            
        except Teacher.DoesNotExist:
            teacher = None
            classes = Class.objects.none()
            students = Student.objects.none()
            courses = Course.objects.none()
            today_attendance = Attendance.objects.none()
            present_today = 0
            total_attendance_today = 0
            total_students = 0
            attendance_rate = 0
        
        context.update({
            'teacher': teacher,
            'my_classes': classes,
            'my_students': students,
            'my_courses': courses,
            'total_students': total_students,
            'total_classes': classes.count(),
            'total_courses': courses.count(),
            'today_attendance': total_attendance_today,
            'present_today': present_today,
            'attendance_rate': f"{attendance_rate}%",
            'current_date': today,
            'current_time': datetime.now(),
            'recent_activities': get_recent_activities_teacher(teacher),
            'is_teacher': True,
            'user_role': 'teacher',
        })
        return render(request, 'Backend/dashboard/teacher_dashboard.html', context)
    
    # Check Student model SECOND
    elif Student.objects.filter(user=user).exists():
        # ===== STUDENT DASHBOARD =====
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            student = None
        
        # Get all classes the student is enrolled in
        my_classes = Class.objects.none()
        if student:
            my_classes = student.classes_enrolled.filter(is_active=True)
        
        # Get courses from enrolled classes using M2M
        course_ids = []
        for class_obj in my_classes:
            for course in class_obj.courses.all():
                course_ids.append(course.id)
        course_ids = list(set(course_ids))
        courses = Course.objects.filter(id__in=course_ids, is_active=True).distinct()
        
        # Get today's attendance
        today = date.today()
        today_attendance = Attendance.objects.filter(student=student, date=today)
        
        context.update({
            'student': student,
            'my_classes': my_classes,
            'my_courses': courses,
            'total_classes': my_classes.count(),
            'total_courses': courses.count(),
            'today_attendance': today_attendance.count(),
            'current_date': today,
            'current_time': datetime.now(),
            'is_student': True,
            'user_role': 'student',
        })
        return render(request, 'Backend/dashboard/student_dashboard.html', context)
    
    else:
        # ===== ADMIN DASHBOARD (FALLBACK) =====
        today = date.today()

        # ── Attendance figures scoped BY COURSE ────────────────────────────────
        from courses.models import Course as CourseModel
        from django.db.models import Count, Q

        active_courses = CourseModel.objects.filter(is_active=True).order_by('code')

        today_by_course = []
        total_present_today   = 0
        total_absent_today    = 0
        total_late_today      = 0
        total_excused_today   = 0
        total_today_records   = 0

        for course in active_courses:
            qs = Attendance.objects.filter(course=course, date=today)
            present  = qs.filter(status='present').count()
            absent   = qs.filter(status='absent').count()
            late     = qs.filter(status='late').count()
            excused  = qs.filter(status='excused').count()
            total    = qs.count()

            if total == 0:
                continue

            total_present_today  += present
            total_absent_today   += absent
            total_late_today     += late
            total_excused_today  += excused
            total_today_records  += total

            rate = attendance_rate_percent(present, total)

            today_by_course.append({
                'course'  : course,
                'present' : present,
                'absent'  : absent,
                'late'    : late,
                'excused' : excused,
                'total'   : total,
                'rate'    : rate,
            })

        # Overall attendance rate across all courses today
        total_students = Student.objects.count()
        attendance_percentage = attendance_rate_percent(total_present_today, total_students)

        # ── Other counts ───────────────────────────────────────────────────────
        total_attendances  = Attendance.objects.count()
        total_faculties    = Faculty.objects.count()
        total_departments  = Department.objects.count()
        total_majors       = Major.objects.count()
        total_courses      = CourseModel.objects.count()
        total_teachers     = Teacher.objects.count()
        total_classes      = Class.objects.count()

        context.update({
            # University Structure Counts
            'total_faculties'   : total_faculties,
            'total_departments' : total_departments,
            'total_majors'      : total_majors,
            'total_courses'     : total_courses,

            # Main Counts
            'total_students'    : total_students,
            'total_teachers'    : total_teachers,
            'total_classes'     : total_classes,
            'total_attendances' : total_attendances,

            # Today's Attendance — course-level breakdown
            'today_by_course'       : today_by_course,
            'today_attendance'      : total_today_records,
            'present_today'         : total_present_today,
            'absent_today'          : total_absent_today,
            'late_today'            : total_late_today,
            'excused_today'         : total_excused_today,
            'attendance_percentage' : attendance_percentage,
            'attendance_rate'       : f"{attendance_percentage}%",

            # Date/Time
            'current_date'      : today,
            'current_time'      : datetime.now(),
            'recent_activities' : get_recent_activities(),
            'is_admin'          : True,
            'user_role'         : 'admin',
        })
        return render(request, 'Backend/dashboard/admin_dashboard.html', context)


def get_recent_activities_teacher(teacher):
    """Get recent activities for teacher dashboard"""
    activities = []
    
    if not teacher:
        return activities
    
    # Get classes taught by teacher
    classes = Class.objects.filter(teacher=teacher, is_active=True)
    
    # Get course IDs from classes using M2M
    class_course_ids = list(
        Course.objects.filter(class_offerings__in=classes, is_active=True)
        .values_list('id', flat=True)
        .distinct()
    )

    # Also include courses directly assigned to this teacher
    direct_course_ids = list(
        Course.objects.filter(teacher=teacher, is_active=True)
        .values_list('id', flat=True)
        .distinct()
    )

    course_ids = list(set(class_course_ids) | set(direct_course_ids))
    
    # Get recent attendance records for teacher's courses
    if course_ids:
        recent_attendances = Attendance.objects.filter(
            course_id__in=course_ids
        ).order_by('-created_at')[:5]
        
        for att in recent_attendances:
            status_display = att.get_status_display() if hasattr(att, 'get_status_display') else att.status
            course_name = att.course.name if att.course else 'Unknown'
            student_name = att.student.get_full_name() if att.student else 'Unknown'
            
            activities.append({
                'title': f'Attendance marked for {student_name}',
                'description': f'Status: {status_display} in {course_name}',
                'time': att.created_at,
                'type': 'success' if att.status == 'present' else 'warning' if att.status == 'late' else 'danger',
                'icon': 'fa-check-circle' if att.status == 'present' else 'fa-clock' if att.status == 'late' else 'fa-times-circle',
                'icon_color': 'green' if att.status == 'present' else 'orange' if att.status == 'late' else 'red',
                'status': att.status,
                'status_display': status_display
            })
    
    # Sort by time (most recent first)
    activities.sort(key=lambda x: x['time'], reverse=True)
    
    return activities[:10]


def get_recent_activities():
    """Get recent activities for admin dashboard"""
    activities = []
    
    # Get recent attendance records
    recent_attendances = Attendance.objects.order_by('-created_at')[:5]
    for att in recent_attendances:
        status_display = att.get_status_display() if hasattr(att, 'get_status_display') else att.status
        course_name = att.course.name if att.course else 'Unknown'
        student_name = att.student.get_full_name() if att.student else 'Unknown'
        
        activities.append({
            'title': f'Attendance marked for {student_name}',
            'description': f'Status: {status_display} in {course_name}',
            'time': att.created_at,
            'type': 'success' if att.status == 'present' else 'warning' if att.status == 'late' else 'danger',
            'icon': 'fa-check-circle' if att.status == 'present' else 'fa-clock' if att.status == 'late' else 'fa-times-circle',
            'icon_color': 'green' if att.status == 'present' else 'orange' if att.status == 'late' else 'red',
            'status': att.status,
            'status_display': status_display
        })
    
    # Get recent student additions
    recent_students = Student.objects.order_by('-created_at')[:3]
    for student in recent_students:
        activities.append({
            'title': f'New student enrolled: {student.get_full_name()}',
            'description': f'Student ID: {student.student_id}',
            'time': student.created_at,
            'type': 'success',
            'icon': 'fa-user-plus',
            'icon_color': 'blue'
        })
    
    # Sort by time (most recent first)
    activities.sort(key=lambda x: x['time'], reverse=True)
    
    return activities[:10]

# ==================== ADMIN VIEWS ====================

@login_required
@admin_required
def admin_student_list(request):
    students = Student.objects.all()
    return render(request, 'Backend/admin/student/student_list.html', {'students': students})

@login_required
@admin_required
def admin_teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'Backend/admin/teacher/teacher_list.html', {'teachers': teachers})

@login_required
@admin_required
def admin_class_list(request):
    classes = Class.objects.all()
    return render(request, 'Backend/admin/class/class_list.html', {'classes': classes})

@login_required
@admin_required
def admin_course_list(request):
    courses = Course.objects.all()
    return render(request, 'Backend/admin/course/course_list.html', {'courses': courses})

@login_required
@admin_required
def admin_attendance_report(request):
    attendances = Attendance.objects.all()
    return render(request, 'Backend/attendance/attendance_report.html', {'attendances': attendances})


# ==================== TEACHER VIEWS ====================

@login_required
@teacher_required
def teacher_class_view(request):
    """Teacher's class view - shows classes assigned to teacher"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        classes = Class.objects.filter(teacher=teacher, is_active=True).distinct()
        
        # Get courses from classes using M2M
        course_ids = []
        for class_obj in classes:
            for course in class_obj.courses.all():
                course_ids.append(course.id)
        course_ids = list(set(course_ids))
        courses = Course.objects.filter(id__in=course_ids, is_active=True).distinct()
        
        today = date.today()
        
        # Get students for each class using ManyToMany
        for class_obj in classes:
            class_obj.students = class_obj.enrolled_students.filter(is_active=True)
            class_obj.student_count = class_obj.students.count()
            
            # Get courses for this class
            class_courses = class_obj.courses.all()
            
            # Get students from these courses as well
            course_student_ids = []
            for course in class_courses:
                course_students = Student.objects.filter(courses=course, is_active=True)
                course_student_ids.extend(course_students.values_list('id', flat=True))
            
            # Combine class students with course students
            all_student_ids = set(class_obj.students.values_list('id', flat=True)) | set(course_student_ids)
            class_obj.all_students = Student.objects.filter(id__in=all_student_ids, is_active=True).distinct()
            class_obj.all_student_count = class_obj.all_students.count()
            
            # Count present students across all students in this class/courses
            present_count = 0
            for course in class_courses:
                present_count += Attendance.objects.filter(
                    course=course, 
                    date=today, 
                    status='present',
                    student_id__in=all_student_ids
                ).values('student_id').distinct().count()
            
            class_obj.present_today = min(present_count, class_obj.all_student_count)
            class_obj.course_list = class_courses
            
        # Calculate today's attendance count across courses
        today_attendance = Attendance.objects.filter(date=today, course_id__in=course_ids) if course_ids else Attendance.objects.none()
        today_attendance_count = today_attendance.count()
        
        # Calculate total students across classes using ManyToMany (union of class and course enrollment)
        total_students = Student.objects.filter(
            Q(classes_enrolled__in=classes) | Q(courses__in=courses),
            is_active=True
        ).distinct()
        total_students_count = total_students.count()
        
        # Calculate attendance rate
        attendance_rate = 0
        if total_students_count > 0:
            present_today = (
                today_attendance.filter(status='present')
                .values('student_id')
                .distinct()
                .count()
            )
            attendance_rate = attendance_rate_percent(present_today, total_students_count)
        
        # ===== PAGINATION (unified footer) =====
        per_page = request.GET.get('per_page', '10')
        try:
            per_page = int(per_page)
        except (TypeError, ValueError):
            per_page = 10
        if per_page not in (5, 10, 20):
            per_page = 10

        classes = list(classes)
        paginator = Paginator(classes, per_page)
        page_number = request.GET.get('page')
        classes_page = paginator.get_page(page_number)

        context = {
            'classes': classes_page,
            'per_page': per_page,
            'courses': courses,
            'teacher': teacher,
            'total_students': total_students_count,
            'today_attendance': today_attendance_count,
            'attendance_rate': f"{attendance_rate}%",
            'current_date': today,
            'current_time': datetime.now(),
            'total_classes': len(classes),
            'total_courses': courses.count(),
        }
        return render(request, 'Backend/teacher/class/teacher_class_list.html', context)
        
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('accounts:dashboard')
    except Exception as e:
        messages.error(request, f'Error loading classes: {str(e)}')
        return redirect('accounts:dashboard')


@login_required
@teacher_or_admin_required
def teacher_student_view(request):
    """Teachers can only view students in their assigned classes"""
    search_query = request.GET.get('search', '')
    class_filter = request.GET.get('class_filter', '')
    course_filter = request.GET.get('course_filter', '')
    
    if request.user.role == 'admin':
        students = Student.objects.filter(is_active=True)
        classes = Class.objects.filter(is_active=True)
        courses = Course.objects.filter(is_active=True)
        classes_count = Class.objects.count()
    else:
        try:
            teacher = Teacher.objects.get(user=request.user)
            classes = Class.objects.filter(teacher=teacher, is_active=True).distinct()
            
            class_course_ids = list(
                Course.objects.filter(class_offerings__in=classes, is_active=True)
                .values_list('id', flat=True)
                .distinct()
            )
            direct_course_ids = list(
                Course.objects.filter(teacher=teacher, is_active=True)
                .values_list('id', flat=True)
                .distinct()
            )
            course_ids = list(set(class_course_ids) | set(direct_course_ids))
            courses = Course.objects.filter(id__in=course_ids, is_active=True).distinct()
            
            students = Student.objects.filter(
                Q(classes_enrolled__in=classes) | Q(courses__in=courses),
                is_active=True
            ).distinct()
            classes_count = classes.count()
        except Teacher.DoesNotExist:
            students = Student.objects.none()
            classes = Class.objects.none()
            courses = Course.objects.none()
            classes_count = 0
    
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(guardian_name__icontains=search_query)
        ).distinct()
    
    if class_filter:
        students = students.filter(classes_enrolled__id=class_filter).distinct()
    
    if course_filter:
        students = students.filter(courses__id=course_filter).distinct()
    
    total_students = students.count()
    active_students = students.filter(is_active=True).count()

    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(students, per_page)
    page_number = request.GET.get('page')
    students_page = paginator.get_page(page_number)

    context = {
        'students': students_page,
        'per_page': per_page,
        'per_page_params': 'per_page=' + str(per_page),
        'classes': classes,
        'courses': courses,
        'classes_count': classes_count,
        'total_students': total_students,
        'active_students': active_students,
        'search_query': search_query,
        'class_filter': class_filter,
        'course_filter': course_filter,
    }
    return render(request, 'Backend/teacher/student/student_list.html', context)


@login_required
@teacher_or_admin_required
def teacher_student_ajax(request):
    """AJAX endpoint for teacher student search/filter"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    search_query = request.GET.get('search', '')
    class_filter = request.GET.get('class_filter', '')
    course_filter = request.GET.get('course_filter', '')
    
    if request.user.role == 'admin':
        students = Student.objects.filter(is_active=True)
    else:
        try:
            teacher = Teacher.objects.get(user=request.user)
            classes = Class.objects.filter(teacher=teacher, is_active=True).distinct()
            
            class_course_ids = list(
                Course.objects.filter(class_offerings__in=classes, is_active=True)
                .values_list('id', flat=True)
                .distinct()
            )
            direct_course_ids = list(
                Course.objects.filter(teacher=teacher, is_active=True)
                .values_list('id', flat=True)
                .distinct()
            )
            course_ids = list(set(class_course_ids) | set(direct_course_ids))
            courses = Course.objects.filter(id__in=course_ids, is_active=True).distinct()
            
            students = Student.objects.filter(
                Q(classes_enrolled__in=classes) | Q(courses__in=courses),
                is_active=True
            ).distinct()
        except Teacher.DoesNotExist:
            return JsonResponse({'students': [], 'total': 0})
    
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(guardian_name__icontains=search_query)
        ).distinct()
    
    if class_filter:
        students = students.filter(classes_enrolled__id=class_filter).distinct()
    
    if course_filter:
        students = students.filter(courses__id=course_filter).distinct()
    
    students = students.select_related('user', 'major').prefetch_related('classes_enrolled', 'courses')[:50]
    
    student_data = []
    for student in students:
        classes_list = [c.name for c in student.classes_enrolled.all()] or ['Not Assigned']
        student_data.append({
            'id': student.id,
            'full_name': student.get_full_name(),
            'first_name': student.first_name,
            'last_name': student.last_name,
            'student_id': student.student_id,
            'email': student.email,
            'classes': classes_list,
            'is_active': student.is_active,
            'enrollment_date': student.enrollment_date.strftime('%b %d, %Y') if student.enrollment_date else '',
            'guardian_name': student.guardian_name,
            'guardian_phone': student.guardian_phone,
        })
    
    return JsonResponse({
        'students': student_data,
        'total': len(student_data)
    })


@login_required
@teacher_or_admin_required
def teacher_student_detail(request, student_id):
    """Teachers can view student details and attendance history"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            # Check if student is enrolled in any of teacher's classes or courses
            teacher_classes = Class.objects.filter(teacher=teacher, is_active=True).distinct()
            teacher_courses = Course.objects.filter(
                class_offerings__in=teacher_classes, is_active=True
            ).distinct() | Course.objects.filter(teacher=teacher, is_active=True).distinct()
            if not (student.classes_enrolled.filter(id__in=teacher_classes).exists() or 
                    student.courses.filter(id__in=teacher_courses).exists()):
                messages.error(request, 'You do not have permission to view this student.')
                return redirect('accounts:teacher_student_view')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher profile not found.')
            return redirect('accounts:teacher_student_view')
    
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    
    total = attendances.count()
    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()
    late = attendances.filter(status='late').count()
    excused = attendances.filter(status='excused').count()
    
    attendance_rate = 0
    if total > 0:
        attendance_rate = attendance_rate_percent(present, total)
    
    context = {
        'student': student,
        'attendances': attendances,
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'excused': excused,
        'attendance_rate': attendance_rate,
    }
    return render(request, 'Backend/teacher/attendance/student_attendance_detail.html', context)


@login_required
@teacher_required
def teacher_class_detail(request, pk):
    """View details of a specific class for teacher"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        class_obj = get_object_or_404(Class, teacher=teacher, pk=pk)
        
        # Get students using the ManyToMany relationship
        students = class_obj.enrolled_students.filter(is_active=True)
        
        today = date.today()
        
        # Get all courses for this class
        class_courses = class_obj.courses.all()
        
        for student in students:
            # Check attendance for any course in this class
            att = None
            for course in class_courses:
                att = Attendance.objects.filter(
                    student=student, 
                    course=course, 
                    date=today
                ).first()
                if att:
                    break
            student.attendance_status = att.status if att else None
        
        context = {
            'class': class_obj,
            'students': students,
            'total_students': students.count(),
            'today': today,
            'courses': class_courses,
        }
        return render(request, 'Backend/teacher/class/class_detail.html', context)
        
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('accounts:dashboard')
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('accounts:teacher_class_view')
    

@login_required
def settings_view(request):
    user = request.user
    
    # Detect role and set layout
    if Teacher.objects.filter(user=user).exists():
        user_role = 'teacher'
        is_teacher = True
        is_admin = False
        is_student = False
        layout = 'Backend/layouts/teacher_layout.html'
    elif Student.objects.filter(user=user).exists():
        user_role = 'student'
        is_teacher = False
        is_admin = False
        is_student = True
        layout = 'Backend/layouts/student_layout.html'
    else:
        user_role = 'admin'
        is_teacher = False
        is_admin = True
        is_student = False
        layout = 'Backend/layouts/admin_layout.html'
    
    context = {
        'title': 'Settings',
        'user_role': user_role,
        'layout': layout,
        'role_label': {
            'admin': 'Administrator',
            'teacher': 'Teacher',
            'student': 'Student'
        }.get(user_role, 'Student'),
        'is_admin': is_admin,
        'is_teacher': is_teacher,
        'is_student': is_student,
        'user': user,
    }
    
    return render(request, 'Backend/setting/settings.html', context)