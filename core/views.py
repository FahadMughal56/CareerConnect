import requests
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from .serializers import JobSerializer
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .utils import extract_text_from_resume, extract_profile_with_llama, extract_skills_with_llama
from .forms import SignUpForm
from .forms import RecruiterSignUpForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from .models import Job
from .forms import JobForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q


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
    jobs = Job.objects.all()[:4]  # Show top 6 jobs on homepage
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


from .models import JobApplication

@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # If already applied, redirect
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, "You have already applied to this job.")
        return redirect('job_details', job_id=job.id)



    # Save application
    JobApplication.objects.create(
        job=job,
        applicant=request.user,
        resume=request.user.resume  # use the resume uploaded during signup
    )

    messages.success(request, "Application submitted successfully!")
    return redirect('job_details', job_id=job.id)



# API Views for Job Model
class JobListCreateAPIView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class JobDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer




def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')  # Not used in authentication but can help for context

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            request.session['full_name'] = user.full_name
            messages.success(request, "Welcome back!")

            # Redirect both to home (you said index)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials, please try again.")

    return render(request, 'login.html')


def parse_resume_ajax(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        resume_text = extract_text_from_resume(resume_file)
        profile_data = extract_profile_with_llama(resume_text)
        return JsonResponse(profile_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def profile_view(request):
    user = request.user  # Logged-in user
    skills_list = user.skills  # split by comma

    return render(request, 'profile.html', {'user': user, "user_skills": skills_list})



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Ensure password is hashed

            # Resume parsing (optional, based on your existing logic)
            resume_file = request.FILES.get('resume')
            if resume_file:
                resume_text = extract_text_from_resume(resume_file)
                user.skills = extract_skills_with_llama(resume_text)
                user.resume = resume_file  # ✅ Save actual file to DB

            user.save()
            messages.success(request, "Your account has been created successfully! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'signup.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})



def recruiter_signup_view(request):
    if request.method == 'POST':
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the recruiter user
            messages.success(request, 'Recruiter account created successfully! You can now log in.')
            return redirect('login')  # Redirect to login page after successful signup
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterSignUpForm()

    return render(request, 'recruiter_signup.html', {'form': form})


@login_required
def post_job_view(request):
    if not request.user.is_authenticated or request.user.user_type != 'recruiter':
        return redirect('login')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user  # ✅ This is crucial!
            job.save()
            messages.success(request, 'Job posted successfully.')
            return redirect('/recruiter/profile/')

    else:
        form = JobForm()

    return render(request, 'recruiters/post_job.html', {'form': form})



def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')  # or redirect to the page you want after logout
    return redirect('index')  # Default redirect in case of GET request, though GET shouldn't be allowed







@login_required
def recruiter_profile(request):
    if request.user.user_type != 'recruiter':
        return redirect('index')

    jobs = request.user.jobs.all()
    posted_jobs = Job.objects.filter(recruiter=request.user).prefetch_related('applications__applicant')

    return render(request, 'recruiters/profile.html', {'user': request.user, 'jobs': posted_jobs})



@login_required
def edit_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            updated_job = form.save(commit=False)
            updated_job.recruiter = request.user
            updated_job.save()
            return redirect('recruiter_profile')
    else:
        # Convert skills list to comma-separated string
        job.skills = ', '.join(job.skills) if job.skills else ''
        form = JobForm(instance=job)

    return render(request, 'recruiters/edit_job.html', {'form': form})


from django.db.models import Q
from .models import Job

def index(request):
    jobs = Job.objects.all()[:10]
    recommended_jobs = []

    if request.user.is_authenticated and request.user.user_type == "job_seeker":
        user_profile = request.user
        skills = user_profile.skills or []

        print("Logged in as:", request.user.full_name)
        print("User skills:", skills)

        if skills:
            query = Q()
            for skill in skills:
                print("Checking skill:", skill)
                query |= Q(title__icontains=skill) | Q(description__icontains=skill)

            recommended_jobs = Job.objects.filter(query).distinct()[:10]
            print("Found matching jobs:", recommended_jobs.count())

        # Fallback: show random jobs if none matched
        if not recommended_jobs.exists():
            print("No skill-matched jobs found. Showing fallback jobs.")
            recommended_jobs = Job.objects.order_by('?')[:5]

    return render(request, 'index.html', {
        'jobs': jobs,
        'recommended_jobs': recommended_jobs
    })

def jobs_by_category(request, category_name):
    jobs = Job.objects.filter(title__icontains=category_name)
    return render(request, 'category_jobs.html', {
        'jobs': jobs,
        'category': category_name
    })




@login_required
def delete_job_view(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    job.delete()
    return redirect('recruiter_profile')

def job_suggestions(request):
    query = request.GET.get('term', '')
    suggestions = []

    if query:
        # Fetch job titles that start with the search term
        jobs = Job.objects.filter(title__icontains=query).values_list('title', flat=True)[:3]  # Limit to 10 results
        suggestions = list(jobs)

    return JsonResponse(suggestions, safe=False)

