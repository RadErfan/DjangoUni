from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .form import UserLoginForm

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),

    path('signup/', views.register, name='signup'),

    path('login/', auth_views.LoginView.as_view(
        template_name='jobs/login.html',
        authentication_form=UserLoginForm,
        redirect_authenticated_user=True
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('login/sms/', views.login_phone_view, name='login_sms'),
    path('verify/sms/', views.verify_otp_view, name='verify_sms'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url=reverse_lazy('jobs:password_change_done')
    ), name='change_password'),
    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='change_password_done.html'
    ), name='password_change_done'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('companies/', views.company_list, name='company_list'),
    path('company/<int:pk>/', views.company_detail, name='company_detail'),

    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:pk>/update/', views.job_update, name='job_update'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),

    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('update/<int:job_id>/', views.update_job, name='update_job'),
    path('delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('toggle-status/<int:job_id>/', views.toggle_job_status, name='toggle_job_status'),

    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('employer/resumes/', views.received_resumes, name='received_resumes'),
    path('my-resumes/', views.sent_resumes, name='sent_resumes'),

    path('resume/<int:pk>/status/<str:status>/', views.change_application_status, name='change_status'),
path('dev/inbox/', views.dev_email_inbox, name='dev_inbox'),


    path('resume/<int:pk>/delete/', views.delete_application, name='delete_application'),
path('register-success/', views.register_success, name='register_success'),
path('activate/<uidb64>/<token>/', views.activate, name='activate'),
path('my-jobs/<int:job_id>/resumes/', views.job_resumes, name='job_resumes'),
    path('resume/<int:resume_id>/change-status/<str:status>/', views.change_application_status, name='change_status'),
path('resume/<int:resume_id>/change-status/<str:status>/', views.change_application_status, name='change_status'),

]
