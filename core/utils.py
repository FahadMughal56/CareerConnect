import fitz  # PyMuPDF for PDFs
from ollama import chat
from pydantic import BaseModel
from typing import Optional


# Extract text from resume
def extract_text_from_resume(resume_file):
    if resume_file.name.endswith('.pdf'):
        doc = fitz.open(stream=resume_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif resume_file.name.endswith('.docx'):
        import docx
        doc = docx.Document(resume_file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""


# Model for skills
class ResumeSkills(BaseModel):
    skills: list[str]


# Model for profile details
class ResumeProfile(BaseModel):
    full_name: str
    email: str
    phone_number: str
    education_level: str
    industry_interest: str
    experience_level: str


# Extract structured profile data (name, phone, etc.)
def extract_profile_with_llama(resume_text):
    user_prompt = f"Extract full_name, email, phone_number, education_level, industry_interest, and experience_level from this resume:\n\n{resume_text}"
    try:
        response = chat(
            messages=[{"role": "user", "content": user_prompt}],
            model="ResumeExtract",  # 👈 your custom model
            format=ResumeProfile.model_json_schema()
        )
        data = ResumeProfile.model_validate_json(response.message.content)
        return data.dict()
    except Exception as e:
        print(f"LLaMA resume profile error: {e}")
        return {}


# Optional: Extract just the skills (for tagging or filtering)
def extract_skills_with_llama(resume_text):
    try:
        response = chat(
            messages=[{"role": "user", "content": resume_text}],
            model="ResumeScan",  # Another custom model if needed
            format=ResumeSkills.model_json_schema()
        )
        skill_data = ResumeSkills.model_validate_json(response.message.content)
        return skill_data.skills

    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []
