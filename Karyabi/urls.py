from django.contrib import admin
from django.urls import path
from jobs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
path('register/', views.register, name='register'),

path('jobs/create/', views.create_job, name='create_job'),
]