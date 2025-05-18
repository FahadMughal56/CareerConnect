import django
from django.conf import settings
from core.models import Job  # Assuming "core" is the name of your app

# Set up Django
django.setup()


def get_job_data(prompt):
    # Assuming you want to filter jobs based on a query like "Machine Learning in New York"
    location = 'USA'
    title = 'Machine Learning'

    jobs = Job.objects.filter(location__icontains=location, skills__icontains=title)[:10]
    job_links = [job.apply_link for job in jobs]

    return job_links
