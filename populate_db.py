import os
import django
import random
import sys

# تنظیمات محیطی جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Karyabi.settings')
django.setup()

# حل مشکل نمایش فارسی در ترمینال ویندوز
sys.stdout.reconfigure(encoding='utf-8')

from jobs.models import User, Company, JobPosition, Resume

# دیتای دستی
FIRST_NAMES = ['علی', 'محمد', 'رضا', 'سارا', 'مریم', 'زهرا', 'امید', 'کاوه', 'نیکان', 'الهام']
LAST_NAMES = ['راد', 'تهرانی', 'محمدی', 'حسینی', 'کریمی', 'اکبری', 'صادقی', 'کاظمی', 'رحیمی', 'یزدانی']
COMPANY_NAMES = ['تکنولوژی پیشرو', 'داده پردازان شرق', 'نوآوران وب', 'گروه صنعتی البرز', 'استارتاپ کهکشان',
                 'شرکت نرم‌افزاری پارت']
JOB_TITLES = ['برنامه‌نویس پایتون', 'طراح UI/UX', 'مدیر محصول', 'کارشناس دیجیتال مارکتینگ', 'حسابدار ارشد', 'منشی',
              'برنامه‌نویس فرانت‌اند']
CITIES = ['تهران', 'اصفهان', 'شیراز', 'مشهد', 'تبریز', 'کرج']


def create_data():
    print("🚀 شروع ساخت داده‌های تستی...")

    # 1. ساخت ۱۰ تا کارفرما (Employer)
    employers = []
    for i in range(10):
        username = f'employer_{i + 1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'emp{i + 1}@test.com',
                password='123',
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
                is_employer=True,
                is_verified=True,
                # استفاده از i برای یونیک کردن شماره
                phone_number=f"0910{str(i).zfill(7)}"
            )
            employers.append(user)
            print(f"✅ کارفرما: {username}")
        else:
            employers.append(User.objects.get(username=username))

    # 2. ساخت شرکت برای هر کارفرما
    jobs = []
    for i, emp in enumerate(employers):
        if not Company.objects.filter(owner=emp).exists():
            comp = Company.objects.create(
                owner=emp,
                name=f"{COMPANY_NAMES[i % len(COMPANY_NAMES)]} {random.randint(1, 100)}",
                address=f"{random.choice(CITIES)}، خیابان اصلی",
                website=f"http://www.company{i}.com"
            )
            # ساخت شغل برای شرکت
            for _ in range(2):
                job = JobPosition.objects.create(
                    employer=emp,
                    company=comp,
                    title=random.choice(JOB_TITLES),
                    location=random.choice(CITIES),
                    description="این یک فرصت شغلی عالی در یک شرکت معتبر است...",
                    requirements="مسلط به جنگو، روحیه کار تیمی، نظم و انضباط",
                    benefits="بیمه، پاداش، ناهار",
                    # نکته مهم: فقط salary_min رو مقدار میدیم چون salary_max در مدل شما نیست
                    salary_min=random.randint(8, 20) * 1000000,
                    is_active=True
                )
                jobs.append(job)
                print(f"💼 شغل ایجاد شد: {job.title}")

    # 3. ساخت ۲۰ تا کارجو (Job Seeker)
    seekers = []
    for i in range(20):
        username = f'seeker_{i + 1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'seeker{i + 1}@test.com',
                password='123',
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
                is_jobseeker=True,
                is_verified=True,
                phone_number=f"0935{str(i).zfill(7)}"
            )
            seekers.append(user)
            print(f"👤 کارجو: {username}")
        else:
            seekers.append(User.objects.get(username=username))

    # 4. ارسال رزومه
    # حتما باید فایل media/resumes/dummy.pdf وجود داشته باشه
    for seeker in seekers:
        if jobs:
            # هر کارجو به ۱ تا ۳ تا شغل درخواست بده
            selected_jobs = random.sample(jobs, k=random.randint(1, 3))
            for job in selected_jobs:
                if not Resume.objects.filter(job_seeker=seeker, job_position=job).exists():
                    Resume.objects.create(
                        job_seeker=seeker,
                        job_position=job,
                        cv_file='resumes/dummy.pdf',
                        status=random.choice(['pending', 'rejected', 'interview'])
                    )
                    print(f"📄 رزومه: {seeker.username} -> {job.title}")

    print("🎉 تمام! دیتابیس با موفقیت پر شد.")


if __name__ == '__main__':
    create_data()
