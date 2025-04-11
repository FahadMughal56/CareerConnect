from django.urls import path
from . import views
from .views import JobListCreateAPIView, JobDetailAPIView
from .views import job_suggestions

urlpatterns = [
    # HTML pages
    path('', views.index, name='index'),
    path('search-results/', views.search_results, name='search_results'),
    path('job-details/<int:job_id>/', views.job_details, name='job_details'),

    # Optional: Uncomment if you're using these features
    # path('international-careers/', views.international_careers, name='international_careers'),
    # path('international-careers/<str:company_name>/', views.company_jobs, name='company_jobs'),

    # Chat and login (optional if you're using them)
    path('login/', views.login, name='login'),
    path('chatbot/', views.chatbot_view, name='chatbot'),

    # API views
    path('api/jobs/', JobListCreateAPIView.as_view(), name='job-list-create'),
    path('api/jobs/<int:pk>/', JobDetailAPIView.as_view(), name='job-detail'),
    path('search-suggestions/', job_suggestions, name='job_suggestions'),
]
