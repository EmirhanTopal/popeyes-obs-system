from django import forms
from .models import Teacher, TeacherSchedule, OfficeHour
# from courses.models import LearningOutcome

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'academic_title', 
            'expertise_area', 
            'office_location', 
            'office_phone',
        ]
        widgets = {
            'expertise_area': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Uzmanlık alanlarınızı yazınız...'
            }),
            'office_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: A-205'
            }),
            'office_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: 0212 123 4567'
            }),
            'academic_title': forms.Select(attrs={'class': 'form-control'}),
        }

class TeacherContactInfoForm(forms.ModelForm):
    """Sadece iletişim bilgileri için form"""
    class Meta:
        model = Teacher
        fields = [
            'office_location',
            'office_phone',
            'personal_website',
            'linkedin',
            'google_scholar',
            'researchgate',
            'orcid'
        ]
        widgets = {
            'office_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ofis numaranız'
            }),
            'office_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ofis telefonunuz'
            }),
            'personal_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'LinkedIn profil linkiniz'
            }),
            'google_scholar': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Google Scholar linkiniz'
            }),
            'researchgate': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'ResearchGate profil linkiniz'
            }),
            'orcid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ORCID ID\'niz'
            }),
        }

# Diğer formlar aynı kalacak...
class TeacherScheduleForm(forms.ModelForm):
    class Meta:
        model = TeacherSchedule
        fields = ['day_of_week', 'start_time', 'end_time', 'location', 'activity_type']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'activity_type': forms.TextInput(attrs={'class': 'form-control'}),
        }

class OfficeHourForm(forms.ModelForm):
    class Meta:
        model = OfficeHour
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

# class LearningOutcomeForm(forms.ModelForm):
#     class Meta:
#         model = LearningOutcome
#         fields = ['outcome_code', 'description', 'bloom_level', 'order']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'outcome_code': forms.TextInput(attrs={'class': 'form-control'}),
#             'bloom_level': forms.Select(attrs={'class': 'form-control'}),
#             'order': forms.NumberInput(attrs={'class': 'form-control'}),
#         }
#         labels = {
#             'outcome_code': 'Çıktı Kodu (Örn: LO1)',
#             'description': 'Öğrenme Çıktısı Açıklaması',
#             'bloom_level': 'Bloom Seviyesi',
#             'order': 'Sıralama',
#         }