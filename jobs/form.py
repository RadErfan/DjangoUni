from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import JobPosition, Resume, Company

User = get_user_model()



from django import forms
from .models import User


class UserRegistrationForm(forms.ModelForm):
    pass1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'real-input', 'placeholder': 'رمز عبور'}),
        label="رمز عبور"
    )
    pass2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'real-input', 'placeholder': 'تکرار رمز عبور'}),
        label="تکرار رمز عبور"
    )


    company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'real-input', 'placeholder': 'نام مجموعه'}),
        label="نام مجموعه"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_employer', 'is_jobseeker']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'real-input', 'placeholder': 'نام کاربری'}),
            'email': forms.EmailInput(attrs={'class': 'real-input', 'placeholder': 'ایمیل'}),
            'first_name': forms.TextInput(attrs={'class': 'real-input', 'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'real-input', 'placeholder': 'نام خانوادگی'}),
            'phone_number': forms.TextInput(attrs={'class': 'real-input', 'placeholder': 'شماره موبایل'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get('pass1')
        p2 = cleaned_data.get('pass2')
        if p1 and p2 and p1 != p2:
            self.add_error('pass2', "رمز عبور و تکرار آن مطابقت ندارند.")

        is_employer = cleaned_data.get('is_employer')
        company_name = cleaned_data.get('company_name')

        if is_employer and not company_name:
            self.add_error('company_name', "نوشتن نام مجموعه برای کارفرمایان الزامی است.")

        return cleaned_data

    def save(self, commit=True):
        # فقط یوزر و پسورد رو ست کن
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['pass1'])

        if commit:
            user.save()
            # اون تیکه کد ساخت Company رو از اینجا پاک کن، چون توی View داریش

        return user



class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control glass-input',
        'placeholder': 'نام کاربری',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control glass-input',
        'placeholder': 'رمز عبور',
    }))

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if not user.is_verified:
            raise ValidationError(
                "❌ ایمیل شما تایید نشده است. لطفاً به ایمیل خود مراجعه کرده و روی لینک فعال‌سازی کلیک کنید.",
                code='inactive',
            )



class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label='نام / نام شرکت', max_length=100, required=False)
    email = forms.EmailField(label='ایمیل', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'glass-input form-control'})


class JobForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = ['company', 'title', 'location', 'salary_min', 'description', 'requirements', 'benefits', 'is_active']

        labels = {
            'company': 'نام شرکت',
            'title': 'عنوان شغلی',
            'location': 'موقعیت مکانی',
            'description': 'توضیحات کلی شغل',
            'requirements': 'نیازمندی‌ها و مهارت‌ها',
            'benefits': 'مزایا و تسهیلات',
            'salary_min': 'حداقل حقوق (تومان)',
            'is_active': 'آگهی فعال باشد؟',
        }

        widgets = {
            'company': forms.Select(attrs={'class': 'form-select glass-input'}),
            'title': forms.TextInput(
                attrs={'class': 'form-control glass-input', 'placeholder': 'مثلا: توسعه‌دهنده پایتون'}),
            'location': forms.TextInput(
                attrs={'class': 'form-control glass-input', 'placeholder': 'مثلا: تهران، جردن'}),
            'salary_min': forms.NumberInput(
                attrs={'class': 'form-control glass-input', 'placeholder': 'مبلغ به تومان (فقط عدد)'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control glass-input', 'rows': 4, 'placeholder': 'شرح وظایف...'}),
            'requirements': forms.Textarea(
                attrs={'class': 'form-control glass-input', 'rows': 4, 'placeholder': 'مهارت‌های مورد نیاز...'}),
            'benefits': forms.Textarea(
                attrs={'class': 'form-control glass-input', 'rows': 3, 'placeholder': 'بیمه، پاداش...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(JobForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['company'].queryset = Company.objects.filter(owner=user)
            self.fields['company'].empty_label = "انتخاب شرکت..."



class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['cv_file']
        widgets = {
            'cv_file': forms.FileInput(attrs={
                'class': 'form-control glass-input',
                'accept': '.pdf,.doc,.docx'
            }),
        }
        labels = {
            'cv_file': 'فایل رزومه (PDF یا Word)',
        }


class JobPositionForm(forms.ModelForm):
    class Meta:
        model = JobPosition
        fields = ['title', 'location', 'salary_min', 'description', 'requirements', 'benefits', 'is_active']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان شغلی'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلا: تهران، ونک'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'حداقل حقوق'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'شرح کامل موقعیت شغلی...'}),
            'requirements': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'مهارت‌های مورد نیاز...'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'مزایا و تسهیلات...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        labels = {
            'salary_min': 'حداقل حقوق (تومان)',
            'is_active': 'آگهی فعال باشد؟'
        }
