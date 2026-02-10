from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import datetime
from django.utils import timezone


# --- User Model ---
class UserManager(models.Manager):
    def employers(self):
        return self.filter(is_employer=True)

    def jobseekers(self):
        return self.filter(is_jobseeker=True)

    def verified_users(self):
        return self.filter(is_verified=True)


class User(AbstractUser):
    is_employer = models.BooleanField(default=False, verbose_name="کارفرما است")
    is_jobseeker = models.BooleanField(default=False, verbose_name="کارجو است")

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        verbose_name="شماره تلفن"
    )

    is_verified = models.BooleanField(default=False, verbose_name="تایید شده")
    email_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username


class Company(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies', verbose_name="مدیر شرکت")
    name = models.CharField(max_length=200, verbose_name="نام شرکت")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    website = models.URLField(blank=True, null=True, verbose_name="وب‌سایت")

    def __str__(self):
        return self.name


class JobPositionManager(models.Manager):
    def active_jobs(self):
        return self.filter(is_active=True)

    def jobs_by_employer(self, user):
        return self.filter(employer=user)

    def high_salary(self, min_salary):
        return self.filter(salary_min__gte=min_salary)


class JobPosition(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کارفرما")
    company = models.ForeignKey('Company', on_delete=models.CASCADE, verbose_name="شرکت")
    title = models.CharField(max_length=100, verbose_name="عنوان شغلی")
    location = models.CharField(max_length=150, verbose_name="موقعیت مکانی")
    description = models.TextField(verbose_name="توضیحات شغل")
    requirements = models.TextField(verbose_name="نیازمندی‌ها")
    benefits = models.TextField(blank=True, null=True, verbose_name="مزایا و تسهیلات")
    salary_min = models.IntegerField(verbose_name="حداقل حقوق (تومان)")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="آگهی فعال باشد؟")

    objects = JobPositionManager()

    def __str__(self):
        return self.title


class ResumeManager(models.Manager):
    def pending(self):
        return self.filter(status='pending')

    def accepted(self):
        return self.filter(status='accepted')

    def rejected(self):
        return self.filter(status='rejected')

    def for_employer(self, employer):
        return self.filter(job_position__employer=employer)


class Resume(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('rejected', 'رد شده'),
        ('interview', 'دعوت به مصاحبه'),
    ]

    job_seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes', verbose_name="کارجو")
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='applications',
                                     verbose_name="شغل درخواستی")
    cv_file = models.FileField(upload_to='resumes/', verbose_name="فایل رزومه")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    interview_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان مصاحبه")
    interview_date = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ مصاحبه")

    objects = ResumeManager()

    def __str__(self):
        return f"{self.job_seeker.username} -> {self.job_position.title}"

class OTPRequest(models.Model):
    phone = models.CharField(max_length=11, verbose_name="شماره موبایل")
    code = models.CharField(max_length=6, verbose_name="کد تایید")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")

    class Meta:
        verbose_name = "کد تایید پیامکی"
        verbose_name_plural = "کدهای تایید پیامکی"


    def is_valid(self):
        return self.created_at > timezone.now() - datetime.timedelta(minutes=2)
