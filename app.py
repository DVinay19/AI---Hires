
from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from utils.analyzer import analyze_resume, extract_pdf
from utils.pdf_generator import analysis_pdf, resume_pdf


BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="AI Hires | Resume Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    css_path = BASE_DIR / "static" / "css" / "style.css"
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def render_resume(data):
    template_path = BASE_DIR / "templates" / "resume.html"
    template = template_path.read_text(encoding="utf-8")

    contact = " | ".join(
        value for value in [
            data.get("email", ""),
            data.get("phone", ""),
            data.get("location", ""),
            data.get("linkedin", ""),
            data.get("github", ""),
        ] if value.strip()
    )

    values = {
        "NAME": data.get("name", ""),
        "CONTACT": contact,
        "SUMMARY": data.get("summary", ""),
        "SKILLS": data.get("skills", ""),
        "EXPERIENCE": data.get("experience", ""),
        "PROJECTS": data.get("projects", ""),
        "EDUCATION": data.get("education", ""),
        "CERTIFICATIONS": data.get("certifications", ""),
    }

    for key, value in values.items():
        template = template.replace(
            "{{" + key + "}}",
            escape(str(value)).replace("\n", "&#10;"),
        )

    return template


load_css()

with st.sidebar:
    st.markdown("## 🎯 AI Hires")
    st.caption("SMART RESUME PLATFORM")
    st.divider()

    page = st.radio(
        "Workspace",
        ["Resume Analyzer", "AI Resume Builder"],
        label_visibility="visible",
    )

    st.divider()
    st.caption("Build a stronger resume. Target your next opportunity.")


st.markdown("""
<div class="hero">
    <h1>AI Hires</h1>
    <p>Analyze your resume. Improve your story. Get ready for your next role.</p>
</div>
""", unsafe_allow_html=True)


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


if page == "Resume Analyzer":
    st.markdown(
        '<div class="section-heading">Resume Analyzer</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Compare your resume with a job description, discover skill gaps, "
        "and download a report."
    )

    left, right = st.columns(2, gap="large")

    with left:
        uploaded = st.file_uploader(
            "Upload resume PDF",
            type=["pdf"],
            key="analysis_pdf",
        )

        pasted_resume = st.text_area(
            "Or paste resume text",
            height=180,
            key="analysis_text",
            placeholder="Paste your resume text here...",
        )

        resume_text = pasted_resume.strip()

        if uploaded is not None:
            try:
                extracted = extract_pdf(uploaded)
                if extracted:
                    resume_text = extracted
                    st.success(
                        f"PDF loaded · {len(extracted.split())} words"
                    )
                else:
                    st.warning(
                        "No selectable text found. Try a text-based PDF "
                        "or paste the resume text."
                    )
            except Exception as exc:
                st.error(f"Could not read the PDF: {exc}")

    with right:
        job_title = st.text_input(
            "Target job title",
            value="Python Developer",
            key="analysis_job_title",
        )

        job_description = st.text_area(
            "Job description",
            height=250,
            key="analysis_job_description",
            placeholder="Paste the target job description...",
        )

    if st.button(
        "Analyze Resume →",
        type="primary",
        use_container_width=True,
    ):
        try:
            result = analyze_resume(
                resume_text,
                job_description,
                job_title,
            )
            st.session_state.analysis_result = result
            st.success("Resume analysis completed.")
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")

    result = st.session_state.analysis_result

    if result:
        st.divider()
        st.markdown(
            '<div class="section-heading">Analysis Overview</div>',
            unsafe_allow_html=True,
        )

        columns = st.columns(4)
        metrics = [
            ("MATCH ESTIMATE", f'{result["overall"]}%'),
            ("SKILLS MATCHED", str(len(result["matched"]))),
            ("SKILL GAPS", str(len(result["missing"]))),
            ("RESUME WORDS", str(result["resume_words"])),
        ]

        for column, (label, value) in zip(columns, metrics):
            with column:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">{label}</div>'
                    f'<div class="metric-value">{value}</div></div>',
                    unsafe_allow_html=True,
                )

        chart_col, detail_col = st.columns(2, gap="large")

        with chart_col:
            st.markdown("#### Score breakdown")
            st.bar_chart({
                "Score (%)": {
                    "Skill coverage": result["skill_score"],
                    "Text similarity": result["similarity"],
                    "Resume sections": result["section_score"],
                }
            }, horizontal=True)

        with detail_col:
            st.markdown("#### Skills found")
            st.write("**Matched skills**")
            if result["matched"]:
                st.success(", ".join(result["matched"]))
            else:
                st.write("No matching skills detected.")

            st.write("**Missing or undetected skills**")
            if result["missing"]:
                st.warning(", ".join(result["missing"]))
            else:
                st.write("No gaps detected in recognized job skills.")

            st.write("**Additional skills**")
            st.write(", ".join(result["additional"]) or "None detected.")

        st.markdown("#### Recommended improvements")
        for index, suggestion in enumerate(
            result["suggestions"], start=1
        ):
            st.write(f"{index}. {suggestion}")

        st.caption(
            "Match scores are estimates based on keyword coverage, text "
            "similarity and resume sections. They are not official ATS scores "
            "or predictions of hiring outcomes."
        )

        st.download_button(
            "Download Analysis PDF",
            data=analysis_pdf(result),
            file_name="AI_Hires_Analysis_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


elif page == "AI Resume Builder":
    st.markdown(
        '<div class="section-heading">AI Resume Builder</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Create a job-targeted resume using your genuine skills, "
        "education, projects and experience."
    )

    with st.form("resume_builder_form"):
        st.markdown("#### Personal details")

        name = st.text_input("Full name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        location = st.text_input("City / Location")
        linkedin = st.text_input("LinkedIn URL")
        github = st.text_input("GitHub URL")

        st.markdown("#### Target job")

        target_role = st.text_input(
            "Target role",
            value="Python Developer",
        )
        target_description = st.text_area(
            "Job description",
            height=160,
            placeholder="Paste the job description to tailor your resume...",
        )

        st.markdown("#### Your professional profile")

        summary = st.text_area(
            "Professional summary",
            height=100,
            placeholder="Describe your real background and career goals...",
        )
        skills = st.text_area(
            "Skills",
            height=90,
            placeholder="Python, SQL, Git, Flask...",
        )
        projects = st.text_area(
            "Projects",
            height=130,
            placeholder="Project name, technologies, your contribution and outcomes...",
        )
        experience = st.text_area(
            "Work experience / internships",
            height=120,
            placeholder="Role, organization, dates and actual responsibilities...",
        )
        education = st.text_area(
            "Education",
            height=100,
            placeholder="Degree, institution, graduation year...",
        )
        certifications = st.text_area(
            "Certifications",
            height=80,
            placeholder="Relevant completed certifications...",
        )

        submitted = st.form_submit_button(
            "Generate Resume Preview →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        elif not any([
            summary.strip(),
            skills.strip(),
            projects.strip(),
            experience.strip(),
            education.strip(),
        ]):
            st.error(
                "Enter at least one real section of your background "
                "before generating a resume."
            )
        else:
            data = {
                "name": name.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
                "location": location.strip(),
                "linkedin": linkedin.strip(),
                "github": github.strip(),
                "target_role": target_role.strip(),
                "target_description": target_description.strip(),
                "summary": summary.strip(),
                "skills": skills.strip(),
                "projects": projects.strip(),
                "experience": experience.strip(),
                "education": education.strip(),
                "certifications": certifications.strip(),
            }

            # Generate suggestions only from the supplied job description.
            if data["target_description"]:
                from utils.analyzer import detect_skills

                job_skills = detect_skills(data["target_description"])
                profile_text = " ".join([
                    data["summary"],
                    data["skills"],
                    data["projects"],
                    data["experience"],
                    data["education"],
                    data["certifications"],
                ])
                profile_skills = detect_skills(profile_text)
                gaps = [
                    skill for skill in job_skills
                    if skill not in profile_skills
                ]
                data["job_skill_gaps"] = gaps
            else:
                data["job_skill_gaps"] = []

            st.session_state.resume_data = data
            st.success("Resume preview generated.")

    data = st.session_state.get("resume_data")

    if data:
        st.divider()
        st.markdown(
            '<div class="section-heading">Resume Studio</div>',
            unsafe_allow_html=True,
        )

        if data["job_skill_gaps"]:
            st.warning(
                "Skills in the job description not found in your supplied "
                "profile: " + ", ".join(data["job_skill_gaps"])
                + ". Add them only if you genuinely have those skills."
            )

        preview_tab, edit_tab = st.tabs([
            "Live Preview",
            "Edit Resume",
        ])

        with preview_tab:
            html_document = render_resume(data)
            components.html(
                html_document,
                height=1050,
                scrolling=True,
            )

        with edit_tab:
            st.info(
                "Edit any field below. These changes update the resume "
                "preview and downloaded PDF."
            )

            editable_fields = [
                ("summary", "Professional summary"),
                ("skills", "Skills"),
                ("experience", "Experience"),
                ("projects", "Projects"),
                ("education", "Education"),
                ("certifications", "Certifications"),
            ]

            for key, label in editable_fields:
                data[key] = st.text_area(
                    label,
                    value=data.get(key, ""),
                    key=f"edit_{key}",
                )

            st.session_state.resume_data = data

        st.download_button(
            "Download Resume PDF",
            data=resume_pdf(data),
            file_name="AI_Hires_Resume.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.download_button(
            "Download Resume HTML",
            data=render_resume(data),
            file_name="AI_Hires_Resume.html",
            mime="text/html",
            use_container_width=True,
        )

        st.caption(
            "Generated locally using your supplied information and a "
            "rule-based template. Review all details before applying."
        )

st.markdown("---")
st.caption(
    f"AI Hires · Resume Studio · {datetime.now().year}"
)
