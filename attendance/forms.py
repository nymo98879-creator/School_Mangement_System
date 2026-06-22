from django import forms
from .models import Attendance
from students.models import Student
from classes.models import Class

class AttendanceForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        class_obj = kwargs.pop('class_obj', None)
        super().__init__(*args, **kwargs)
        
        if class_obj:
            students = Student.objects.filter(class_enrolled=class_obj, is_active=True)
            for student in students:
                self.fields[f'student_{student.id}'] = forms.ChoiceField(
                    choices=Attendance.STATUS_CHOICES,
                    widget=forms.Select(attrs={
                        'class': 'form-select student-status',
                        'data-student-id': student.id
                    }),
                    initial='present',
                    label=f"{student.get_full_name()} ({student.student_id})"
                )

class AttendanceFilterForm(forms.Form):
    class_obj = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Class',
        empty_label='All Classes'
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
            'placeholder': 'Search student...'
        }),
        label='Student'
    )