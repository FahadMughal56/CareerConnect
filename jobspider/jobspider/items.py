import scrapy
from scrapy_djangoitem import DjangoItem
from core.models import Job  # Ensure this is your correct Django app name

class JobItem(DjangoItem):
    django_model = Job
