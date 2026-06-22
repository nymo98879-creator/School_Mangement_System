from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')  # Changed from 'login'
        if request.user.role != 'admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:dashboard')  # Changed from 'dashboard'
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')  # Changed from 'login'
        if request.user.role != 'teacher':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:dashboard')  # Changed from 'dashboard'
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')  # Changed from 'login'
        if request.user.role != 'student':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:dashboard')  # Changed from 'dashboard'
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')  # Changed from 'login'
        if request.user.role not in ['admin', 'teacher']:
            messages.error(request, 'Only teachers and admins can access this page.')
            return redirect('accounts:dashboard')  # Changed from 'dashboard'
        return view_func(request, *args, **kwargs)
    return wrapper