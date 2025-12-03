from django import forms
from .models import JobPosition


class JobForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        # فیلدهایی که کاربر باید پر کنه
        fields = ['title', 'salary_min', 'requirements', 'benefits']

        # خوشگل‌سازی فیلدها با کلاس‌های بوت‌استرپ
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: برنامه نویس پایتون'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'به تومان'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'title': 'عنوان شغل',
            'salary_min': 'حقوق پیشنهادی',
            'requirements': 'نیازمندی‌ها',
            'benefits': 'مزایا',
        }