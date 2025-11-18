from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, JobPosition, Resume


admin.site.register(User, UserAdmin)


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'salary_min', 'created_at')
    search_fields = ('title', 'requirements')
    list_filter = ('created_at',)


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('job_seeker', 'job_position', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')