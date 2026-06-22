from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from accounts.decorators import admin_required
from .models import Faculty, Department, Major, Course
from .forms import (
    FacultyForm, DepartmentForm, MajorForm, CourseForm,
    FacultySearchForm, DepartmentSearchForm, MajorSearchForm, CourseSearchForm
)
import csv
from datetime import datetime

# ==================== FACULTY VIEWS ====================

@login_required
@admin_required
def faculty_list(request):
    faculties = Faculty.objects.all()
    form = FacultySearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        
        if search:
            faculties = faculties.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        if status:
            faculties = faculties.filter(is_active=(status == 'active'))
    
    paginator = Paginator(faculties, 10)
    page = request.GET.get('page')
    faculties_page = paginator.get_page(page)
    
    context = {
        'faculties': faculties_page,
        'form': form,
        'total': Faculty.objects.count(),
        'active': Faculty.objects.filter(is_active=True).count(),
        'inactive': Faculty.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/faculty/faculty_list.html', context)

@login_required
@admin_required
def faculty_add(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'✅ Faculty {faculty.name} added successfully!')
            return redirect('courses:faculty_list')
    else:
        form = FacultyForm()
    
    return render(request, 'Backend/admin/faculty/faculty_form.html', {'form': form, 'title': 'Add Faculty'})

@login_required
@admin_required
def faculty_edit(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'✅ Faculty {faculty.name} updated successfully!')
            return redirect('courses:faculty_list')
    else:
        form = FacultyForm(instance=faculty)
    
    return render(request, 'Backend/admin/faculty/faculty_form.html', {'form': form, 'faculty': faculty, 'title': 'Edit Faculty', 'is_edit': True})

@login_required
@admin_required
def faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        name = faculty.name
        faculty.delete()
        messages.success(request, f'🗑️ Faculty {name} deleted successfully!')
        return redirect('courses:faculty_list')
    return render(request, 'Backend/admin/faculty/faculty_delete.html', {'faculty': faculty})

@login_required
@admin_required
def faculty_toggle_status(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty.is_active = not faculty.is_active
    faculty.save()
    status = 'activated' if faculty.is_active else 'deactivated'
    messages.success(request, f'Faculty {faculty.name} {status}!')
    return redirect('courses:faculty_list')


# ==================== DEPARTMENT VIEWS ====================

@login_required
@admin_required
def department_list(request):
    departments = Department.objects.all()
    form = DepartmentSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        faculty = form.cleaned_data.get('faculty')
        status = form.cleaned_data.get('status')
        
        if search:
            departments = departments.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        if faculty:
            departments = departments.filter(faculty=faculty)
        if status:
            departments = departments.filter(is_active=(status == 'active'))
    
    paginator = Paginator(departments, 10)
    page = request.GET.get('page')
    departments_page = paginator.get_page(page)
    
    context = {
        'departments': departments_page,
        'form': form,
        'total': Department.objects.count(),
        'active': Department.objects.filter(is_active=True).count(),
        'inactive': Department.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/department/department_list.html', context)

@login_required
@admin_required
def department_add(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'✅ Department {department.name} added successfully!')
            return redirect('courses:department_list')
    else:
        form = DepartmentForm()
    
    return render(request, 'Backend/admin/department/department_form.html', {'form': form, 'title': 'Add Department'})

@login_required
@admin_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'✅ Department {department.name} updated successfully!')
            return redirect('courses:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'Backend/admin/department/department_form.html', {'form': form, 'department': department, 'title': 'Edit Department', 'is_edit': True})

@login_required
@admin_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f'🗑️ Department {name} deleted successfully!')
        return redirect('courses:department_list')
    return render(request, 'Backend/admin/department/department_delete.html', {'department': department})

@login_required
@admin_required
def department_toggle_status(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.is_active = not department.is_active
    department.save()
    status = 'activated' if department.is_active else 'deactivated'
    messages.success(request, f'Department {department.name} {status}!')
    return redirect('courses:department_list')


# ==================== MAJOR VIEWS ====================

@login_required
@admin_required
def major_list(request):
    majors = Major.objects.all()
    form = MajorSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        department = form.cleaned_data.get('department')
        degree_type = form.cleaned_data.get('degree_type')
        status = form.cleaned_data.get('status')
        
        if search:
            majors = majors.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        if department:
            majors = majors.filter(department=department)
        if degree_type:
            majors = majors.filter(degree_type=degree_type)
        if status:
            majors = majors.filter(is_active=(status == 'active'))
    
    paginator = Paginator(majors, 10)
    page = request.GET.get('page')
    majors_page = paginator.get_page(page)
    
    context = {
        'majors': majors_page,
        'form': form,
        'total': Major.objects.count(),
        'active': Major.objects.filter(is_active=True).count(),
        'inactive': Major.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/major/major_list.html', context)

@login_required
@admin_required
def major_add(request):
    if request.method == 'POST':
        form = MajorForm(request.POST)
        if form.is_valid():
            major = form.save()
            messages.success(request, f'✅ Major {major.name} added successfully!')
            return redirect('courses:major_list')
    else:
        form = MajorForm()
    
    return render(request, 'Backend/admin/major/major_form.html', {'form': form, 'title': 'Add Major'})

@login_required
@admin_required
def major_edit(request, pk):
    major = get_object_or_404(Major, pk=pk)
    if request.method == 'POST':
        form = MajorForm(request.POST, instance=major)
        if form.is_valid():
            major = form.save()
            messages.success(request, f'✅ Major {major.name} updated successfully!')
            return redirect('courses:major_list')
    else:
        form = MajorForm(instance=major)
    
    return render(request, 'Backend/admin/major/major_form.html', {'form': form, 'major': major, 'title': 'Edit Major', 'is_edit': True})

@login_required
@admin_required
def major_delete(request, pk):
    major = get_object_or_404(Major, pk=pk)
    if request.method == 'POST':
        name = major.name
        major.delete()
        messages.success(request, f'🗑️ Major {name} deleted successfully!')
        return redirect('courses:major_list')
    return render(request, 'Backend/admin/major/major_delete.html', {'major': major})

@login_required
@admin_required
def major_toggle_status(request, pk):
    major = get_object_or_404(Major, pk=pk)
    major.is_active = not major.is_active
    major.save()
    status = 'activated' if major.is_active else 'deactivated'
    messages.success(request, f'Major {major.name} {status}!')
    return redirect('courses:major_list')


# ==================== COURSE VIEWS ====================

@login_required
@admin_required
def course_list(request):
    courses = Course.objects.all()
    form = CourseSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        major = form.cleaned_data.get('major')
        level = form.cleaned_data.get('level')
        status = form.cleaned_data.get('status')
        min_credits = form.cleaned_data.get('min_credits')
        max_credits = form.cleaned_data.get('max_credits')
        
        if search:
            courses = courses.filter(
                Q(name__icontains=search) | 
                Q(code__icontains=search) | 
                Q(course_id__icontains=search)
            )
        if major:
            courses = courses.filter(major=major)
        if level:
            courses = courses.filter(level=level)
        if status:
            courses = courses.filter(is_active=(status == 'active'))
        if min_credits:
            courses = courses.filter(credits__gte=min_credits)
        if max_credits:
            courses = courses.filter(credits__lte=max_credits)
    
    # Get counts BEFORE pagination
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(is_active=True).count()
    inactive_courses = Course.objects.filter(is_active=False).count()
    
    paginator = Paginator(courses, 10)
    page = request.GET.get('page')
    courses_page = paginator.get_page(page)
    
    context = {
        'courses': courses_page,
        'form': form,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'inactive_courses': inactive_courses,
    }
    return render(request, 'Backend/admin/course/course_list.html', context)

@login_required
@admin_required
def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'✅ Course {course.code} - {course.name} added successfully!')
            return redirect('courses:course_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
    
    context = {
        'form': form,
        'title': 'Add New Course',
        'is_edit': False,
    }
    return render(request, 'Backend/admin/course/course_form.html', context)

@login_required
@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'✅ Course {course.code} - {course.name} updated successfully!')
            return redirect('courses:course_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'title': 'Edit Course',
        'course': course,
        'is_edit': True,
    }
    return render(request, 'Backend/admin/course/course_form.html', context)

@login_required
@admin_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    student_count = course.students.count() if hasattr(course, 'students') else 0
    
    context = {
        'course': course,
        'student_count': student_count,
        'prerequisites': course.prerequisites.all(),
    }
    return render(request, 'Backend/admin/course/course_detail.html', context)

@login_required
@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        name = course.name
        course.delete()
        messages.success(request, f'🗑️ Course {name} deleted successfully!')
        return redirect('courses:course_list')
    
    context = {
        'course': course,
    }
    return render(request, 'Backend/admin/course/course_delete.html', context)

@login_required
@admin_required
def course_toggle_status(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.is_active = not course.is_active
    course.save()
    
    status = 'activated' if course.is_active else 'deactivated'
    messages.success(request, f'Course {course.name} {status} successfully!')
    return redirect('courses:course_list')

@login_required
@admin_required
def course_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="courses_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Course ID', 'Code', 'Name', 'Description', 
        'Credits', 'Level', 'Duration', 'Fee', 'Major', 'Teacher', 'Status', 'Created At'
    ])
    
    for course in Course.objects.all():
        writer.writerow([
            course.id,
            course.course_id,
            course.code,
            course.name,
            course.description,
            course.credits,
            course.get_level_display(),
            course.duration,
            course.fee,
            course.major.name if course.major else '',
            course.teacher.get_full_name() if course.teacher else '',
            'Active' if course.is_active else 'Inactive',
            course.created_at.strftime('%Y-%m-%d %H:%M') if course.created_at else ''
        ])
    
    return response