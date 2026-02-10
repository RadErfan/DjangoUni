import os
import django
import random
import sys

# تنظیمات محیطی جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Karyabi.settings')
django.setup()

# حل مشکل پرینت فارسی
sys.stdout.reconfigure(encoding='utf-8')

from jobs.models import User, Company, JobPosition, Resume


def make_erfan_boss():
    print("🚀 شروع عملیات: تبدیل عرفان راد به مدیر بزرگ...")

    # 1. پیدا کردن عرفان راد
    try:
        erfan = User.objects.get(username='ErfanRad')
    except User.DoesNotExist:
        print("❌ کاربر ErfanRad پیدا نشد! لطفا اول ثبت نامش کنید.")
        return

    # 2. تبدیل به کارفرما
    erfan.is_employer = True
    erfan.is_jobseeker = False  # شاید قبلا کارجو بوده، الان دیگه رئیسه
    erfan.save()
    print(f"✅ {erfan.username} حالا رسماً یک کارفرماست!")

    # 3. ثبت شرکت برای عرفان (اگر نداره)
    company, created = Company.objects.get_or_create(
        owner=erfan,
        defaults={
            'name': 'هلدینگ بین‌المللی راد و شرکا',
            'address': 'تهران، برج میلاد، طبقه آخر',
            'website': 'https://erfanrad.com'
        }
    )
    if created:
        print(f"🏢 شرکت تاسیس شد: {company.name}")
    else:
        print(f"🏢 عرفان از قبل شرکت داشت: {company.name}")

    # 4. ایجاد موقعیت‌های شغلی توسط عرفان
    job_titles = [
        ('CTO (مدیر فنی)', 50000000),
        ('Senior Django Developer', 35000000),
        ('مدیر مارکتینگ', 20000000),
        ('کارآموز پایتون (با حقوق)', 8000000)
    ]

    my_jobs = []
    for title, min_salary in job_titles:
        # چک میکنیم تکراری نسازه
        job, created = JobPosition.objects.get_or_create(
            employer=erfan,
            title=title,
            defaults={
                'company': company,
                'location': 'تهران',
                'description': 'ما دنبال بهترین‌ها هستیم. اگر فکر می‌کنید بهترین هستید، بسم‌الله.',
                'requirements': 'تعهد، تخصص، اخلاق حرفه‌ای',
                'benefits': 'سفرهای خارجی، پلی‌استیشن ۵، ناهار',
                'salary_min': min_salary,
                'is_active': True
            }
        )
        my_jobs.append(job)
        if created:
            print(f"💼 آگهی شغلی جدید عرفان: {title}")

    # 5. هجوم کارجوها برای ارسال رزومه
    # پیدا کردن همه یوزرهایی که با seeker_ شروع میشن
    seekers = User.objects.filter(username__startswith='seeker_')

    if not seekers.exists():
        print("⚠️ کارجویی پیدا نشد! لطفا اول اسکریپت populate_db.py را اجرا کنید.")
        return

    print(f"👥 {seekers.count()} کارجو پیدا شد که آماده استخدام هستند...")

    resume_count = 0
    for job in my_jobs:
        # انتخاب تصادفی ۵ تا ۱۰ نفر برای هر شغل
        applicants = random.sample(list(seekers), k=min(len(seekers), random.randint(3, 8)))

        for seeker in applicants:
            # چک کنیم قبلا رزومه نداده باشه
            if not Resume.objects.filter(job_seeker=seeker, job_position=job).exists():
                Resume.objects.create(
                    job_seeker=seeker,
                    job_position=job,
                    cv_file='resumes/dummy.pdf',  # فرض بر اینه که فایل dummy.pdf هست
                    status='pending'  # وضعیت در انتظار بررسی
                )
                resume_count += 1
                # print(f"  📩 رزومه از {seeker.username} برای {job.title}")

    print(f"🎉 عملیات تمام شد! {resume_count} رزومه جدید برای شرکت عرفان ارسال شد.")
    print("حالا می‌تونید با یوزر ErfanRad لاگین کنید و رزومه‌ها رو مدیریت کنید.")


if __name__ == '__main__':
    make_erfan_boss()
