from django.shortcuts import render, redirect
from .models import JobPosition
from .form import JobForm
from django.contrib.auth.decorators import login_required


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
            # شغل رو موقتاً نگه دار تا کارفرما رو بهش وصل کنیم
            job = form.save(commit=False)
            job.employer = request.user  # کارفرما میشه همین کسی که لاگین کرده
            job.save()
            return redirect('job_list')  # بعد از ثبت، برو به لیست شغل‌ها
    else:
        form = JobForm()

    return render(request, 'job_form.html', {'form': form})