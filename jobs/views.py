from django.shortcuts import render, redirect
from .models import JobPosition ,Company
from .form import JobForm , RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login



def home(request):
    return render(request, 'home.html')


def job_list(request):
    jobs = JobPosition.objects.all().order_by('-created_at')

    return render(request, 'job_list.html', {'jobs': jobs})


@login_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            return redirect('job_list')
    else:
        form = JobForm()
        form.fields['company'].queryset = request.user.companies.all()

    return render(request, 'job_form.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # ---> منطق جدید: ساخت شرکت
            is_employer = form.cleaned_data.get('is_employer')
            company_name = form.cleaned_data.get('company_name')

            if is_employer and company_name:
                # ساخت یک شرکت جدید برای این کاربر
                Company.objects.create(owner=user, name=company_name)

            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})