from django.contrib import admin
from django.urls import path
from jobs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),             # صفحه اصلی
    path('jobs/', views.job_list, name='job_list'), # صفحه لیست شغل‌ها

path('jobs/create/', views.create_job, name='create_job'), # مسیر ثبت شغل
]