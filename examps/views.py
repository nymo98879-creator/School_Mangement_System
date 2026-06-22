from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import admin_required
from .models import Exam
from .forms import ExamForm

@login_required
@admin_required
def exam_list(request):
    exams = Exam.objects.all()
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        exams = exams.filter(
            Q(name__icontains=search) |
            Q(class_obj__name__icontains=search) |
            Q(course__name__icontains=search)
        )
    
    paginator = Paginator(exams, 10)
    page_number = request.GET.get('page')
    exams_page = paginator.get_page(page_number)
    
    context = {
        'exams': exams_page,
        'total_exams': Exam.objects.count(),
        'active_exams': Exam.objects.filter(is_active=True).count(),
        'inactive_exams': Exam.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/exam/exam_list.html', context)

@login_required
@admin_required
def exam_add(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam {exam.name} added successfully!')
            return redirect('examps:exam_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExamForm()
    
    context = {
        'form': form,
        'title': 'Add New Exam',
        'is_edit': False,
    }
    return render(request, 'Backend/admin/exam/exam_form.html', context)

@login_required
@admin_required
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f'Exam {exam.name} updated successfully!')
            return redirect('examps:exam_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExamForm(instance=exam)
    
    context = {
        'form': form,
        'title': 'Edit Exam',
        'exam': exam,
        'is_edit': True,
    }
    return render(request, 'Backend/admin/exam/exam_form.html', context)

@login_required
@admin_required
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    context = {'exam': exam}
    return render(request, 'Backend/admin/exam/exam_detail.html', context)

@login_required
@admin_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    
    if request.method == 'POST':
        exam_name = exam.name
        exam.delete()
        messages.success(request, f'Exam {exam_name} deleted successfully!')
        return redirect('examps:exam_list')
    
    context = {'exam': exam}
    return render(request, 'Backend/admin/exam/exam_delete.html', context)

@login_required
@admin_required
def exam_toggle_status(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.is_active = not exam.is_active
    exam.save()
    
    status = 'activated' if exam.is_active else 'deactivated'
    messages.success(request, f'Exam {exam.name} {status} successfully!')
    return redirect('examps:exam_list')