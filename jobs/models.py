from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_employer = models.BooleanField(default=False, verbose_name="آیا کارفرما است؟")
    is_jobseeker = models.BooleanField(default=False, verbose_name="آیا کارجو است؟")


class Company(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies', verbose_name="مدیر شرکت")
    name = models.CharField(max_length=200, verbose_name="نام شرکت")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    website = models.URLField(blank=True, null=True, verbose_name="وب‌سایت")

    def __str__(self):
        return self.name


class JobPosition(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs', verbose_name="کارفرما")

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', verbose_name="شرکت", null=True,
                                blank=True)

    title = models.CharField(max_length=200, verbose_name="عنوان شغل")
    salary_min = models.BigIntegerField(default=0, verbose_name="حداقل حقوق")
    requirements = models.TextField(verbose_name="قابلیت‌های مورد نیاز")
    benefits = models.TextField(blank=True, null=True, verbose_name="مزایا")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def __str__(self):
        company_name = self.company.name if self.company else 'بدون شرکت'
        return f"{self.title} ({company_name})"


class Resume(models.Model):
    job_seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes', verbose_name="کارجو")
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='applications',
                                     verbose_name="شغل درخواستی")
    cv_file = models.FileField(upload_to='resumes/', verbose_name="فایل رزومه")

    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('rejected', 'رد شده'),
        ('interview', 'دعوت به مصاحبه'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    interview_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان مصاحبه")

    def __str__(self):
        return f"{self.job_seeker.username} -> {self.job_position.title}"