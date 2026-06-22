from django import forms
from django.core.exceptions import ValidationError
from .models import Teacher

class TeacherForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Email Address'
        }),
        required=True,
        label="Confirm Email"
    )
    
    class Meta:
        model = Teacher
        fields = [
            'teacher_id', 'first_name', 'last_name', 'date_of_birth',
            'gender', 'phone', 'email', 'address', 'qualification',
            'specialization', 'position', 'years_of_experience', 'hired_date',
            'is_active', 'profile_picture'
        ]
        widgets = {
            'teacher_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., TCH-2024-001'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'teacher@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete address'
            }),
            'qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Ph.D. Computer Science'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Artificial Intelligence'
            }),
            'position': forms.Select(attrs={
                'class': 'form-control'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 5',
                'min': 0
            }),
            'hired_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'teacher_id': 'Teacher ID',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'address': 'Address',
            'qualification': 'Qualification',
            'specialization': 'Specialization',
            'position': 'Position/Rank',
            'years_of_experience': 'Years of Experience',
            'hired_date': 'Hired Date',
            'is_active': 'Active Status',
            'profile_picture': 'Profile Picture',
        }
        help_texts = {
            'position': 'Select the current position/rank of the teacher. Note: Only teachers with "Dean" position can be assigned as Dean of a Faculty.',
            'years_of_experience': 'Total years of teaching experience',
            'qualification': 'Highest academic qualification (e.g., Ph.D., M.Sc.)',
            'specialization': 'Area of specialization/expertise',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make fields required
        self.fields['teacher_id'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['date_of_birth'].required = True
        self.fields['gender'].required = True
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['qualification'].required = True
        self.fields['specialization'].required = True
        self.fields['position'].required = True
        
        # Add empty label for position
        self.fields['position'].empty_label = '--------- Select Position ---------'
        
        # Set field order
        self.order_fields([
            'teacher_id', 'first_name', 'last_name', 'date_of_birth',
            'gender', 'phone', 'email', 'confirm_email', 'address',
            'qualification', 'specialization', 'position',
            'years_of_experience', 'hired_date', 'is_active', 'profile_picture'
        ])
    
    # teachers/forms.py - Updated clean method

def clean(self):
    cleaned_data = super().clean()
    email = cleaned_data.get('email')
    confirm_email = cleaned_data.get('confirm_email')
    position = cleaned_data.get('position')
    qualification = cleaned_data.get('qualification')
    
    # Validate email match
    if email and confirm_email and email != confirm_email:
        self.add_error('confirm_email', 'Email addresses do not match.')
    
    # ===== VALIDATE DEAN REQUIRES Ph.D. =====
    if position == 'dean':
        # Check if qualification contains Ph.D. (case insensitive)
        has_phd = False
        if qualification:
            has_phd = 'ph.d.' in qualification.lower() or 'phd' in qualification.lower()
        
        if not has_phd:
            self.add_error(
                'position', 
                'Dean position requires a Ph.D. qualification. '
                'Please add "Ph.D." or "PhD" to your qualification field.'
            )
    
    return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Teacher.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError('Email already registered to another teacher.')
        return email
    
    def clean_years_of_experience(self):
        years = self.cleaned_data.get('years_of_experience')
        if years and years < 0:
            raise ValidationError('Years of experience cannot be negative.')
        if years and years > 50:
            raise ValidationError('Years of experience cannot exceed 50.')
        return years
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        position = cleaned_data.get('position')
        qualification = cleaned_data.get('qualification')
        
        # Validate email match
        if email and confirm_email and email != confirm_email:
            self.add_error('confirm_email', 'Email addresses do not match.')
        
        # ===== VALIDATE DEAN REQUIRES Ph.D. =====
        if position == 'dean':
            # Check if qualification contains Ph.D.
            has_phd = False
            if qualification:
                has_phd = 'Ph.D.' in qualification or 'PhD' in qualification
            
            if not has_phd:
                self.add_error(
                    'position', 
                    'Dean position requires a Ph.D. qualification. Please update your qualification to include "Ph.D." or "PhD".'
                )
                self.add_error(
                    'qualification',
                    'Dean position requires a Ph.D. qualification. Please enter "Ph.D." in your qualification.'
                )
        
        return cleaned_data


class TeacherSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ID, or email...'
        })
    )
    gender_filter = forms.ChoiceField(
        choices=[('', 'All Genders')] + list(Teacher.GENDER_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    position_filter = forms.ChoiceField(
        choices=[('', 'All Positions')] + list(Teacher.POSITION_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    status_filter = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class TeacherBulkUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload Excel file with teacher data. Required columns: teacher_id, first_name, last_name, email, phone, date_of_birth, gender, qualification, specialization, position',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        })
    )
    send_welcome_email = forms.BooleanField(
        required=False,
        label='Send welcome email to teachers',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )