from django.contrib.auth.forms import UserCreationForm
from jobs.models import User
from django import forms
from .models import JobPosition


class JobForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = ['company', 'title', 'salary_min', 'requirements', 'benefits']

        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),

            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: برنامه نویس پایتون'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'به تومان'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'company': 'انتخاب شرکت',
            'title': 'عنوان شغل',
            'salary_min': 'حقوق پیشنهادی',
            'requirements': 'نیازمندی‌ها',
            'benefits': 'مزایا',
        }


class RegisterForm(UserCreationForm):
    company_name = forms.CharField(
        required=False,
        label='نام شرکت (فقط برای کارفرمایان)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام شرکت خود را وارد کنید'})
    )
    class Meta:
        model = User

        fields = ['username', 'first_name', 'last_name', 'email', 'is_employer', 'is_jobseeker']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'is_employer': 'من کارفرما هستم و می‌خواهم آگهی ثبت کنم',
            'is_jobseeker': 'من کارجو هستم و دنبال کار می‌گردم',
        }

    def clean(self):
        cleaned_data = super().clean()
        is_employer = cleaned_data.get('is_employer')
        is_jobseeker = cleaned_data.get('is_jobseeker')
        company_name = cleaned_data.get('company_name')

        if is_employer and is_jobseeker:
            raise forms.ValidationError(
                "شما نمی‌توانید همزمان هم کارفرما باشید و هم کارجو. لطفاً فقط یکی را انتخاب کنید.")

        if not is_employer and not is_jobseeker:
            raise forms.ValidationError("لطفاً مشخص کنید که کارفرما هستید یا کارجو.")

        if is_employer and not company_name:
            self.add_error('company_name', "وارد کردن نام شرکت برای کارفرمایان الزامی است.")

        return cleaned_data