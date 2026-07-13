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
from classes.models import Class
from students.models import Student
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
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(faculties, per_page)
    page = request.GET.get('page')
    faculties_page = paginator.get_page(page)
    
    context = {
        'faculties': faculties_page,
        'per_page': per_page,
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
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(departments, per_page)
    page = request.GET.get('page')
    departments_page = paginator.get_page(page)
    
    context = {
        'departments': departments_page,
        'per_page': per_page,
        'form': form,
        'faculties': Faculty.objects.filter(is_active=True).order_by('name'),
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
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(majors, per_page)
    page = request.GET.get('page')
    majors_page = paginator.get_page(page)
    
    context = {
        'majors': majors_page,
        'per_page': per_page,
        'form': form,
        'departments': Department.objects.filter(is_active=True).order_by('name'),
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
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(courses, per_page)
    page = request.GET.get('page')
    courses_page = paginator.get_page(page)
    
    context = {
        'courses': courses_page,
        'per_page': per_page,
        'form': form,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'inactive_courses': inactive_courses,
        'majors': Major.objects.filter(is_active=True).select_related('department'),
    }
    return render(request, 'Backend/admin/course/course_list.html', context)

def _get_teacher_classes_for_course(course):
    if course.teacher:
        return course.class_offerings.filter(teacher=course.teacher, is_active=True)
    return Class.objects.none()

@login_required
@admin_required
def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            class_ids = request.POST.getlist('classes')
            if class_ids:
                course.class_offerings.set(class_ids)
            messages.success(request, f'✅ Course {course.code} - {course.name} added successfully!')
            return redirect('courses:course_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
    
    all_classes = Class.objects.filter(is_active=True).order_by('name')
    context = {
        'form': form,
        'title': 'Add New Course',
        'is_edit': False,
        'all_classes': all_classes,
        'assigned_class_ids': [],
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
            class_ids = request.POST.getlist('classes')
            course.class_offerings.set(class_ids)
            messages.success(request, f'✅ Course {course.code} - {course.name} updated successfully!')
            return redirect('courses:course_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    
    all_classes = Class.objects.filter(is_active=True).order_by('name')
    assigned_class_ids = [str(cid) for cid in course.class_offerings.values_list('id', flat=True)]
    context = {
        'form': form,
        'title': 'Edit Course',
        'course': course,
        'is_edit': True,
        'all_classes': all_classes,
        'assigned_class_ids': assigned_class_ids,
    }
    return render(request, 'Backend/admin/course/course_form.html', context)

@login_required
@admin_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    students = Student.objects.filter(courses=course, is_active=True).distinct().order_by('first_name', 'last_name')
    prerequisites = course.prerequisites.all()
    teacher_classes = course.class_offerings.filter(is_active=True)

    context = {
        'course': course,
        'students': students,
        'prerequisites': prerequisites,
        'teacher_classes': teacher_classes,
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
def course_add_student(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        if not student_ids:
            messages.warning(request, 'Please select at least one student.')
            return redirect('courses:course_add_student', pk=course.pk)
        
        added_count = 0
        already_enrolled = 0
        
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id, is_active=True)
                if student.courses.filter(id=course.id).exists():
                    already_enrolled += 1
                else:
                    student.courses.add(course)
                    added_count += 1
            except Student.DoesNotExist:
                continue
        
        if added_count > 0:
            messages.success(request, f'{added_count} student(s) added to course "{course.name}" successfully!')
        if already_enrolled > 0:
            messages.warning(request, f'{already_enrolled} student(s) were already enrolled in this course.')
        if added_count == 0 and already_enrolled == 0:
            messages.warning(request, 'No students were added.')
        
        return redirect('courses:course_detail', pk=course.pk)
    
    all_students = Student.objects.filter(is_active=True).order_by('first_name', 'last_name')
    enrolled_student_ids = list(Student.objects.filter(courses=course, is_active=True).values_list('id', flat=True))
    
    context = {
        'course': course,
        'all_students': all_students,
        'enrolled_student_ids': enrolled_student_ids,
    }
    return render(request, 'Backend/admin/course/add_student.html', context)


@login_required
@admin_required
def course_add_student_direct(request, course_pk, student_pk):
    course = get_object_or_404(Course, pk=course_pk)
    student = get_object_or_404(Student, pk=student_pk, is_active=True)
    if not student.courses.filter(pk=course.pk).exists():
        student.courses.add(course)
        messages.success(request, f'{student.get_full_name} added to {course.name}.')
    else:
        messages.info(request, f'{student.get_full_name} is already enrolled in {course.name}.')
    return redirect('courses:course_detail', pk=course.pk)


@login_required
@admin_required
def course_remove_student(request, course_pk, student_pk):
    course = get_object_or_404(Course, pk=course_pk)
    student = get_object_or_404(Student, pk=student_pk)
    if student.courses.filter(pk=course.pk).exists():
        student.courses.remove(course)
        messages.success(request, f'{student.get_full_name} removed from {course.name}.')
    else:
        messages.info(request, f'{student.get_full_name} was not enrolled in {course.name}.')
    return redirect('courses:course_detail', pk=course.pk)


@login_required
@admin_required
def course_student_edit(request, course_pk, student_pk):
    course = get_object_or_404(Course, pk=course_pk)
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == 'POST':
        if student.courses.filter(pk=course.pk).exists():
            student.courses.remove(course)
            messages.success(request, f'{student.get_full_name} removed from {course.name}.')
        else:
            student.courses.add(course)
            messages.success(request, f'{student.get_full_name} added to {course.name}.')
        return redirect('courses:course_detail', pk=course.pk)

    context = {
        'course': course,
        'student': student,
        'enrolled': student.courses.filter(pk=course.pk).exists(),
    }
    return render(request, 'Backend/admin/course/course_student_edit.html', context)


@login_required
@admin_required
def course_student_delete(request, course_pk, student_pk):
    course = get_object_or_404(Course, pk=course_pk)
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == 'POST':
        if student.courses.filter(pk=course.pk).exists():
            student.courses.remove(course)
            messages.success(request, f'{student.get_full_name} removed from {course.name}.')
        else:
            messages.info(request, f'{student.get_full_name} was not enrolled in {course.name}.')
        return redirect('courses:course_detail', pk=course.pk)

    context = {
        'course': course,
        'student': student,
    }
    return render(request, 'Backend/admin/course/course_student_delete.html', context)


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