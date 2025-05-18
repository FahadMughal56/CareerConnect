import sys
from django.core.management.base import BaseCommand
from core.utils import extract_text_from_resume  # Ensure this is imported correctly

class Command(BaseCommand):
    help = 'Test resume parsing functionality'

    def add_arguments(self, parser):
        # Add an argument to provide the file path of the resume
        parser.add_argument('resume_file_path', type=str)

    def handle(self, *args, **kwargs):
        resume_file_path = kwargs['resume_file_path']
        try:
            with open(resume_file_path, 'rb') as resume_file:
                resume_text = extract_text_from_resume(resume_file)
                self.stdout.write(self.style.SUCCESS(f"Extracted Text:\n{resume_text}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
