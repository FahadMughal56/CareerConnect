import json
import os
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import requests
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Define paths to the JSON files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_FILE_PATH = os.path.join(BASE_DIR, 'data', 'jobs.json')
INTERNATIONAL_JOBS_FILE_PATH = os.path.join(BASE_DIR, 'data', 'international_jobs.json')



from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        prompt = request.POST.get("user_message", "").strip().lower()
        url = "http://127.0.0.1:11434/api/chat"

        payload = {
            "model": "CareerConnect",
            "messages": [{"role": "user", "content": prompt}],
        }

        def format_text(text):
            """Basic text cleanup without any formatting"""
            return text.strip().replace('*', '')

        def stream_response():
            try:
                with requests.post(url, json=payload, stream=True, timeout=30) as response:
                    if response.status_code == 200:
                        for line in response.iter_lines(decode_unicode=True):
                            if line:
                                try:
                                    json_data = json.loads(line)
                                    if "message" in json_data and "content" in json_data["message"]:
                                        formatted_text = format_text(json_data["message"]["content"])
                                        # Stream text word-by-word
                                        for word in formatted_text.split():
                                            yield word + " "
                                except json.JSONDecodeError:
                                    print(f"Failed to parse line: {line}")
            except requests.exceptions.RequestException as e:
                yield f"Error: {str(e)}"

        return StreamingHttpResponse(stream_response(), content_type="text/event-stream")

    return JsonResponse({"error": "Invalid request method"}, status=400)

# Utility function to load jobs data from JSON
def load_jobs_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# View for the homepage
def index(request):
    jobs = load_jobs_from_json(JOBS_FILE_PATH)
    return render(request, 'index.html', {'jobs': jobs[:4]})

# View for the International Careers page
def international_careers(request):
    international_jobs = load_jobs_from_json(INTERNATIONAL_JOBS_FILE_PATH)
    return render(request, 'internationalCareers.html', {'international_jobs': international_jobs})

# View for company-specific jobs
def company_jobs(request, company_name):
    international_jobs = load_jobs_from_json(INTERNATIONAL_JOBS_FILE_PATH)
    jobs = international_jobs.get(company_name, [])
    return render(request, 'companyJobs.html', {'jobs': jobs, 'company_name': company_name})

# View for job details
def job_details(request, job_id):
    # Load all jobs from both JSON files
    general_jobs = load_jobs_from_json(JOBS_FILE_PATH)
    international_jobs = load_jobs_from_json(INTERNATIONAL_JOBS_FILE_PATH)

    # Combine jobs from both files and find the matching job by `job_id`
    all_jobs = general_jobs + [job for jobs in international_jobs.values() for job in jobs]
    job = next((job for job in all_jobs if job['id'] == job_id), None)
    
    if job is None:
        return render(request, '404.html', status=404)  # Custom 404 if job not found
    
    return render(request, 'jobDetails.html', {'job': job})

# View for the search results page
def search_results(request):
    keyword = request.GET.get('keyword', '').lower()
    location = request.GET.get('location', '').lower()

    # Load jobs from both files
    general_jobs = load_jobs_from_json(JOBS_FILE_PATH)
    international_jobs = load_jobs_from_json(INTERNATIONAL_JOBS_FILE_PATH)
    all_jobs = general_jobs + [job for jobs in international_jobs.values() for job in jobs]

    # Filter jobs based on keyword and location
    filtered_jobs = [
        job for job in all_jobs
        if (keyword in job.get('title', '').lower() or keyword in job.get('company', '').lower()) and
           (location in job.get('location', '').lower())
    ]

    return render(request, 'searchResults.html', {'jobs': filtered_jobs, 'keyword': keyword, 'location': location})

def login(request):
    return render(request, 'login.html')
