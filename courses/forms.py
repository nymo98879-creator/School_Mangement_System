from django import forms
from .models import Faculty, Department, Major, Course
from teachers.models import Teacher

# ===== FACULTY FORM =====
class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'code', 'description', 'dean', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter faculty name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., SCI'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Faculty description'}),
            'dean': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        labels = {
            'name': 'Faculty Name',
            'code': 'Faculty Code',
            'description': 'Description',
            'dean': 'Dean',
            'is_active': 'Active Status',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dean'].queryset = Teacher.objects.filter(is_active=True, position='dean')
        self.fields['dean'].empty_label = 'Select Dean'
        self.fields['name'].required = True
        self.fields['code'].required = True
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Faculty.objects.filter(code=code).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('A faculty with this code already exists.')
        return code


# ===== DEPARTMENT FORM =====
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'faculty', 'head', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department description'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'head': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        labels = {
            'name': 'Department Name',
            'code': 'Department Code',
            'description': 'Description',
            'faculty': 'Faculty',
            'head': 'Department Head',
            'is_active': 'Active Status',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].queryset = Faculty.objects.filter(is_active=True)
        self.fields['faculty'].empty_label = 'Select Faculty'
        self.fields['head'].queryset = Teacher.objects.filter(is_active=True)
        self.fields['head'].empty_label = 'Select Department Head'
        self.fields['name'].required = True
        self.fields['code'].required = True
        self.fields['faculty'].required = True
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Department.objects.filter(code=code).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('A department with this code already exists.')
        return code


# ===== MAJOR FORM =====
class MajorForm(forms.ModelForm):
    class Meta:
        model = Major
        fields = ['name', 'code', 'degree_type', 'description', 'department', 'duration', 'total_credits', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter major name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., BSCS'}),
            'degree_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Major description'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 4'}),
            'total_credits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        labels = {
            'name': 'Major Name',
            'code': 'Major Code',
            'degree_type': 'Degree Type',
            'description': 'Description',
            'department': 'Department',
            'duration': 'Duration (Years)',
            'total_credits': 'Total Credits Required',
            'is_active': 'Active Status',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['department'].empty_label = 'Select Department'
        self.fields['department'].required = True
        self.fields['name'].required = True
        self.fields['code'].required = True
        self.fields['duration'].required = True
        self.fields['total_credits'].required = True
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Major.objects.filter(code=code).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('A major with this code already exists.')
        return code


# ===== COURSE FORM =====
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'credits', 'level', 'duration', 'fee', 'major', 'teacher', 'prerequisites', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS-101', 'readonly': True}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Course description'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 12 weeks'}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'major': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'prerequisites': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 100px;'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        labels = {
            'code': 'Course Code',
            'name': 'Course Name',
            'description': 'Description',
            'credits': 'Credits',
            'level': 'Level',
            'duration': 'Duration',
            'fee': 'Fee ($)',
            'major': 'Major',
            'teacher': 'Teacher',
            'prerequisites': 'Prerequisites',
            'is_active': 'Active Status',
        }
        help_texts = {
            'code': 'Auto-generated (CS-101, CS-102...)',
            'credits': 'Number of credit hours (1-6)',
            'duration': 'e.g., 12 weeks, 1 semester',
            'fee': 'Course fee in USD',
            'prerequisites': 'Hold Ctrl/Cmd to select multiple prerequisite courses',
            'major': 'Select the major this course belongs to',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['major'].queryset = Major.objects.filter(is_active=True)
        self.fields['major'].empty_label = 'Select Major'
        self.fields['teacher'].queryset = Teacher.objects.filter(is_active=True)
        self.fields['teacher'].empty_label = 'Select Teacher'
        self.fields['prerequisites'].queryset = Course.objects.filter(is_active=True)
        self.fields['prerequisites'].required = False
        
        # Make fields required
        self.fields['code'].required = True
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['credits'].required = True
        self.fields['duration'].required = True
        
        # Make code readonly
        if 'readonly' in self.fields['code'].widget.attrs:
            self.fields['code'].widget.attrs['readonly'] = True
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            return code
        if Course.objects.filter(code=code).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('A course with this code already exists.')
        return code
    
    def clean_credits(self):
        credits = self.cleaned_data.get('credits')
        if credits and (credits < 1 or credits > 6):
            raise forms.ValidationError('Credits must be between 1 and 6.')
        return credits
    
    def clean_fee(self):
        fee = self.cleaned_data.get('fee')
        if fee and fee < 0:
            raise forms.ValidationError('Fee cannot be negative.')
        return fee


# ===== SEARCH FORMS =====
class FacultySearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or code...'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class DepartmentSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or code...'})
    )
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Faculties'
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class MajorSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name or code...'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Departments'
    )
    degree_type = forms.ChoiceField(
        choices=[('', 'All Degrees')] + Major.DEGREE_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CourseSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by code or name...'})
    )
    major = forms.ModelChoiceField(
        queryset=Major.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Majors'
    )
    level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Course.LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_credits = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=6,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'})
    )
    max_credits = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=6,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max'})
    )