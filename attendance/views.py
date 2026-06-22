from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from datetime import date, datetime
import csv
import json

from accounts.decorators import admin_required, teacher_or_admin_required
from .models import Attendance
from .forms import AttendanceFilterForm
from classes.models import Class
from students.models import Student
from teachers.models import Teacher


# ==================== TAKE ATTENDANCE (Shared for Admin & Teacher) ====================

@login_required
@teacher_or_admin_required
def take_attendance(request, class_id=None):
    """
    Take attendance for a class
    - Admin: Can take attendance for any class
    - Teacher: Can only take attendance for their own classes
    """
    today = date.today()
    selected_class = None
    students = []
    existing_status = {}
    
    # Get class_id from GET or POST
    class_id = request.GET.get('class_id') or request.POST.get('class_id') or class_id
    
    if class_id:
        selected_class = get_object_or_404(Class, id=class_id)
        
        # Check permissions for teachers
        if request.user.role != 'admin':
            try:
                teacher = Teacher.objects.get(user=request.user)
                if selected_class.teacher != teacher:
                    messages.error(request, 'You can only take attendance for your own classes.')
                    return redirect('attendance:teacher_attendance')
            except Teacher.DoesNotExist:
                messages.error(request, 'Teacher profile not found.')
                return redirect('attendance:teacher_attendance')
        
        students = Student.objects.filter(class_enrolled=selected_class, is_active=True)
        
        # Check if attendance already taken today
        existing_attendances = Attendance.objects.filter(
            class_obj=selected_class,
            date=today
        )
        for att in existing_attendances:
            existing_status[str(att.student.id)] = att.status
    
    # Handle POST request - Save attendance
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        attendance_date = request.POST.get('date')
        
        if not class_id:
            messages.error(request, 'Please select a class.')
            return redirect('attendance:take_attendance')
        
        if not attendance_date:
            attendance_date = today.isoformat()
        
        selected_class = get_object_or_404(Class, id=class_id)
        students_list = Student.objects.filter(class_enrolled=selected_class, is_active=True)
        
        # Get the teacher (if exists)
        marked_by = None
        if request.user.role == 'teacher':
            try:
                marked_by = Teacher.objects.get(user=request.user)
            except Teacher.DoesNotExist:
                pass
        
        # Process each student's attendance
        for student in students_list:
            status = request.POST.get(f'student_{student.id}')
            if status:
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    class_obj=selected_class,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'marked_by': marked_by
                    }
                )
                if not created:
                    attendance.status = status
                    attendance.marked_by = marked_by
                    attendance.save()
        
        messages.success(request, f'Attendance for {selected_class.name} recorded successfully!')
        
        # Redirect based on user role
        if request.user.role == 'admin':
            return redirect('attendance:admin_attendance_list')
        else:
            return redirect('attendance:teacher_attendance')
    
    # Get all classes for dropdown
    if request.user.role == 'admin':
        classes = Class.objects.filter(is_active=True)
    else:
        try:
            teacher = Teacher.objects.get(user=request.user)
            classes = Class.objects.filter(teacher=teacher, is_active=True)
        except Teacher.DoesNotExist:
            classes = []
    
    context = {
        'classes': classes,
        'selected_class': selected_class,
        'students': students,
        'today': today,
        'existing_status': existing_status,
        'total_students': len(students),
        'is_admin': request.user.role == 'admin',
    }
    
    # Use different templates based on user role
    if request.user.role == 'admin':
        return render(request, 'Backend/admin/attendance/take_attendance.html', context)
    else:
        return render(request, 'Backend/teacher/attendance/take_attendance.html', context)


# ==================== ADMIN ATTENDANCE VIEWS ====================

@login_required
@admin_required
def admin_attendance_list(request):
    """Admin view for all attendance records"""
    attendances = Attendance.objects.all().order_by('-date')
    form = AttendanceFilterForm(request.GET or None)
    
    if form.is_valid():
        class_obj = form.cleaned_data.get('class_obj')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        status = form.cleaned_data.get('status')
        student_search = form.cleaned_data.get('student')
        
        if class_obj:
            attendances = attendances.filter(class_obj=class_obj)
        if date_from:
            attendances = attendances.filter(date__gte=date_from)
        if date_to:
            attendances = attendances.filter(date__lte=date_to)
        if status:
            attendances = attendances.filter(status=status)
        if student_search:
            attendances = attendances.filter(
                Q(student__first_name__icontains=student_search) |
                Q(student__last_name__icontains=student_search) |
                Q(student__student_id__icontains=student_search)
            )
    
    paginator = Paginator(attendances, 20)
    page_number = request.GET.get('page')
    attendances_page = paginator.get_page(page_number)
    
    total_attendances = attendances.count()
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    excused_count = attendances.filter(status='excused').count()
    
    attendance_rate = 0
    if total_attendances > 0:
        attendance_rate = round((present_count / total_attendances) * 100, 1)
    
    context = {
        'attendances': attendances_page,
        'form': form,
        'total_attendances': total_attendances,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'attendance_rate': attendance_rate,
        'classes': Class.objects.filter(is_active=True),
    }
    return render(request, 'Backend/admin/attendance/attendance_list.html', context)


@login_required
@admin_required
def admin_attendance_report(request):
    """Admin view for attendance reports"""
    attendances = Attendance.objects.all().order_by('-date')
    form = AttendanceFilterForm(request.GET or None)
    
    if form.is_valid():
        class_obj = form.cleaned_data.get('class_obj')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        status = form.cleaned_data.get('status')
        student_search = form.cleaned_data.get('student')
        
        if class_obj:
            attendances = attendances.filter(class_obj=class_obj)
        if date_from:
            attendances = attendances.filter(date__gte=date_from)
        if date_to:
            attendances = attendances.filter(date__lte=date_to)
        if status:
            attendances = attendances.filter(status=status)
        if student_search:
            attendances = attendances.filter(
                Q(student__first_name__icontains=student_search) |
                Q(student__last_name__icontains=student_search) |
                Q(student__student_id__icontains=student_search)
            )
    
    total_attendances = attendances.count()
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    excused_count = attendances.filter(status='excused').count()
    
    attendance_rate = 0
    if total_attendances > 0:
        attendance_rate = round((present_count / total_attendances) * 100, 1)
    
    context = {
        'attendances': attendances,
        'form': form,
        'total_attendances': total_attendances,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'attendance_rate': attendance_rate,
        'classes': Class.objects.filter(is_active=True),
    }
    return render(request, 'Backend/admin/attendance/attendance_report.html', context)


@login_required
@admin_required
def admin_class_attendance(request):
    """Admin view for class-wise attendance"""
    classes = Class.objects.filter(is_active=True)
    for cls in classes:
        attendances = Attendance.objects.filter(class_obj=cls)
        total = attendances.count()
        present = attendances.filter(status='present').count()
        cls.attendance_rate = round((present / total) * 100, 1) if total > 0 else 0
    
    context = {'classes': classes}
    return render(request, 'Backend/admin/attendance/class_attendance.html', context)


@login_required
@admin_required
def admin_class_attendance_detail(request, class_id):
    """Admin view for detailed class attendance"""
    class_obj = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(class_enrolled=class_obj, is_active=True)
    
    student_data = []
    for student in students:
        attendances = Attendance.objects.filter(student=student, class_obj=class_obj)
        total = attendances.count()
        present = attendances.filter(status='present').count()
        absent = attendances.filter(status='absent').count()
        late = attendances.filter(status='late').count()
        excused = attendances.filter(status='excused').count()
        rate = round((present / total) * 100, 1) if total > 0 else 0
        
        student_data.append({
            'student': student,
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'rate': rate
        })
    
    context = {
        'class': class_obj,
        'student_data': student_data,
        'total_students': len(student_data),
    }
    return render(request, 'Backend/admin/attendance/class_attendance_detail.html', context)


@login_required
@admin_required
def admin_student_attendance(request, student_id):
    """View attendance for a specific student"""
    student = get_object_or_404(Student, id=student_id)
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
    return render(request, 'Backend/admin/attendance/student_attendance.html', context)


@login_required
@admin_required
def admin_edit_attendance(request, attendance_id):
    """Edit an attendance record"""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status:
            attendance.status = status
            attendance.save()
            messages.success(request, 'Attendance record updated successfully!')
            return redirect('attendance:admin_attendance_list')
    
    context = {'attendance': attendance}
    return render(request, 'Backend/admin/attendance/edit_attendance.html', context)


@login_required
@admin_required
def admin_delete_attendance(request, attendance_id):
    """Delete an attendance record"""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'Attendance record deleted successfully!')
        return redirect('attendance:admin_attendance_list')
    
    context = {'attendance': attendance}
    return render(request, 'Backend/admin/attendance/delete_attendance.html', context)


@login_required
@admin_required
def admin_export_attendance(request):
    """Export attendance data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Student Name', 'Class', 'Date', 'Status', 'Time In', 'Marked By'
    ])
    
    attendances = Attendance.objects.all().order_by('-date')
    for attendance in attendances:
        writer.writerow([
            attendance.student.student_id,
            attendance.student.get_full_name(),
            attendance.class_obj.name if attendance.class_obj else 'N/A',
            attendance.date.strftime('%Y-%m-%d'),
            attendance.get_status_display(),
            attendance.time_in.strftime('%H:%M') if attendance.time_in else '',
            attendance.marked_by.get_full_name() if attendance.marked_by else 'System'
        ])
    
    return response


# ==================== TEACHER ATTENDANCE VIEWS ====================
@login_required
@teacher_or_admin_required
def teacher_attendance_view(request):
    """Teachers can take and view attendance for their classes"""
    if request.user.role == 'admin':
        classes = Class.objects.filter(is_active=True)
    else:
        try:
            teacher = Teacher.objects.get(user=request.user)
            classes = Class.objects.filter(teacher=teacher, is_active=True)
        except Teacher.DoesNotExist:
            classes = []
    
    today = date.today()
    
    # Calculate total classes
    total_classes = classes.count()
    
    # Calculate today's attendance
    today_attendance = Attendance.objects.filter(date=today)
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            today_attendance = today_attendance.filter(class_obj__teacher=teacher)
        except Teacher.DoesNotExist:
            pass
    today_attendance_count = today_attendance.count()
    
    # Calculate total students across all classes
    total_students = Student.objects.filter(is_active=True)
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            total_students = total_students.filter(class_enrolled__teacher=teacher).distinct()
        except Teacher.DoesNotExist:
            pass
    total_students_count = total_students.count()
    
    # Calculate attendance rate
    attendance_rate = 0
    if total_students_count > 0:
        # Get present count for today
        present_today = today_attendance.filter(status='present').count()
        attendance_rate = round((present_today / total_students_count) * 100, 1)
    
    context = {
        'classes': classes,
        'total_classes': total_classes,
        'today_attendance': today_attendance_count,
        'total_students': total_students_count,
        'attendance_rate': f"{attendance_rate}%",
        'current_date': today,
    }
    return render(request, 'Backend/teacher/attendance/teacher_attendance.html', context)


@login_required
@teacher_or_admin_required
def teacher_take_attendance(request, class_id):
    """Take attendance for a specific class (Teacher version)"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Check if teacher has access
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            if class_obj.teacher != teacher:
                messages.error(request, 'You can only take attendance for your own classes.')
                return redirect('attendance:teacher_attendance')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher profile not found.')
            return redirect('attendance:teacher_attendance')
    
    students = Student.objects.filter(class_enrolled=class_obj, is_active=True)
    
    if request.method == 'POST':
        attendance_date = request.POST.get('date')
        if not attendance_date:
            attendance_date = date.today().isoformat()
        
        marked_by = class_obj.teacher if class_obj.teacher else None
        
        for student in students:
            status = request.POST.get(f'student_{student.id}')
            if status:
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    class_obj=class_obj,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'marked_by': marked_by
                    }
                )
                if not created:
                    attendance.status = status
                    attendance.marked_by = marked_by
                    attendance.save()
        
        messages.success(request, f'Attendance for {class_obj.name} recorded successfully!')
        return redirect('attendance:teacher_attendance')
    
    today = date.today()
    existing_attendances = Attendance.objects.filter(class_obj=class_obj, date=today)
    existing_status = {str(att.student.id): att.status for att in existing_attendances}
    
    context = {
        'class': class_obj,
        'students': students,
        'today': today,
        'existing_status': existing_status,
        'total_students': students.count(),
    }
    return render(request, 'Backend/teacher/attendance/take_attendance.html', context)

@login_required
@teacher_or_admin_required
def teacher_attendance_history(request, class_id):
    """View attendance history for a specific class"""
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Check if teacher has access
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            if class_obj.teacher != teacher:
                messages.error(request, 'You can only view attendance for your own classes.')
                return redirect('attendance:teacher_attendance')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher profile not found.')
            return redirect('attendance:teacher_attendance')
    
    attendances = Attendance.objects.filter(class_obj=class_obj).order_by('-date')
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if status:
        attendances = attendances.filter(status=status)
    
    # Calculate statistics
    total_records = attendances.count()
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    excused_count = attendances.filter(status='excused').count()
    
    # Handle CSV export
    if request.GET.get('export') == 'csv':
        return export_attendance_csv(attendances, class_obj)
    
    context = {
        'class': class_obj,
        'attendances': attendances,
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
    }
    return render(request, 'Backend/teacher/attendance/attendance_history.html', context)


def export_attendance_csv(attendances, class_obj):
    """Export attendance records to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{class_obj.name}_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student Name', 'Student ID', 'Date', 'Status', 'Time In', 'Remarks'
    ])
    
    for attendance in attendances:
        writer.writerow([
            attendance.student.get_full_name(),
            attendance.student.student_id,
            attendance.date.strftime('%Y-%m-%d'),
            attendance.get_status_display(),
            attendance.time_in.strftime('%H:%M') if attendance.time_in else '',
            attendance.remarks or ''
        ])
    
    return response

# ==================== TEACHER STUDENT ATTENDANCE ====================

@login_required
@teacher_or_admin_required
def teacher_student_attendance(request, student_id):
    """View attendance for a specific student (Teacher view)"""
    student = get_object_or_404(Student, id=student_id)
    
    # Check if teacher has access to this student
    if request.user.role != 'admin':
        try:
            teacher = Teacher.objects.get(user=request.user)
            # Check if student is in any of the teacher's classes
            student_classes = Class.objects.filter(teacher=teacher, is_active=True)
            if not student.class_enrolled or student.class_enrolled not in student_classes:
                messages.error(request, 'You do not have permission to view this student.')
                return redirect('attendance:teacher_attendance')
        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher profile not found.')
            return redirect('attendance:teacher_attendance')
    
    # Get attendance records
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    
    # Calculate statistics
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