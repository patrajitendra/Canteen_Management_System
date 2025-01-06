# forms.py
from django import forms
from .models import Student_Masterfile
from django.core.exceptions import ValidationError
import os

# Custom file validation for Aadhar Card
def validate_file(value):
    file_extension = os.path.splitext(value.name)[1].lower()
    if file_extension not in ['.pdf', '.png', '.jpeg', '.jpg']:
        raise ValidationError("File must be in PDF, PNG, or JPEG format.")
    if value.size > 4 * 1024 * 1024:  # 4 MB size limit
        raise ValidationError("File size must not exceed 4MB.")

class StudentRegForm(forms.ModelForm):
    class Meta:
        model = Student_Masterfile
        fields = [
            'registration_number',
            'first_name',
            'last_name',
            'email',
            'batch',
            'branch',
            'admission_date',
            'aadhar_card',
            'semester'
        ]

    # Custom validation for admission_date (should be a 4-digit year)
    def clean_admission_date(self):
        admission_date = self.cleaned_data.get('admission_date')
        if len(str(admission_date)) != 4:
            raise ValidationError("Admission date must be in year format (e.g., 2024).")
        return admission_date
