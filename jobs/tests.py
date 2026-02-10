from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import JobPosition, Resume, Company
from unittest.mock import patch

User = get_user_model()


class KaryabiCoreTests(TestCase):

    def setUp(self):

        self.client = Client()

        self.employer = User.objects.create_user(
            username='09120000001',
            phone_number='09120000001',
            password='password123',
            is_employer=True,
            is_verified=True
        )

        self.company = Company.objects.create(
            owner=self.employer,
            name="شرکت تست",
            address="تهران",
            website="https://test.com"
        )

        self.job_seeker = User.objects.create_user(
            username='09120000002',
            phone_number='09120000002',
            password='password123',
            is_jobseeker=True,
            is_verified=True
        )


        self.job = JobPosition.objects.create(
            employer=self.employer,
            company=self.company,
            title="برنامه‌نویس پایتون",
            location="تهران",
            description="توضیحات شغل تستی",
            requirements="تسلط به جنگو",
            benefits="بیمه تکمیلی",
            salary_min=20000000,
            is_active=True
        )

    def test_employer_can_create_job(self):
        self.client.force_login(self.employer)
        url = reverse('jobs:create_job')

        data = {
            'company': self.company.id,
            'title': 'طراح رابط کاربری',
            'location': 'اصفهان',
            'description': 'توضیحات تست ایجاد شغل',
            'requirements': 'فیگما',
            'benefits': 'ناهار',
            'salary_min': 15000000,
        }

        response = self.client.post(url, data)


        if response.status_code == 200:
            print("Form Errors:",
                  response.context.get('form').errors if response.context.get('form') else "No Form Context")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(JobPosition.objects.filter(title='طراح رابط کاربری').exists())

    def test_seeker_can_apply_for_job(self):
        self.client.force_login(self.job_seeker)

        resume_file = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")

        url = reverse('jobs:apply_job', kwargs={'job_id': self.job.id})

        data = {
            'cv_file': resume_file,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Resume.objects.filter(job_seeker=self.job_seeker, job_position=self.job).exists())

    @patch('jobs.utils.KavenegarAPI')
    def test_employer_change_status_interview(self, mock_kavenegar):
        mock_instance = mock_kavenegar.return_value
        mock_instance.verify_lookup.return_value = {'status': 200, 'message': 'Mocked SMS Sent'}

        resume = Resume.objects.create(
            job_seeker=self.job_seeker,
            job_position=self.job,
            cv_file=SimpleUploadedFile("test.pdf", b"content"),
            status='pending'
        )

        self.client.force_login(self.employer)

        url = reverse('jobs:change_status', kwargs={'resume_id': resume.id, 'status': 'interview'})

        data = {
            'interview_date': '2026-05-20T14:30'
        }

        response = self.client.post(url, data)

        resume.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(resume.status, 'interview')
        self.assertIsNotNone(resume.interview_date)

    def test_employer_reject_resume(self):
        resume = Resume.objects.create(
            job_seeker=self.job_seeker,
            job_position=self.job,
            cv_file=SimpleUploadedFile("test.pdf", b"content"),
            status='pending'
        )

        self.client.force_login(self.employer)

        url = reverse('jobs:change_status', kwargs={'resume_id': resume.id, 'status': 'rejected'})

        response = self.client.get(url)

        resume.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(resume.status, 'rejected')
