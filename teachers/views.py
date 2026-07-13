from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from accounts.decorators import admin_required
from .models import Teacher
from .forms import TeacherForm, TeacherSearchForm
from classes.models import Class
import csv
from datetime import datetime

@login_required
@admin_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    form = TeacherSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        gender_filter = form.cleaned_data.get('gender_filter')
        status_filter = form.cleaned_data.get('status_filter')
        
        if search:
            teachers = teachers.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(teacher_id__icontains=search) |
                Q(email__icontains=search)
            )
        
        if gender_filter:
            teachers = teachers.filter(gender=gender_filter)
        
        if status_filter == 'active':
            teachers = teachers.filter(is_active=True)
        elif status_filter == 'inactive':
            teachers = teachers.filter(is_active=False)
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(teachers, per_page)
    page_number = request.GET.get('page')
    teachers_page = paginator.get_page(page_number)
    
    context = {
        'teachers': teachers_page,
        'per_page': per_page,
        'form': form,
        'total_teachers': Teacher.objects.count(),
        'active_teachers': Teacher.objects.filter(is_active=True).count(),
        'inactive_teachers': Teacher.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/teacher/teacher_list.html', context)

@login_required
@admin_required
def teacher_add(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Teacher {teacher.get_full_name()} added successfully!')
            return redirect('teachers:teacher_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherForm()
    
    context = {
        'form': form,
        'title': 'Add New Teacher',
        'is_edit': False,
    }
    return render(request, 'Backend/admin/teacher/teacher_form.html', context)

@login_required
@admin_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f'Teacher {teacher.get_full_name()} updated successfully!')
            return redirect('teachers:teacher_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherForm(instance=teacher)
    
    context = {
        'form': form,
        'title': 'Edit Teacher',
        'teacher': teacher,
        'is_edit': True,
    }
    return render(request, 'Backend/admin/teacher/teacher_form.html', context)

@login_required
@admin_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    classes = Class.objects.filter(teacher=teacher, is_active=True)
    context = {
        'teacher': teacher,
        'classes': classes,
    }
    return render(request, 'Backend/admin/teacher/teacher_detail.html', context)

@login_required
@admin_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        teacher_name = teacher.get_full_name()
        teacher.delete()
        messages.success(request, f'Teacher {teacher_name} deleted successfully!')
        return redirect('teachers:teacher_list')
    
    context = {'teacher': teacher}
    return render(request, 'Backend/admin/teacher/teacher_delete.html', context)

@login_required
@admin_required
def teacher_toggle_status(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = not teacher.is_active
    teacher.save()
    
    status = 'activated' if teacher.is_active else 'deactivated'
    messages.success(request, f'Teacher {teacher.get_full_name()} {status} successfully!')
    return redirect('teachers:teacher_list')

@login_required
@admin_required
def teacher_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="teachers_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Teacher ID', 'Full Name', 'Email', 'Phone', 'Gender',
        'Qualification', 'Specialization', 'Hire Date', 'Status'
    ])
    
    teachers = Teacher.objects.all()
    for teacher in teachers:
        writer.writerow([
            teacher.id,
            teacher.teacher_id,
            teacher.get_full_name(),
            teacher.email,
            teacher.phone,
            teacher.get_gender_display(),
            teacher.qualification,
            teacher.specialization,
            teacher.hire_date,
            'Active' if teacher.is_active else 'Inactive'
        ])
    
    return response