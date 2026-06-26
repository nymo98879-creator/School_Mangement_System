from django import forms
from .models import Building, Floor, Room, Term, TimeSlot, Class
from teachers.models import Teacher
from courses.models import Course

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
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'term_type': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024-2025'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Start date must be before end date.')
        return cleaned_data

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['days', 'start_time', 'end_time', 'slot_type', 'name', 'description', 'is_active']
        widgets = {
            'days': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'slot_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = [
            'name', 'section', 'code',
            'building', 'floor', 'room', 'room_number',
            'time_slots',
            'start_time', 'end_time', 'days', 'schedule',
            'term', 'academic_year',
            'start_date', 'end_date',
            'capacity',
            'teacher', 'course',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter class name',
                'required': True
            }),
            'section': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A, B, C'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MATH101-A'
            }),
            'building': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select Building'
            }),
            'floor': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select Floor'
            }),
            'room': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select Room'
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 101'
            }),
            'time_slots': forms.SelectMultiple(attrs={
                'class': 'form-select select2-multiple',
                'data-placeholder': 'Select time slots'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'days': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monday, Wednesday, Friday'
            }),
            'schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MWF 10:00-11:30'
            }),
            'term': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select Term'
            }),
            'academic_year': forms.TextInput(attrs={
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
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'placeholder': '30',
                'required': True
            }),
            'teacher': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select Teacher',
                'required': True
            }),
            'course': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select Course'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'checked': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set empty labels for foreign key fields
        self.fields['building'].empty_label = 'Select Building'
        self.fields['floor'].empty_label = 'Select Floor'
        self.fields['room'].empty_label = 'Select Room'
        self.fields['term'].empty_label = 'Select Term'
        self.fields['teacher'].empty_label = 'Select Teacher'
        self.fields['course'].empty_label = 'Select Course'
        
        # Mark required fields
        self.fields['name'].required = True
        self.fields['teacher'].required = True
        self.fields['capacity'].required = True
        
        # Add help texts
        self.fields['time_slots'].help_text = "Hold Ctrl/Cmd to select multiple"
        self.fields['capacity'].help_text = "Maximum students (1-100)"
    
    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity and (capacity < 1 or capacity > 100):
            raise forms.ValidationError("Capacity must be between 1 and 100")
        return capacity
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Start date must be before end date.')
        return cleaned_data
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