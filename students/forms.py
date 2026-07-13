from django import forms
from django.core.exceptions import ValidationError
from .models import Student
from classes.models import Class
from courses.models import Major
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentForm(forms.ModelForm):
    confirm_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Email Address',
            'autocomplete': 'off'
        }),
        required=True,
        label="Confirm Email"
    )
    
    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password'
        }),
        help_text="Minimum 8 characters with at least one number"
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'date_of_birth', 
            'gender', 'phone', 'email', 'address', 'guardian_name', 
            'guardian_phone', 'guardian_email', 'major', 
            'is_active', 'profile_picture'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@example.com', 'autocomplete': 'off'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter complete address'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian full name'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian phone number'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'guardian@example.com'}),
            'class_enrolled': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        from courses.models import Major 
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['date_of_birth'].required = True
        self.fields['gender'].required = True
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['guardian_name'].required = True
        self.fields['guardian_phone'].required = True
        
        if not self.is_edit:
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True
        else:
            self.fields['password'].help_text = "Leave blank to keep current password"
            self.fields['confirm_password'].help_text = "Leave blank to keep current password"
        
        self.fields['major'].label = 'Major'  # Changed
        self.fields['is_active'].label = 'Active Status'
        self.fields['profile_picture'].label = 'Profile Picture'
        self.fields['major'].empty_label = 'Select Major'  # Changed
        self.fields['major'].queryset = Major.objects.filter(is_active=True) 
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError('Email already registered to another student.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 10:
            raise ValidationError('Phone number must be at least 10 digits.')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if email and confirm_email and email != confirm_email:
            self.add_error('confirm_email', 'Email addresses do not match.')
        
        if password or confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', 'Passwords do not match.')
            
            if password and len(password) < 8:
                self.add_error('password', 'Password must be at least 8 characters long.')
        
        return cleaned_data


class StudentBulkUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload Excel file with student data. Required columns: first_name, last_name, email, phone, date_of_birth, gender, guardian_name, guardian_phone',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        })
    )
    class_enrolled = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        label='Default Class',
        help_text='Select a class for all students',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label='Select Class'
    )
    send_welcome_email = forms.BooleanField(
        required=False,
        label='Send welcome email to students',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class StudentSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, ID, or email...'
        })
    )
    major_filter = forms.ModelChoiceField(  # Changed from class_filter
        queryset=Major.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label='All Majors'
    )
    gender_filter = forms.ChoiceField(
        choices=[('', 'All Genders')] + list(Student.GENDER_CHOICES),
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
    has_qr = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('registered', 'QR Registered'),
            ('not_registered', 'QR Not Registered')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


# ===== STUDENT SELF-REGISTRATION FORM =====
class StudentSelfRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label='Confirm Password'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label='Password',
        help_text='Minimum 8 characters with at least one number'
    )
    confirm_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Email'}),
        label='Confirm Email'
    )
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'gender', 'address', 'guardian_name', 'guardian_phone', 
            'guardian_email', 'major', 'profile_picture'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian Name'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guardian Phone'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Guardian Email'}),
            'class_enrolled': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from courses.models import Major  # Import Major model
        self.fields['major'].queryset = Major.objects.filter(is_active=True)
        self.fields['major'].empty_label = 'Select Major'
        self.fields['gender'].choices = [('', 'Select Gender')] + list(Student.GENDER_CHOICES)
        self.fields['gender'].required = True
        self.fields['major'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_confirm_email(self):
        email = self.cleaned_data.get('email')
        confirm_email = self.cleaned_data.get('confirm_email')
        if email and confirm_email and email != confirm_email:
            raise ValidationError('Emails do not match.')
        return confirm_email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 10:
            raise ValidationError('Phone number must be at least 10 digits.')
        return phone
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        
        return cleaned_data
    
