from django import forms
from .models import Attendance
from students.models import Student
from courses.models import Course
from datetime import date


class AttendanceForm(forms.Form):
    """
    Dynamic form for taking attendance for a course.
    Generates a field for each student enrolled in the course.
    """
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        initial=date.today
    )
    
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        existing_attendance = kwargs.pop('existing_attendance', {})
        super().__init__(*args, **kwargs)
        
        if course:
            # Get students enrolled in this course
            from django.db.models import Q
            from classes.models import Class
            course_year = course.level[0] if course.level and len(course.level) > 0 else None
            if course_year:
                students = Student.objects.filter(
                    Q(courses__id=course.id) | Q(classes_enrolled__course=course),
                    year=course_year,
                    is_active=True
                ).distinct()
            else:
                students = Student.objects.filter(
                    Q(courses__id=course.id) | Q(classes_enrolled__course=course),
                    is_active=True
                ).distinct()
            
            for student in students:
                # Status field
                default_status = 'present'
                if str(student.id) in existing_attendance:
                    default_status = existing_attendance[str(student.id)].get('status', 'present')
                
                self.fields[f'student_{student.id}'] = forms.ChoiceField(
                    choices=Attendance.STATUS_CHOICES,
                    widget=forms.Select(attrs={
                        'class': 'form-select student-status',
                        'data-student-id': student.id
                    }),
                    initial=default_status,
                    label=f"{student.get_full_name()} ({student.student_id})"
                )
                
                # Remark field
                default_remark = ''
                if str(student.id) in existing_attendance:
                    default_remark = existing_attendance[str(student.id)].get('remarks', '')
                
                self.fields[f'remark_{student.id}'] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control remark-input',
                        'placeholder': 'Add remark...',
                        'data-student-id': student.id
                    }),
                    initial=default_remark,
                    label=''
                )
                
                # Time In field
                default_time_in = ''
                if str(student.id) in existing_attendance:
                    default_time_in = existing_attendance[str(student.id)].get('time_in', '')
                
                self.fields[f'time_in_{student.id}'] = forms.TimeField(
                    required=False,
                    widget=forms.TimeInput(attrs={
                        'class': 'form-control time-input',
                        'type': 'time',
                        'data-student-id': student.id
                    }),
                    initial=default_time_in,
                    label=''
                )


class AttendanceFilterForm(forms.Form):
    """
    Form for filtering attendance records.
    """
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Course',
        empty_label='All Courses'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date From'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date To'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Attendance.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Status'
    )
    
    student = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search student by name or ID...'
        }),
        label='Student'
    )