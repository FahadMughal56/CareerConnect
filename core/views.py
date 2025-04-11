import requests
import json
import os
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from .models import Job
from rest_framework import generics
from .serializers import JobSerializer



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



# Views for rendering HTML pages
def index(request):
    jobs = Job.objects.all()[:6]  # Show top 6 jobs on homepage
    return render(request, 'index.html', {'jobs': jobs})

def search_results(request):
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    jobs = Job.objects.all()

    if keyword:
        jobs = jobs.filter(title__icontains=keyword)
    if location:
        jobs = jobs.filter(location__icontains=location)

    return render(request, 'searchResults.html', {
        'jobs': jobs,
        'keyword': keyword,
        'location': location
    })

def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobDetails.html', {'job': job})

# API Views for Job Model
class JobListCreateAPIView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class JobDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer



def login(request):
    return render(request, 'login.html')




def job_suggestions(request):
    query = request.GET.get('term', '')
    suggestions = []

    if query:
        # Fetch job titles that start with the search term
        jobs = Job.objects.filter(title__icontains=query).values_list('title', flat=True)[:3]  # Limit to 10 results
        suggestions = list(jobs)

    return JsonResponse(suggestions, safe=False)

