from django.urls import path
from . import views
from .views import JobListCreateAPIView, JobDetailAPIView
from .views import job_suggestions
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # HTML pages
    path('', views.index, name='index'),
    path('search-results/', views.search_results, name='search_results'),
    path('job-details/<int:job_id>/', views.job_details, name='job_details'),

    # Optional: Uncomment if you're using these features
    # path('international-careers/', views.international_careers, name='international_careers'),
    # path('international-careers/<str:company_name>/', views.company_jobs, name='company_jobs'),

    # Chat and login (optional if you're using them)
    path('login/', views.login_view, name='login'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    # API views
    path('api/jobs/', JobListCreateAPIView.as_view(), name='job-list-create'),
    path('api/jobs/<int:pk>/', JobDetailAPIView.as_view(), name='job-detail'),
    path('search-suggestions/', job_suggestions, name='job_suggestions'),
    path('ajax/parse-resume/', views.parse_resume_ajax, name='parse_resume_ajax'),
    path('profile/', views.profile_view, name='profile'),
    path('recruiter/signup/', views.recruiter_signup_view, name='recruiter_signup'),
    path('recruiter/profile/', views.recruiter_profile, name='recruiter_profile'),
    path('recruiter/post-job/', views.post_job_view, name='post_job_view'),
    path('recruiter/edit-job/<int:job_id>/', views.edit_job_view, name='edit_job'),
    path('recruiter/delete-job/<int:job_id>/', views.delete_job_view, name='delete_job'),
    path('apply/<int:job_id>/', views.apply_to_job, name='apply_to_job'),
    path('category/<str:category_name>/', views.jobs_by_category, name='jobs_by_category'),



]
