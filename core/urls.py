from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('job-details/', views.job_details, name='job_details'),
    path('search-results/', views.search_results, name='search_results'),
    path('international-careers/', views.international_careers, name='international_careers'),
    path('international-careers/<str:company_name>/', views.company_jobs, name='company_jobs'),
    path('job-details/<int:job_id>/', views.job_details, name='job_details'),
    path('login/', views.login, name='login'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
]
