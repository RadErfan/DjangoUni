from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, JobPosition, Resume, Company

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('نقش کاربر', {'fields': ('is_employer', 'is_jobseeker')}),
    )
    list_display = UserAdmin.list_display + ('is_employer', 'is_jobseeker')

admin.site.register(User, CustomUserAdmin)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'website')
    search_fields = ('name',)

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'salary_min', 'created_at')
    search_fields = ('title', 'requirements')
    list_filter = ('created_at',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('job_seeker', 'job_position', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')