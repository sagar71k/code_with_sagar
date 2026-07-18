import streamlit as st
from pathlib import Path

from resume_parser import parse_resume, final_score, read_resume

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")

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

    if job_description.strip() == "":
        st.error("Please paste the job description.")
        st.stop()

    # Save uploaded resume
    resume_path = Path(uploaded_file.name)

    with open(resume_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        with st.spinner("Analyzing Resume..."):

            # Read Resume
            resume_text = read_resume(resume_path)

            # Parse Resume
            candidate = parse_resume(resume_text)

            # Calculate Score
            result = final_score(job_description, candidate)

        st.success("Analysis Completed ✅")

        st.subheader("👤 Candidate Details")
        st.json(candidate.model_dump())

        st.subheader("📊 Final Result")
        st.json(result.model_dump())

    except Exception as e:
        st.error(str(e))