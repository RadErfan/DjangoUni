
from django.utils.dateparse import parse_datetime
from django.utils.encoding import force_str
from .utils import send_interview_sms
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import jdatetime
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import logging
from .form import UserLoginForm
from .form import JobPositionForm
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import OTPRequest
from .utils import send_otp_code
from django.db.models import Q
from .models import JobPosition, Company, Resume, User
from .form import JobForm, UserRegistrationForm, ResumeForm , JobPosition , UserUpdateForm
from .decorators import email_verified_required


logger = logging.getLogger('django')



def home(request):
    return render(request, 'home.html')



def job_list(request):
    query = request.GET.get('q')
    min_salary = request.GET.get('min_price')
    max_salary = request.GET.get('max_price')

    jobs = JobPosition.objects.filter(is_active=True)

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(requirements__icontains=query) |
            Q(benefits__icontains=query)
        )

    if min_salary:
        jobs = jobs.filter(salary_min__gte=min_salary)

    if max_salary:
        jobs = jobs.filter(salary_min__lte=max_salary)

    jobs = jobs.order_by('-created_at')

    return render(request, 'jobs/job_list.html', {'jobs': jobs})


@login_required
def toggle_job_status(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id, employer=request.user)
    job.is_active = not job.is_active
    job.save()

    status_msg = "فعال" if job.is_active else "غیرفعال"
    messages.success(request, f"وضعیت آگهی به «{status_msg}» تغییر کرد.")

    return redirect('jobs:my_jobs')


@login_required
def employer_dashboard(request):

    today = jdatetime.date.today().strftime("%Y/%m/%d")

    if not request.user.is_employer:
        messages.error(request, "شما دسترسی کارفرما ندارید.")
        return redirect('home')

    resumes = Resume.objects.filter(job_position__employer=request.user).order_by('-applied_at')
    context = {
        'resumes': resumes,
        'today_date': today,
    }
    return render(request, 'jobs/employer_dashboard.html', context)


def job_detail(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id)

    has_active_application = False

    if request.user.is_authenticated:
        has_active_application = Resume.objects.filter(
            job_position=job,
            job_seeker=request.user
        ).exclude(status='rejected').exists()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_active_application
    })


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id, employer=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, "آگهی با موفقیت حذف شد.")
        return redirect('employer_dashboard')

    return render(request, 'jobs/confirm_delete.html', {'job': job})


@login_required
def update_job(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id, employer=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/create_job.html', {'form': form, 'title': 'ویرایش آگهی'})
@login_required
@email_verified_required
def create_job(request):
    user_companies = Company.objects.filter(owner=request.user)
    if not user_companies.exists():
        messages.warning(request, "شما برای ثبت آگهی ابتدا باید یک شرکت ثبت کنید!")
        return redirect('jobs:employer_dashboard')

    if request.method == 'POST':
        form = JobForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, "آگهی شما با موفقیت ثبت شد ✅")
            return redirect('jobs:employer_dashboard')
    else:
        form = JobForm(user=request.user)

    return render(request, 'jobs/create_job.html', {'form': form})


@login_required
@email_verified_required
def my_jobs(request):
    jobs_list = JobPosition.objects.filter(
        employer=request.user
    ).order_by('-created_at')

    # paginator = Paginator(jobs_list, 10)
    # page_number = request.GET.get('page')
    # jobs = paginator.get_page(page_number)

    jobs = jobs_list

    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})


# jobs/views.py


def register(request):
    if request.user.is_authenticated:
        return redirect('jobs:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            if form.cleaned_data.get('is_employer'):
                company_name = form.cleaned_data.get('company_name')
                if company_name:
                    Company.objects.create(owner=user, name=company_name)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activation_link = request.build_absolute_uri(
                reverse('jobs:activate', kwargs={'uidb64': uid, 'token': token})
            )

            print("\n" + "=" * 50)
            print(f"📧 EMAIL SIMULATION FOR: {user.username}")
            print(f"🔗 CLICK HERE TO ACTIVATE: {activation_link}")
            print("=" * 50 + "\n")

            return render(request, 'jobs/register_success.html')

    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def send_verification_email(user, request):
    link = request.build_absolute_uri(
        f'/verify-email/{user.email_token}/'
    )

    # متن ایمیل
    email_subject = 'فعال‌سازی حساب کاربری'
    email_body = f'''
    سلام {user.username} عزیز، خوش آمدید! 🌱

    برای تایید حساب کاربری خود روی لینک زیر کلیک کنید:
    {link}

    اگر شما این درخواست را نداده‌اید، این ایمیل را نادیده بگیرید.
    '''

    send_mail(
        subject=email_subject,
        message=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات پروفایل شما با موفقیت بروزرسانی شد.')
            return redirect('jobs:profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'jobs/profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # این خط باعث میشه بعد از تغییر رمز، کاربر لاگ‌اوت نشه
            update_session_auth_hash(request, user)
            messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد.')
            return redirect('jobs:profile')
        else:
            messages.error(request, 'لطفا خطاهای موجود را اصلاح کنید.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'jobs/password_change.html', {'form': form})



@login_required
@email_verified_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.job_seeker = request.user
            resume.save()

            logger.info(f"Resume uploaded by {request.user.username}")
            return redirect('home')
    else:
        form = ResumeForm()

    return render(request, 'jobs/upload_resume.html', {'form': form})



@login_required
@email_verified_required
def received_resumes(request):
    if not request.user.is_employer:
        return redirect('home')

    resumes = Resume.objects.for_employer(request.user)

    paginator = Paginator(resumes, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/received_resumes.html', {
        'page_obj': page_obj
    })

def send_verification_email(user, request):
    link = request.build_absolute_uri(
        f'/verify-email/{user.email_token}/'
    )

    send_mail(
        subject='تایید حساب کاربری',
        message=f'''
سلام {user.username} عزیز 🌱

برای فعال‌سازی حساب کاربری خود روی لینک زیر کلیک کنید:

{link}
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def verify_email(request, token):
    user = get_object_or_404(User, email_token=token)
    user.is_verified = True
    user.save()

    messages.success(request, '✅ ایمیل شما با موفقیت تایید شد')
    return redirect('jobs:login')


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('jobs:home')
    else:
        form = UserLoginForm()

    return render(request, 'jobs/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('jobs:home')
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'jobs/company_list.html', {'companies': companies})


@login_required
def sent_resumes(request):
    if not getattr(request.user, 'is_jobseeker', False):
        return render(request, 'jobs/403.html', status=403)

    resumes = Resume.objects.filter(job_seeker=request.user)\
        .select_related('job_position', 'job_position__company')\
        .order_by('-applied_at')

    return render(request, 'jobs/sent_resumes.html', {'resumes': resumes})


@login_required(login_url='jobs:login')
def apply_job(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id)
    if not job.is_active:
        messages.error(request, "این فرصت شغلی بسته شده است و امکان ارسال رزومه وجود ندارد.")
        return redirect('jobs:job_list')
    existing_resume = Resume.objects.filter(job_position=job, job_seeker=request.user).first()
    existing_resume = Resume.objects.filter(job_seeker=request.user, job_position=job).first()
    if existing_resume:
        messages.warning(request, "شما قبلاً برای این شغل رزومه ارسال کرده‌اید.")
        return redirect('jobs:job_detail', job_id=job.id)

        if request.method == 'POST':
            existing_resume.delete()

    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.job_position = job
            resume.job_seeker = request.user
            resume.status = 'pending'
            resume.save()
            messages.success(request, "رزومه جدید شما با موفقیت ارسال شد.")
            return redirect('jobs:job_detail', job.id)
    else:
        form = ResumeForm()

    return render(request, 'jobs/apply_job.html', {'job': job, 'form': form})


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)

    company_jobs = JobPosition.objects.filter(company=company, is_active=True)

    context = {
        'company': company,
        'jobs': company_jobs
    }
    return render(request, 'company_detail.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل شما با موفقیت بروزرسانی شد! ✅')

            return redirect('jobs:home')

    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def job_update(request, pk):
    job = get_object_or_404(JobPosition, pk=pk)

    if job.employer != request.user:
        return redirect('jobs:home')

    if request.method == 'POST':
        form = JobPositionForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('jobs:job_detail', job_id=job.pk)
    else:
        form = JobPositionForm(instance=job)

    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'ویرایش آگهی'})


@login_required
def change_application_status(request, pk, status):
    application = get_object_or_404(Resume, pk=pk)

    if application.job_position.employer != request.user:
        messages.error(request, "⛔ شما اجازه تغییر وضعیت این رزومه را ندارید.")
        return redirect('jobs:employer_dashboard')

    if status in ['interview', 'rejected', 'pending']:
        application.status = status
        application.save()

        msg_map = {
            'interview': "✅ کارجو به مصاحبه دعوت شد.",
            'rejected': "❌ رزومه رد شد.",
            'pending': "🕒 وضعیت به «در انتظار» تغییر کرد."
        }
        messages.success(request, msg_map.get(status, "وضعیت تغییر کرد."))

    return redirect('jobs:employer_dashboard')


@login_required
def delete_application(request, pk):
    application = get_object_or_404(Resume, pk=pk)

    if application.job_position.employer != request.user:
        messages.error(request, "⛔ دسترسی غیرمجاز!")
        return redirect('jobs:employer_dashboard')


    if application.status == 'pending':
        messages.warning(request, "⚠️ ابتدا باید وضعیت رزومه (قبول/رد) را مشخص کنید، سپس می‌توانید آن را حذف کنید.")
    else:
        application.delete()
        messages.success(request, "🗑️ رزومه با موفقیت از لیست حذف شد.")

    return redirect('jobs:employer_dashboard')



def translate_to_english(text):
    if text is None:
        return None
    persian_nums = "۰۱۲۳۴۵۶۷۸۹"
    english_nums = "0123456789"
    translation_table = str.maketrans(persian_nums, english_nums)
    return text.translate(translation_table)


def login_phone_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        phone = translate_to_english(phone)

        if phone:
            request.session['phone_number'] = phone

            send_otp_code(phone)

            return redirect('jobs:verify_sms')
        else:
            messages.error(request, "شماره موبایل وارد نشده است.")

    return render(request, 'jobs/login_phone.html')



def verify_otp_view(request):
    User = get_user_model()
    phone_number = request.session.get('phone_number')

    if not phone_number:
        messages.error(request, "نشست شما منقضی شده، لطفا مجدد شماره را وارد کنید.")
        return redirect('jobs:login_phone')

    if request.method == 'POST':
        entered_code = request.POST.get('code')
        entered_code = translate_to_english(entered_code)

        otp_record = OTPRequest.objects.filter(phone=phone_number, code=entered_code).last()

        if otp_record and otp_record.is_valid():
            otp_record.delete()


            user = User.objects.filter(phone_number=phone_number).first()

            if user:
                login(request, user)
                messages.success(request, f"خوش آمدید {user.username} عزیز! 🌹")

                if user.is_employer:
                    return redirect('jobs:employer_dashboard')
                elif user.is_jobseeker:
                    return redirect('jobs:sent_resumes')
                else:
                    return redirect('jobs:home')

            else:

                new_user = User.objects.create_user(username=phone_number, phone_number=phone_number)
                new_user.is_jobseeker = True  # پیش‌فرض کارجو
                new_user.is_active = True
                new_user.save()

                login(request, new_user)
                messages.warning(request, "حساب کاربری جدید برای شما ساخته شد. لطفاً اطلاعات پروفایل را تکمیل کنید.")
                return redirect('jobs:edit_profile')

        else:
            messages.error(request, "❌ کد وارد شده اشتباه یا منقضی شده است.")

    return render(request, 'jobs/verify_sms.html', {'phone_number': phone_number})


# jobs/views.py

def dev_email_inbox(request):

    if not request.user.is_superuser:
        pass

    unverified_users = User.objects.filter(is_verified=False).order_by('-date_joined')

    emails = []
    for user in unverified_users:
        verify_url = request.build_absolute_uri(reverse('jobs:verify_email', args=[user.email_token]))
        emails.append({
            'user': user,
            'url': verify_url,
            'time': user.date_joined
        })

    return render(request, 'jobs/dev_email_inbox.html', {'emails': emails})

def register_success(request):
    return render(request, 'jobs/register_success.html')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        user.is_active = True
        user.is_verified = True
        user.save()

        login(request, user)

        messages.success(request, 'حساب شما با موفقیت فعال شد! خوش آمدید.')
        return redirect('jobs:home')
    else:
        return render(request, 'jobs/activation_invalid.html')


@login_required
def job_resumes(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id, employer=request.user)


    resumes = job.applications.all().order_by('-applied_at')

    return render(request, 'jobs/job_resumes.html', {
        'job': job,
        'resumes': resumes
    })


@login_required
def change_application_status(request, resume_id, status):
    resume = get_object_or_404(Resume, id=resume_id)

    if request.user != resume.job_position.employer:
        messages.error(request, "⛔ شما اجازه تغییر وضعیت این رزومه را ندارید.")
        return redirect('jobs:employer_dashboard')

    valid_statuses = ['interview', 'rejected', 'pending']
    if status not in valid_statuses:
        messages.error(request, "وضعیت نامعتبر است.")
        return redirect('jobs:job_resumes', job_id=resume.job_position.id)

    if status == 'interview':
        date_str = request.POST.get('interview_date')

        if date_str:
            try:
                dt = parse_datetime(date_str)
                resume.interview_date = dt
                resume.status = status
                resume.save()


                formatted_date = dt.strftime("%Y-%m-%d %H:%M")

                send_interview_sms(
                    resume.job_seeker.phone_number,
                    resume.job_seeker.get_full_name() or resume.job_seeker.username,
                    resume.job_position.title,
                    formatted_date,
                    resume.job_position.salary_min
                )
                messages.success(request, f"✅ دعوت به مصاحبه برای تاریخ {formatted_date} ثبت شد.")

            except ValueError:
                messages.error(request, "❌ فرمت تاریخ نامعتبر است.")
        else:
            messages.warning(request, "⚠️ تاریخ مصاحبه انتخاب نشد!")
            return redirect('jobs:job_resumes', job_id=resume.job_position.id)

    elif status == 'rejected':
        resume.status = status
        resume.interview_date = None
        resume.save()
        messages.error(request, "❌ رزومه رد شد.")

    elif status == 'pending':
        resume.status = status
        resume.interview_date = None
        resume.save()
        messages.info(request, "🕒 وضعیت به «در انتظار» برگشت.")

    return redirect('jobs:job_resumes', job_id=resume.job_position.id)
