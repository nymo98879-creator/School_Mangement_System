from django.shortcuts import render, redirect, get_object_or_404
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
from courses.models import Course, Faculty, Department, Major  # Add these imports
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
    
    if user.role == 'admin':
        today = date.today()
        
        # Get all attendance counts
        total_attendances = Attendance.objects.count()
        today_attendance = Attendance.objects.filter(date=today)
        present_today = today_attendance.filter(status='present').count()
        absent_today = today_attendance.filter(status='absent').count()
        late_today = today_attendance.filter(status='late').count()
        excused_today = today_attendance.filter(status='excused').count()
        
        # Calculate attendance percentage
        total_students = Student.objects.count()
        attendance_percentage = 0
        if total_students > 0:
            attendance_percentage = round((present_today / total_students) * 100, 1)
        
        # Get all counts for sidebar
        total_faculties = Faculty.objects.count()
        total_departments = Department.objects.count()
        total_majors = Major.objects.count()
        total_courses = Course.objects.count()
        total_teachers = Teacher.objects.count()
        total_classes = Class.objects.count()
        
        context.update({
            # University Structure Counts
            'total_faculties': total_faculties,
            'total_departments': total_departments,
            'total_majors': total_majors,
            'total_courses': total_courses,
            
            # Main Counts
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'total_attendances': total_attendances,
            
            # Attendance Details
            'today_attendance': today_attendance.count(),
            'present_today': present_today,
            'absent_today': absent_today,
            'late_today': late_today,
            'excused_today': excused_today,
            'attendance_percentage': attendance_percentage,
            'attendance_rate': f"{attendance_percentage}%",
            
            # Date/Time
            'current_date': today,
            'current_time': datetime.now(),
            'recent_activities': get_recent_activities(),
        })
        return render(request, 'Backend/dashboard/admin_dashboard.html', context)
    
    elif user.role == 'teacher':
        try:
            teacher = Teacher.objects.get(user=user)
            classes = Class.objects.filter(teacher=teacher, is_active=True)
            students = Student.objects.filter(class_enrolled__in=classes).distinct()
        except Teacher.DoesNotExist:
            teacher = None
            classes = []
            students = []
        
        today = date.today()
        today_attendance = Attendance.objects.filter(
            class_obj__in=classes,
            date=today
        ) if classes else []
        
        present_today = today_attendance.filter(status='present').count() if today_attendance else 0
        
        if isinstance(students, list):
            total_students = len(students)
        else:
            total_students = students.count()
        
        attendance_rate = 0
        if total_students > 0:
            attendance_rate = round((present_today / total_students) * 100, 1)
        
        context.update({
            'teacher': teacher,
            'my_classes': classes,
            'my_students': students,
            'total_students': total_students,
            'today_attendance': len(today_attendance) if today_attendance else 0,
            'present_today': present_today,
            'attendance_rate': f"{attendance_rate}%",
            'current_date': today,
            'current_time': datetime.now(),
            'recent_activities': [],
        })
        return render(request, 'Backend/dashboard/teacher_dashboard.html', context)
    
    else:
        # Student Dashboard
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            student = None
        
        my_classes = []
        if student and student.class_enrolled:
            my_classes = [student.class_enrolled]
        
        context.update({
            'student': student,
            'my_classes': my_classes,
            'current_date': date.today(),
            'current_time': datetime.now(),
        })
        return render(request, 'Backend/dashboard/student_dashboard.html', context)


def get_recent_activities():
    """Get recent activities for admin dashboard"""
    activities = []
    
    # Get recent attendance records
    recent_attendances = Attendance.objects.order_by('-created_at')[:5]
    for att in recent_attendances:
        status_display = att.get_status_display() if hasattr(att, 'get_status_display') else att.status
        class_name = att.class_obj.name if att.class_obj else 'Unknown'
        student_name = att.student.get_full_name() if att.student else 'Unknown'
        
        activities.append({
            'title': f'Attendance marked for {student_name}',
            'description': f'Status: {status_display} in {class_name}',
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
    """View for teachers to see their classes"""
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('accounts:dashboard')
    
    # Get teacher's classes
    classes = Class.objects.filter(teacher=teacher, is_active=True)
    
    # Get today's date and current time
    today = date.today()
    current_time = datetime.now()
    
    # Get today's attendance count
    today_attendance = Attendance.objects.filter(
        class_obj__in=classes,
        date=today
    ).count() if classes else 0
    
    # Calculate total students
    total_students = Student.objects.filter(class_enrolled__in=classes).count() if classes else 0
    
    # Calculate attendance rate
    present_today = Attendance.objects.filter(
        class_obj__in=classes,
        date=today,
        status='present'
    ).count() if classes else 0
    
    if total_students > 0:
        attendance_rate = round((present_today / total_students) * 100, 1)
    else:
        attendance_rate = 0
    
    context = {
        'classes': classes,
        'teacher': teacher,
        'total_classes': classes.count(),
        'total_students': total_students,
        'today_attendance': today_attendance,
        'attendance_rate': f"{attendance_rate}%",
        'today': today,
        'current_time': current_time,  # Added this line
    }
    
    return render(request, 'Backend/teacher/class/teacher_class_list.html', context)
@login_required
@teacher_or_admin_required
def teacher_student_view(request):
    """Teachers can only view students in their assigned classes"""
    if request.user.role == 'admin':
        students = Student.objects.filter(is_active=True)
        classes_count = Class.objects.count()
    else:
        try:
            teacher = Teacher.objects.get(user=request.user)
            classes = Class.objects.filter(teacher=teacher, is_active=True)
            students = Student.objects.filter(
                class_enrolled__in=classes,
                is_active=True
            ).distinct()
            classes_count = classes.count()
        except Teacher.DoesNotExist:
            students = []
            classes_count = 0
    
    # Calculate counts correctly
    total_students = students.count() if hasattr(students, 'count') else len(students)
    active_students = students.filter(is_active=True).count() if hasattr(students, 'filter') else len([s for s in students if s.is_active])
    
    context = {
        'students': students,
        'classes_count': classes_count,
        'total_students': total_students,
        'active_students': active_students,
    }
    return render(request, 'Backend/teacher/student/student_list.html', context)


@login_required
@teacher_or_admin_required
def teacher_student_detail(request, student_id):
    """Teachers can view student details and attendance history"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            if student.class_enrolled and student.class_enrolled.teacher != teacher:
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
        attendance_rate = round((present / total) * 100, 1)
    
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
@teacher_or_admin_required
def teacher_class_detail(request, pk):
    """Teachers can view detailed class information with attendance"""
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            if class_obj.teacher != teacher:
                messages.error(request, 'You do not have permission to view this class.')
                return redirect('accounts:teacher_class_view')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher profile not found.')
            return redirect('accounts:teacher_class_view')
    
    students = Student.objects.filter(class_enrolled=class_obj, is_active=True)
    
    today = date.today()
    for student in students:
        att = Attendance.objects.filter(student=student, class_obj=class_obj, date=today).first()
        student.attendance_status = att.status if att else None
    
    total_students = students.count()
    present_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='present').count()
    absent_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='absent').count()
    late_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='late').count()
    excused_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='excused').count()
    
    present_percentage = round((present_count / total_students) * 100, 1) if total_students > 0 else 0
    absent_percentage = round((absent_count / total_students) * 100, 1) if total_students > 0 else 0
    late_percentage = round((late_count / total_students) * 100, 1) if total_students > 0 else 0
    excused_percentage = round((excused_count / total_students) * 100, 1) if total_students > 0 else 0
    
    context = {
        'class': class_obj,
        'students': students,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'present_percentage': present_percentage,
        'absent_percentage': absent_percentage,
        'late_percentage': late_percentage,
        'excused_percentage': excused_percentage,
        'today': today,
    }
    return render(request, 'Backend/teacher/class/class_detail.html', context)