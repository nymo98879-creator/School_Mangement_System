# from django import forms
# from django.core.exceptions import ValidationError
# from django.db.models import Q
# from .models import Building, Floor, Room, Term, TimeSlot, Class
# from teachers.models import Teacher
# from courses.models import Course


# # ===== BUILDING FORMS =====
# class BuildingForm(forms.ModelForm):
#     class Meta:
#         model = Building
#         fields = ['name', 'code', 'address', 'description', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building Name'}),
#             'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building Code'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
#         }


# class BuildingSearchForm(forms.Form):
#     search = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or code...'})
#     )
#     status = forms.ChoiceField(
#         choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )


# # ===== FLOOR FORMS =====
# class FloorForm(forms.ModelForm):
#     class Meta:
#         model = Floor
#         fields = ['building', 'floor_number', 'name', 'description', 'is_active']
#         widgets = {
#             'building': forms.Select(attrs={'class': 'form-control select2'}),
#             'floor_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1, 2, 3, B1'}),
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Floor Name'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
#         }


# class FloorSearchForm(forms.Form):
#     search = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by floor number...'})
#     )
#     building = forms.ModelChoiceField(
#         queryset=Building.objects.filter(is_active=True),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         empty_label='All Buildings'
#     )
#     status = forms.ChoiceField(
#         choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )


# # ===== ROOM FORMS =====
# class RoomForm(forms.ModelForm):
#     class Meta:
#         model = Room
#         fields = ['building', 'floor', 'room_number', 'name', 'room_type', 'capacity', 'description', 'is_active']
#         widgets = {
#             'building': forms.Select(attrs={'class': 'form-control select2'}),
#             'floor': forms.Select(attrs={'class': 'form-control select2'}),
#             'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 101, A203'}),
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room Name'}),
#             'room_type': forms.Select(attrs={'class': 'form-control'}),
#             'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 200}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['floor'].queryset = Floor.objects.filter(is_active=True)
#         self.fields['floor'].empty_label = 'Select Floor'


# class RoomSearchForm(forms.Form):
#     search = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by room number...'})
#     )
#     building = forms.ModelChoiceField(
#         queryset=Building.objects.filter(is_active=True),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         empty_label='All Buildings'
#     )
#     room_type = forms.ChoiceField(
#         choices=[('', 'All Types')] + Room.ROOM_TYPES,
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     status = forms.ChoiceField(
#         choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )


# # ===== TERM FORMS =====
# class TermForm(forms.ModelForm):
#     class Meta:
#         model = Term
#         fields = ['name', 'term_type', 'academic_year', 'start_date', 'end_date', 'is_active', 'is_current', 'description']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Term Name'}),
#             'term_type': forms.Select(attrs={'class': 'form-control'}),
#             'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024-2025'}),
#             'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
#             'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
#         }
    
#     def clean(self):
#         cleaned_data = super().clean()
#         start_date = cleaned_data.get('start_date')
#         end_date = cleaned_data.get('end_date')
        
#         if start_date and end_date and start_date > end_date:
#             self.add_error('end_date', 'End date must be after start date.')
        
#         return cleaned_data


# # ===== TIME SLOT FORMS =====
# class TimeSlotForm(forms.ModelForm):
#     days = forms.MultipleChoiceField(
#         choices=TimeSlot.DAYS_OF_WEEK,
#         widget=forms.CheckboxSelectMultiple(attrs={'class': 'day-checkbox-group'}),
#         required=True,
#         error_messages={'required': 'Please select at least one day.'}
#     )
    
#     slot_type = forms.ChoiceField(
#         choices=TimeSlot.SLOT_TYPES,
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_slot_type'})
#     )
    
#     class Meta:
#         model = TimeSlot
#         fields = ['days', 'slot_type', 'start_time', 'end_time', 'name', 'description', 'is_active']
#         widgets = {
#             'start_time': forms.TimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'time',
#                 'id': 'id_start_time'
#             }),
#             'end_time': forms.TimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'time',
#                 'id': 'id_end_time'
#             }),
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., Morning Session'
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': 'Optional description'
#             }),
#             'is_active': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input',
#                 'role': 'switch'
#             }),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['start_time'].required = True
#         self.fields['end_time'].required = True
        
#         if self.instance and self.instance.pk:
#             initial_days = self.instance.get_days_list()
#             self.fields['days'].initial = initial_days
    
#     def clean(self):
#         cleaned_data = super().clean()
#         start_time = cleaned_data.get('start_time')
#         end_time = cleaned_data.get('end_time')
#         days = cleaned_data.get('days')
        
#         if not days:
#             self.add_error('days', 'Please select at least one day.')
        
#         if start_time and end_time and start_time >= end_time:
#             self.add_error('end_time', 'End time must be after start time.')
        
#         return cleaned_data


# # ===== CLASS FORMS =====
# class ClassForm(forms.ModelForm):
#     building = forms.ModelChoiceField(
#         queryset=Building.objects.filter(is_active=True),
#         required=False,
#         empty_label="Select Building",
#         widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_building'})
#     )
    
#     # FIX: Set to all active floors by default
#     floor = forms.ModelChoiceField(
#         queryset=Floor.objects.filter(is_active=True),  # Changed from .none()
#         required=False,
#         empty_label="Select Floor",
#         widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_floor'})
#     )
    
#     # FIX: Set to all active rooms by default
#     room = forms.ModelChoiceField(
#         queryset=Room.objects.filter(is_active=True),  # Changed from .none()
#         required=False,
#         empty_label="Select Room",
#         widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_room'})
#     )
    
#     term = forms.ModelChoiceField(
#         queryset=Term.objects.filter(is_active=True),
#         required=False,
#         empty_label="Select Term",
#         widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_term'})
#     )
    
#     time_slots = forms.ModelMultipleChoiceField(
#         queryset=TimeSlot.objects.filter(is_active=True),
#         required=False,
#         widget=forms.SelectMultiple(attrs={'class': 'form-control select2-multiple', 'id': 'id_time_slots'})
#     )
    
#     teacher = forms.ModelChoiceField(
#         queryset=Teacher.objects.filter(is_active=True),
#         required=True,
#         empty_label="Select Teacher",
#         widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_teacher'})
#     )
    
#     course = forms.ModelChoiceField(
#         queryset=Course.objects.filter(is_active=True),
#         required=False,
#         empty_label="Select Course",
#         widget=forms.Select(attrs={'class': 'form-control select2'})
#     )
    
#     class Meta:
#         model = Class
#         fields = [
#             'name', 'section', 'code',
#             'building', 'floor', 'room',
#             'time_slots',
#             'start_time', 'end_time',
#             'term', 'academic_year',
#             'capacity',
#             'teacher', 'course',
#             'start_date', 'end_date',
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
#                 'placeholder': 'e.g., A, B'
#             }),
#             'code': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., CS101'
#             }),
#             'start_time': forms.TimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'time'
#             }),
#             'end_time': forms.TimeInput(attrs={
#                 'class': 'form-control',
#                 'type': 'time'
#             }),
#             'academic_year': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'e.g., 2024-2025'
#             }),
#             'capacity': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': '30',
#                 'min': 1,
#                 'max': 100,
#                 'required': True
#             }),
#             'start_date': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date'
#             }),
#             'end_date': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date'
#             }),
#             'is_active': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input',
#                 'role': 'switch',
#                 'id': 'id_is_active'
#             }),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Set all querysets to show all active records
#         self.fields['building'].queryset = Building.objects.filter(is_active=True)
#         self.fields['floor'].queryset = Floor.objects.filter(is_active=True)
#         self.fields['room'].queryset = Room.objects.filter(is_active=True)
#         self.fields['term'].queryset = Term.objects.filter(is_active=True)
#         self.fields['time_slots'].queryset = TimeSlot.objects.filter(is_active=True)
#         self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True)
#         self.fields['course'].queryset = Course.objects.filter(is_active=True)
        
#         # Make required fields
#         self.fields['name'].required = True
#         self.fields['capacity'].required = True
#         self.fields['teacher'].required = True
        
#         # If editing, filter floors and rooms based on building/floor
#         if self.instance and self.instance.pk:
#             if self.instance.building:
#                 self.fields['building'].initial = self.instance.building
#                 # Filter floors based on the building
#                 self.fields['floor'].queryset = Floor.objects.filter(
#                     building=self.instance.building,
#                     is_active=True
#                 )
                
#                 if self.instance.floor:
#                     self.fields['floor'].initial = self.instance.floor
#                     # Filter rooms based on the floor
#                     self.fields['room'].queryset = Room.objects.filter(
#                         floor=self.instance.floor,
#                         is_active=True
#                     )
                    
#                     if self.instance.room:
#                         self.fields['room'].initial = self.instance.room
    
#     def clean_capacity(self):
#         capacity = self.cleaned_data.get('capacity')
#         if capacity and capacity < 1:
#             raise ValidationError('Capacity must be at least 1.')
#         if capacity and capacity > 100:
#             raise ValidationError('Capacity cannot exceed 100.')
#         return capacity
    
#     def clean(self):
#         cleaned_data = super().clean()
#         building = cleaned_data.get('building')
#         floor = cleaned_data.get('floor')
#         room = cleaned_data.get('room')
#         start_date = cleaned_data.get('start_date')
#         end_date = cleaned_data.get('end_date')
#         start_time = cleaned_data.get('start_time')
#         end_time = cleaned_data.get('end_time')
        
#         if building and floor and floor.building != building:
#             self.add_error('floor', 'Selected floor does not belong to the selected building.')
        
#         if building and room and room.building != building:
#             self.add_error('room', 'Selected room does not belong to the selected building.')
        
#         if floor and room and room.floor != floor:
#             self.add_error('room', 'Selected room does not belong to the selected floor.')
        
#         if start_date and end_date and start_date > end_date:
#             self.add_error('end_date', 'End date must be after start date.')
        
#         if start_time and end_time and start_time >= end_time:
#             self.add_error('end_time', 'End time must be after start time.')
        
#         return cleaned_data


# class ClassSearchForm(forms.Form):
#     search = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name, code, or section...'})
#     )
#     teacher = forms.ModelChoiceField(
#         queryset=Teacher.objects.filter(is_active=True),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         empty_label='All Teachers'
#     )
#     building = forms.ModelChoiceField(
#         queryset=Building.objects.filter(is_active=True),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         empty_label='All Buildings'
#     )
#     term = forms.ModelChoiceField(
#         queryset=Term.objects.filter(is_active=True),
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         empty_label='All Terms'
#     )
#     status = forms.ChoiceField(
#         choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )


from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Building, Floor, Room, Term, TimeSlot, Class
from teachers.models import Teacher
from courses.models import Course


# ===== BUILDING FORMS =====
class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'code', 'address', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Building Code'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }


class BuildingSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or code...'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# ===== FLOOR FORMS =====
class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['building', 'floor_number', 'name', 'description', 'is_active']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-control select2'}),
            'floor_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1, 2, 3, B1'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Floor Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }


class FloorSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by floor number...'})
    )
    building = forms.ModelChoiceField(
        queryset=Building.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Buildings'
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# ===== ROOM FORMS =====
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['building', 'floor', 'room_number', 'name', 'room_type', 'capacity', 'description', 'is_active']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-control select2'}),
            'floor': forms.Select(attrs={'class': 'form-control select2'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 101, A203'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room Name'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 200}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['floor'].queryset = Floor.objects.filter(is_active=True)
        self.fields['floor'].empty_label = 'Select Floor'


class RoomSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by room number...'})
    )
    building = forms.ModelChoiceField(
        queryset=Building.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Buildings'
    )
    room_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Room.ROOM_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# ===== TERM FORMS =====
class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['name', 'term_type', 'academic_year', 'start_date', 'end_date', 'is_active', 'is_current', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Term Name'}),
            'term_type': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024-2025'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', 'End date must be after start date.')
        
        return cleaned_data


# ===== TIME SLOT FORMS =====
class TimeSlotForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=TimeSlot.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'day-checkbox-group'}),
        required=True,
        error_messages={'required': 'Please select at least one day.'}
    )
    
    slot_type = forms.ChoiceField(
        choices=TimeSlot.SLOT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_slot_type'})
    )
    
    class Meta:
        model = TimeSlot
        fields = ['days', 'slot_type', 'start_time', 'end_time', 'name', 'description', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'id_start_time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'id_end_time'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Morning Session'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].required = True
        self.fields['end_time'].required = True
        
        if self.instance and self.instance.pk:
            initial_days = self.instance.get_days_list()
            self.fields['days'].initial = initial_days
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        days = cleaned_data.get('days')
        
        if not days:
            self.add_error('days', 'Please select at least one day.')
        
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'End time must be after start time.')
        
        return cleaned_data


# ===== CLASS FORMS =====
class ClassForm(forms.ModelForm):
    building = forms.ModelChoiceField(
        queryset=Building.objects.filter(is_active=True),
        required=False,
        empty_label="Select Building",
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_building'})
    )
    
    floor = forms.ModelChoiceField(
        queryset=Floor.objects.filter(is_active=True),
        required=False,
        empty_label="Select Floor",
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_floor'})
    )
    
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_active=True),
        required=False,
        empty_label="Select Room",
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_room'})
    )
    
    term = forms.ModelChoiceField(
        queryset=Term.objects.filter(is_active=True),
        required=False,
        empty_label="Select Term",
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_term'})
    )
    
    time_slots = forms.ModelMultipleChoiceField(
        queryset=TimeSlot.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2-multiple', 'id': 'id_time_slots'})
    )
    
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.filter(is_active=True),
        required=True,
        empty_label="Select Teacher",
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'id_teacher'})
    )
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        required=False,
        empty_label="Select Course",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    
    class Meta:
        model = Class
        fields = [
            'name', 'section', 'code',
            'building', 'floor', 'room',
            'time_slots',
            'start_time', 'end_time',
            'term', 'academic_year',
            'capacity',
            'teacher', 'course',
            'start_date', 'end_date',
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
                'placeholder': 'e.g., A, B'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CS101'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2024-2025'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '30',
                'min': 1,
                'max': 100,
                'required': True
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
                'id': 'id_is_active'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set all querysets to show all active records
        self.fields['building'].queryset = Building.objects.filter(is_active=True)
        self.fields['floor'].queryset = Floor.objects.filter(is_active=True)
        self.fields['room'].queryset = Room.objects.filter(is_active=True)
        self.fields['term'].queryset = Term.objects.filter(is_active=True)
        self.fields['time_slots'].queryset = TimeSlot.objects.filter(is_active=True)
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True)
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
        
        # Make required fields
        self.fields['name'].required = True
        self.fields['capacity'].required = True
        self.fields['teacher'].required = True
        
        # If editing, filter floors and rooms based on building/floor
        if self.instance and self.instance.pk:
            if self.instance.building:
                self.fields['building'].initial = self.instance.building
                self.fields['floor'].queryset = Floor.objects.filter(
                    building=self.instance.building,
                    is_active=True
                )
                
                if self.instance.floor:
                    self.fields['floor'].initial = self.instance.floor
                    self.fields['room'].queryset = Room.objects.filter(
                        floor=self.instance.floor,
                        is_active=True
                    )
                    
                    if self.instance.room:
                        self.fields['room'].initial = self.instance.room
    
    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity and capacity < 1:
            raise ValidationError('Capacity must be at least 1.')
        if capacity and capacity > 100:
            raise ValidationError('Capacity cannot exceed 100.')
        return capacity
    
    def clean(self):
        cleaned_data = super().clean()
        building = cleaned_data.get('building')
        floor = cleaned_data.get('floor')
        room = cleaned_data.get('room')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if building and floor and floor.building != building:
            self.add_error('floor', 'Selected floor does not belong to the selected building.')
        
        if building and room and room.building != building:
            self.add_error('room', 'Selected room does not belong to the selected building.')
        
        if floor and room and room.floor != floor:
            self.add_error('room', 'Selected room does not belong to the selected floor.')
        
        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', 'End date must be after start date.')
        
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'End time must be after start time.')
        
        return cleaned_data


class ClassSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name, code, or section...'})
    )
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Teachers'
    )
    building = forms.ModelChoiceField(
        queryset=Building.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Buildings'
    )
    term = forms.ModelChoiceField(
        queryset=Term.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Terms'
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )