import os
import streamlit as st

from resume_parser import (
    read_resume,
    parse_resume,
    final_score,
)

# ----------------------------
# Streamlit Config
# ----------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")
st.write("Upload your Resume and paste the Job Description below.")

# ----------------------------
# Resume Upload
# ----------------------------

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

# ----------------------------
# Job Description
# ----------------------------

job_description = st.text_area(
    "Paste Job Description",
    height=250
)

# ----------------------------
# Analyze Button
# ----------------------------

if st.button("Analyze Resume"):

    if uploaded_file is None:
        st.error("Please upload a resume.")
        st.stop()

    if job_description.strip() == "":
        st.error("Please paste a Job Description.")
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

            # Read Resume
            resume_text = read_resume(resume_path)

            # Parse Resume
            candidate = parse_resume(resume_text)

            # Score Resume
            result = final_score(
                job_description,
                candidate
            )

        st.success("Analysis Completed Successfully ✅")

        st.divider()

        st.subheader("📊 Overall Score")

        st.progress(result.overall_score / 100)

        st.metric(
            "Overall Score",
            f"{result.overall_score}/100"
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Technical",
                result.technical_score
            )

            st.metric(
                "Education",
                result.education_score
            )

        with col2:

            st.metric(
                "Experience",
                result.experience_score
            )

            st.metric(
                "Projects",
                result.project_score
            )

        st.divider()

        st.subheader("❌ Missing Skills")

        if result.missing_skills:

            for skill in result.missing_skills:
                st.write("•", skill)

        else:
            st.success("No Missing Skills")

        st.divider()

        st.subheader("✅ Strengths")

        if result.strengths:

            for item in result.strengths:
                st.write("•", item)

        else:
            st.info("No strengths detected")

        st.divider()

        st.subheader("⚠️ Improvements")

        if result.improvements:

            for item in result.improvements:
                st.write("•", item)

        else:
            st.success("No Improvements Required")

        st.divider()

        st.subheader("📝 Verdict")

        st.success(result.verdict)

    except Exception as e:

        st.error(str(e))