from django import forms
from .models import Employee, EmployeeDocument

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_number', 'name', 'educational_level', 'education_date',
            'specialization', 'position', 'organizational_unit',
            'job_class', 'level', 'evaluation_date', 'evaluation_month',
            'phone', 'notes', 'status'
        ]
        widgets = {
            'education_date': forms.DateInput(attrs={'type': 'date'}),
            'evaluation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ['title', 'document']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان المستند'}),
        }

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='ملف Excel',
        help_text='يرجى اختيار ملف Excel (.xlsx)',
        widget=forms.FileInput(attrs={'accept': '.xlsx'})
    )
