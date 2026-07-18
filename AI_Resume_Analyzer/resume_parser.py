import os
import json
from pathlib import Path

import fitz
import docx

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

# ----------------------------------------
# Load Environment Variables
# ----------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)

# ----------------------------------------
# Resume Models
# ----------------------------------------

class ResumeDetails(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""


class Resume(BaseModel):
    details: ResumeDetails

    education: list[str] = Field(default_factory=list)

    skills: list[str] = Field(default_factory=list)

    experience: list[str] = Field(default_factory=list)

    projects: list[str] = Field(default_factory=list)

    certifications: list[str] = Field(default_factory=list)


class JobDescription(BaseModel):
    title: str = ""

    company: str = ""

    required_skills: list[str] = Field(default_factory=list)

    preferred_skills: list[str] = Field(default_factory=list)

    experience: str = ""

    education: str = ""


class FinalResult(BaseModel):
    overall_score: int

    technical_score: int

    education_score: int

    experience_score: int

    project_score: int

    missing_skills: list[str]

    strengths: list[str]

    improvements: list[str]

    verdict: str


# ----------------------------------------
# Read Resume
# ----------------------------------------

def read_resume(file_path):

    file_path = Path(file_path)

    if file_path.suffix.lower() == ".pdf":

        text = ""

        pdf = fitz.open(file_path)

        for page in pdf:
            text += page.get_text()

        pdf.close()

        return text

    elif file_path.suffix.lower() == ".docx":

        document = docx.Document(file_path)

        text = ""

        for para in document.paragraphs:
            text += para.text + "\n"

        return text

    else:
        raise Exception("Unsupported file format")
    # ----------------------------------------
# Parse Resume using Groq
# ----------------------------------------

def parse_resume(resume_text):

    prompt = f"""
You are an expert ATS Resume Parser.

Extract the following information from the resume.

Return ONLY valid JSON.

{{
    "details": {{
        "name":"",
        "email":"",
        "phone":"",
        "location":"",
        "linkedin":"",
        "github":""
    }},
    "education":[],
    "skills":[],
    "experience":[],
    "projects":[],
    "certifications":[]
}}

Resume:

{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    data = json.loads(
        response.choices[0].message.content
    )

    return Resume.model_validate(data)
# ----------------------------------------
# Parse Job Description using Groq
# ----------------------------------------

def parse_job(job_text):

    prompt = f"""
You are an expert ATS Job Description Parser.

Extract the following information from the Job Description.

Return ONLY valid JSON.

{{
    "title":"",
    "company":"",
    "required_skills":[],
    "preferred_skills":[],
    "experience":"",
    "education":""
}}

Job Description:

{job_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    data = json.loads(
        response.choices[0].message.content
    )

    return JobDescription.model_validate(data)
# ----------------------------------------
# Final Resume Evaluation
# ----------------------------------------

def final_score(job_text, resume):

    if isinstance(job_text, str):
        job = parse_job(job_text)
    else:
        job = job_text

    prompt = f"""
You are an ATS Resume Evaluator.

Compare the following Resume with the Job Description.

Return ONLY valid JSON.

Job Description:
{job.model_dump_json(indent=2)}

Resume:
{resume.model_dump_json(indent=2)}

Return JSON in this format:

{{
    "overall_score": 0,
    "technical_score": 0,
    "education_score": 0,
    "experience_score": 0,
    "project_score": 0,
    "missing_skills": [],
    "strengths": [],
    "improvements": [],
    "verdict": ""
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)

    return FinalResult.model_validate(data)
import os
import streamlit as st

from resume_parser import (
    read_resume,
    parse_resume,
    final_score,
)

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
)

st.title("📄 AI Resume Analyzer")

st.write("Upload your Resume and paste the Job Description.")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

job_description = st.text_area(
    "Paste Job Description",
    height=250
)

if st.button("Analyze Resume"):

    if uploaded_file is None:
        st.error("Please upload a resume.")
        st.stop()

    if not job_description.strip():
        st.error("Please enter Job Description.")
        st.stop()

    os.makedirs("temp", exist_ok=True)

    resume_path = os.path.join(
        "temp",
        uploaded_file.name
    )

    with open(resume_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:

        with st.spinner("Analyzing Resume..."):

            resume_text = read_resume(resume_path)

            candidate = parse_resume(resume_text)

            result = final_score(
                job_description,
                candidate
            )

        st.success("Analysis Complete ✅")

        st.subheader("Overall Score")
        st.progress(result.overall_score / 100)
        st.write(f"**{result.overall_score}/100**")

        st.subheader("Scores")

        st.write(
            f"Technical : {result.technical_score}"
        )

        st.write(
            f"Education : {result.education_score}"
        )

        st.write(
            f"Experience : {result.experience_score}"
        )

        st.write(
            f"Projects : {result.project_score}"
        )

        st.subheader("Missing Skills")

        if result.missing_skills:
            for skill in result.missing_skills:
                st.write("•", skill)
        else:
            st.write("No major missing skills.")

        st.subheader("Strengths")

        if result.strengths:
            for item in result.strengths:
                st.write("✅", item)

        st.subheader("Improvements")

        if result.improvements:
            for item in result.improvements:
                st.write("⚠️", item)

        st.subheader("Verdict")

        st.success(result.verdict)

    except Exception as e:
        st.error(str(e))
    
