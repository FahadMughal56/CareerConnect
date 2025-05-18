# core/forms.py
import json
from django import forms
from .models import CustomUser

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'email', 'phone_number',
            'education_level', 'job_preference',
            'industry_interest', 'experience_level',
            'resume', 'password'
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password != password_confirmation:
            raise forms.ValidationError("The two password fields must match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'job_seeker'  # Ensure user type is set to 'job_seeker'
        if commit:
            user.save()
        return user


class RecruiterSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone_number', 'company_website', 'company_description', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'recruiter'  # Ensure user type is set to 'recruiter'
        if commit:
            user.save()
        return user

from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    # 👇 Override the skills field to use TextInput
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'skills-input',
            'placeholder': 'e.g. Python, Django, REST API'
        })
    )

    class Meta:
        model = Job
        exclude = ['recruiter', 'posted_date']

    # 👇 Clean method to split the comma-separated string
    def clean_skills(self):
        raw_skills = self.cleaned_data.get('skills')
        skills_list = []

        try:
            parsed = json.loads(raw_skills)
            skills_list = [item['value'] for item in parsed if 'value' in item]
        except Exception as e:
            print("Error parsing Tagify data:", e)

        return skills_list
