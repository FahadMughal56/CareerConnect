from django.db import models
from django.contrib.auth.models import AbstractUser



# Job Model
class Job(models.Model):
    id = models.AutoField(primary_key=True)#ok
    title = models.CharField(max_length=255)#ok
    company = models.CharField(max_length=255)#ok
    location = models.CharField(max_length=255)#ok
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)#ok
    description = models.TextField(null=True)#ok
    more_description = models.TextField(null=True, blank=True)
    type = models.CharField(
        max_length=50, choices=[('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time')]#ok
    )
    posted_date = models.DateField(null=True, blank=True)#ok
    skills = models.JSONField(default=list, blank=True, null=True)  #ok
    requirements = models.JSONField(default=list, blank=True, null=True)#ok
    responsibilities = models.JSONField(default=list, blank=True, null=True)#ok
    benefits = models.JSONField(default=list, blank=True, null=True)#ok
    apply_link = models.URLField()#ok
    category = models.CharField(max_length=255, null=True, blank=True)  #ok

    def __str__(self):
        return f"{self.title} - {self.company}"


# Custom User Model
class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    skills = models.JSONField(default=list, blank=True)  # Store user's skills for recommendations
    experience_level = models.CharField(
        max_length=50, choices=[
            ('Junior', 'Junior'), ('Mid', 'Mid-Level'), ('Senior', 'Senior')
        ], null=True, blank=True
    )

    def __str__(self):
        return self.username

# Job Applications Model
class JobApplication(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applied_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} applied to {self.job.title}"
