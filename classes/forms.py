from django import forms
from .models import Building, Floor, Room, Term, TimeSlot, Class
from teachers.models import Teacher
from courses.models import Course
from .schedule_conflicts import (
    build_slot_entries,
    find_course_schedule_conflict,
    find_teacher_schedule_conflict,
    normalize_academic_year,
)


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'code', 'address', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BuildingSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search buildings...'}))
    status = forms.ChoiceField(required=False, choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')], widget=forms.Select(attrs={'class': 'form-select'}))


class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['building', 'floor_number', 'name', 'description', 'is_active']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-select'}),
            'floor_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FloorSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search floors...'}))
    building = forms.ModelChoiceField(required=False, queryset=Building.objects.filter(is_active=True), widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(required=False, choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')], widget=forms.Select(attrs={'class': 'form-select'}))


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['building', 'floor', 'room_number', 'name', 'room_type', 'capacity', 'description', 'is_active']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-select'}),
            'floor': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoomSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search rooms...'}))
    building = forms.ModelChoiceField(required=False, queryset=Building.objects.filter(is_active=True), widget=forms.Select(attrs={'class': 'form-select'}))
    room_type = forms.ChoiceField(required=False, choices=[('', 'All')] + Room.ROOM_TYPES, widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(required=False, choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')], widget=forms.Select(attrs={'class': 'form-select'}))

class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['name', 'term_type', 'academic_year', 'start_date', 'end_date', 'is_active', 'is_current', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Semester 1, Semester 2'
            }),
            'term_type': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={  # Changed from NumberInput to TextInput
                'class': 'form-control',
                'placeholder': 'e.g., 2024-2025'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Term description'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set term_type choices with readable labels
        self.fields['term_type'].choices = [
            ('semester1', 'Semester 1 (6 months)'),
            ('semester2', 'Semester 2 (6 months)'),
        ]
        # Force academic_year to be a text input
        self.fields['academic_year'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2024-2025'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('Start date must be before end date.')
            
            from datetime import timedelta
            duration = end_date - start_date
            if duration.days < 150 or duration.days > 210:
                raise forms.ValidationError(
                    f'Term duration should be approximately 6 months (150-210 days). Current duration: {duration.days} days.'
                )
        
        return cleaned_data
    
    
class TimeSlotForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=TimeSlot.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'day-checkbox'}),
        required=True,
        error_messages={
            'required': 'Please select at least one day.'
        }
    )
    
    class Meta:
        model = TimeSlot
        fields = ['days', 'start_time', 'end_time', 'slot_type', 'name', 'description', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'slot_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_days(self):
        days = self.cleaned_data.get('days')
        if not days:
            raise forms.ValidationError('Please select at least one day.')
        return days
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('Start time must be before end time.')
        
        return cleaned_data

# class ClassForm(forms.ModelForm):
#     class Meta:
#         model = Class
#         fields = [
#             'name', 'section', 'code',
#             'building', 'floor', 'room', 'room_number',
#             'time_slots',
#             'start_time', 'end_time', 'days', 'schedule',
#             'term', 'academic_year',
#             'start_date', 'end_date',
#             'capacity',
#             'teacher', 'course',
#             'is_active'
#         ]
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Enter class name',
#                 'required': True
#             }),
#             'section': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., A, B, C'
#             }),
#             'code': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., MATH101-A'
#             }),
#             'building': forms.Select(attrs={
#                 'class': 'form-select select2',
#                 'data-placeholder': 'Select Building'
#             }),
#             'floor': forms.Select(attrs={
#                 'class': 'form-select select2',
#                 'data-placeholder': 'Select Floor'
#             }),
#             'room': forms.Select(attrs={
#                 'class': 'form-select select2',
#                 'data-placeholder': 'Select Room'
#             }),
#             'room_number': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., 101'
#             }),
#             'time_slots': forms.SelectMultiple(attrs={
#                 'class': 'form-select select2-multiple',
#                 'data-placeholder': 'Select time slots'
#             }),
#             'start_time': forms.TimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'time'
#             }),
#             'end_time': forms.TimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'time'
#             }),
#             'days': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., Monday, Wednesday, Friday'
#             }),
#             'schedule': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., MWF 10:00-11:30'
#             }),
#             'term': forms.Select(attrs={
#                 'class': 'form-select select2',
#                 'data-placeholder': 'Select Term'
#             }),
#             'academic_year': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., 2024-2025'
#             }),
#             'start_date': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date'
#             }),
#             'end_date': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date'
#             }),
#             'capacity': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'min': 1,
#                 'max': 100,
#                 'placeholder': '30',
#                 'required': True
#             }),
#             'teacher': forms.Select(attrs={
#                 'class': 'form-select select2',
#                 'data-placeholder': 'Select Teacher',
#                 'required': True
#             }),
#             'course': forms.Select(attrs={
#                 'class': 'form-select select2',
#                 'data-placeholder': 'Select Course'
#             }),
#             'is_active': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input',
#                 'role': 'switch',
#                 'checked': True
#             }),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Set empty labels for foreign key fields
#         self.fields['building'].empty_label = 'Select Building'
#         self.fields['floor'].empty_label = 'Select Floor'
#         self.fields['room'].empty_label = 'Select Room'
#         self.fields['term'].empty_label = 'Select Term'
#         self.fields['teacher'].empty_label = 'Select Teacher'
#         self.fields['course'].empty_label = 'Select Course'
        
#         # Mark required fields
#         self.fields['name'].required = True
#         self.fields['teacher'].required = True
#         self.fields['capacity'].required = True
        
#         # Add help texts
#         self.fields['time_slots'].help_text = "Hold Ctrl/Cmd to select multiple"
#         self.fields['capacity'].help_text = "Maximum students (1-100)"
    
#     def clean_capacity(self):
#         capacity = self.cleaned_data.get('capacity')
#         if capacity and (capacity < 1 or capacity > 100):
#             raise forms.ValidationError("Capacity must be between 1 and 100")
#         return capacity
    
#     def clean(self):
#         cleaned_data = super().clean()
#         start_date = cleaned_data.get('start_date')
#         end_date = cleaned_data.get('end_date')
        
#         if start_date and end_date and start_date > end_date:
#             raise forms.ValidationError('Start date must be before end date.')
            
#         time_slots = cleaned_data.get('time_slots')
        
#         # Auto-populate direct timing fields from ManyToMany time_slots if provided
#         if time_slots:
#             all_days = []
#             earliest_start = None
#             latest_end = None
#             for slot in time_slots:
#                 # Slot days
#                 days_list = [d.strip() for d in slot.days.split(',') if d.strip()]
#                 for d in days_list:
#                     if d not in all_days:
#                         all_days.append(d)
#                 # Slot times
#                 if earliest_start is None or slot.start_time < earliest_start:
#                     earliest_start = slot.start_time
#                 if latest_end is None or slot.end_time > latest_end:
#                     latest_end = slot.end_time
            
#             # Capitalize days for database format (e.g. Monday, Wednesday)
#             capitalized_days = [d.capitalize() for d in all_days]
            
#             if all_days:
#                 cleaned_data['days'] = ', '.join(capitalized_days)
#             if earliest_start:
#                 cleaned_data['start_time'] = earliest_start
#             if latest_end:
#                 cleaned_data['end_time'] = latest_end
            
#             # Format display string for schedule field
#             schedule_str = ", ".join([str(slot) for slot in time_slots])
#             cleaned_data['schedule'] = schedule_str

#         # Check course time slot overlap conflicts (within the same academic year)
#         course = cleaned_data.get('course')
#         term = cleaned_data.get('term')
#         academic_year = normalize_academic_year(cleaned_data.get('academic_year'), term)
#         cleaned_data['academic_year'] = academic_year

#         current_slots = build_slot_entries(
#             time_slots=time_slots,
#             start_time=cleaned_data.get('start_time'),
#             end_time=cleaned_data.get('end_time'),
#             days=cleaned_data.get('days'),
#         )

#         if course and current_slots and not academic_year:
#             raise forms.ValidationError(
#                 'Academic year is required when assigning a course to a class schedule.'
#             )

#         if course:
#             conflict = find_course_schedule_conflict(
#                 course=course,
#                 academic_year=academic_year,
#                 slot_entries=current_slots,
#                 exclude_pk=self.instance.pk if self.instance and self.instance.pk else None,
#             )
#             if conflict:
#                 other, schedule = conflict
#                 raise forms.ValidationError(
#                     f"Conflict: Course '{course.name}' is already assigned to class "
#                     f"'{other.name}' ({academic_year}) at an overlapping schedule: {schedule}. "
#                     f"Use a different time slot or a different academic year."
#                 )

#         # Teacher schedule conflict: a teacher cannot teach two active classes
#         # in the same academic year with overlapping time slots.
#         teacher = cleaned_data.get('teacher')
#         teacher_conflict = find_teacher_schedule_conflict(
#             teacher=teacher,
#             academic_year=academic_year,
#             slot_entries=current_slots,
#             exclude_pk=self.instance.pk if self.instance and self.instance.pk else None,
#         )
#         if teacher_conflict:
#             other, schedule = teacher_conflict
#             raise forms.ValidationError(
#                 f"Conflict: Teacher '{teacher.get_full_name()}' is already assigned to class "
#                 f"'{other.name}' ({academic_year}) at an overlapping schedule: {schedule}. "
#                 f"A teacher cannot teach two classes at the same time in the same academic year."
#             )

#         return cleaned_data

from django import forms
from .models import Class, Building, Floor, Room, Term, TimeSlot
from courses.models import Course
from teachers.models import Teacher

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = [
            'name', 'section', 'code',
            'building', 'floor', 'room',
            'time_slots', 'schedule',
            'term', 'academic_year',
            'capacity', 'teacher', 'courses',  # ADDED courses field
            'is_active', 'start_date', 'end_date',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'building': forms.Select(attrs={'class': 'form-control cascade-select'}),
            'floor': forms.Select(attrs={'class': 'form-control cascade-select'}),
            'room': forms.Select(attrs={'class': 'form-control cascade-select'}),
            'time_slots': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 100px;'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2025-2026'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'courses': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 120px;'}),  # ADDED
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'name': 'Class Name',
            'section': 'Section',
            'code': 'Class Code',
            'building': 'Building',
            'floor': 'Floor',
            'room': 'Room',
            'time_slots': 'Time Slots',
            'schedule': 'Schedule',
            'term': 'Term',
            'academic_year': 'Academic Year',
            'capacity': 'Capacity',
            'teacher': 'Teacher',
            'courses': 'Courses',  # ADDED
            'is_active': 'Active Status',
            'start_date': 'Start Date',
            'end_date': 'End Date',
        }
        help_texts = {
            'courses': 'Hold Ctrl/Cmd to select multiple courses for this class',
            'time_slots': 'Hold Ctrl/Cmd to select multiple time slots',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['courses'].queryset = Course.objects.filter(is_active=True)
        self.fields['courses'].required = False
        self.fields['time_slots'].queryset = TimeSlot.objects.filter(is_active=True)
        self.fields['time_slots'].required = False
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True)
        self.fields['teacher'].empty_label = 'Select Teacher'
        self.fields['term'].empty_label = 'Select Term'
        self.fields['building'].empty_label = 'Select Building'
        self.fields['floor'].empty_label = 'Select Floor'
        self.fields['room'].empty_label = 'Select Room'
        self.fields['name'].required = True


class ClassSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control search-input',
            'placeholder': 'Search classes...'
        })
    )
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Teachers'
    )
    building = forms.ModelChoiceField(
        queryset=Building.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Buildings'
    )
    term = forms.ModelChoiceField(
        queryset=Term.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Terms'
    )
    status = forms.ChoiceField(
        choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
