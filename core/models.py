from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
import json


# Job Model
class Job(models.Model):
    id = models.AutoField(primary_key=True)#ok
    title = models.CharField(max_length=255)#ok
    company = models.CharField(max_length=255)#ok
    location = models.CharField(max_length=255)#ok
    salary = models.CharField(max_length=255, null=True)#ok
    industry = models.CharField(max_length=255, null=True)#ok
    description = models.TextField(null=True)#ok
    more_description = models.TextField(null=True, blank=True)
    type = models.CharField(
        max_length=50, choices=[('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time')]#ok
    )
    posted_date = models.DateField(null=True, blank=True)#ok
    skills = models.JSONField(default=list, blank=True, null=True)  #ok
    apply_link = models.URLField()#ok
    category = models.CharField(max_length=255, null=True, blank=True)  #ok
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs', null=True,
                                  blank=True)


    def __str__(self):
        return f"{self.title} - {self.company}"



# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# Custom User Model (No username)
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    # Job seeker-specific fields
    education_level = models.CharField(max_length=255, null=True, blank=True)
    job_preference = models.CharField(max_length=255, null=True, blank=True)
    industry_interest = models.CharField(max_length=255, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience_level = models.CharField(
        max_length=50,
        choices=[('Junior', 'Junior'), ('Mid', 'Mid-Level'), ('Senior', 'Senior')],
        null=True,
        blank=True
    )

    # Recruiter-specific fields
    company_website = models.URLField(null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)

    # Common fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    USER_TYPE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='job_seeker'
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='applications/', null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.applicant.full_name} applied to {self.job.title}'

class ResumeParsingLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    raw_resume_text = models.TextField(null=True, blank=True)
    extracted_skills = models.JSONField(default=list, blank=True)
