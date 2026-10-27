
import re
from collections import Counter

import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript"],
    "C++": ["c++"],
    "SQL": ["sql", "mysql", "postgresql"],
    "HTML/CSS": ["html", "css"],
    "React": ["react", "reactjs"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Streamlit": ["streamlit"],
    "Machine Learning": ["machine learning", "scikit-learn", "sklearn"],
    "Deep Learning": ["deep learning", "pytorch", "tensorflow"],
    "Generative AI": ["generative ai", "genai", "llm", "llms"],
    "NLP": ["nlp", "natural language processing"],
    "RAG": ["rag", "retrieval augmented generation"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Data Visualization": ["plotly", "matplotlib", "power bi", "tableau"],
    "Git/GitHub": ["git", "github"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "REST APIs": ["rest api", "restful api"],
    "Linux": ["linux"],
    "Testing": ["pytest", "unit testing", "testing"],
    "Communication": ["communication", "teamwork"],
}

SECTION_ALIASES = {
    "education": ["education", "academic background", "qualification"],
    "skills": ["skills", "technical skills", "core competencies"],
    "projects": ["projects", "personal projects", "academic projects"],
    "experience": ["experience", "work experience", "professional experience"],
    "internship": ["internship", "internships"],
    "certifications": ["certifications", "certificates"],
}

ACTION_VERBS = [
    "built", "developed", "created", "implemented", "designed",
    "improved", "automated", "analyzed", "tested", "deployed",
    "managed", "maintained", "integrated", "led", "delivered",
]

RESUME_SIGNALS = [
    "developer", "engineer", "intern", "student", "graduate",
    "university", "college", "bachelor", "degree", "b.tech",
    "responsibilities", "achievements", "employment", "career objective",
    "professional summary", "technical skills", "work experience",
    "education", "projects", "certifications",
]


def extract_pdf(uploaded_file):
    """Extract selectable text from an uploaded PDF."""
    with fitz.open(
        stream=uploaded_file.getvalue(), filetype="pdf"
    ) as document:
        return "\n".join(page.get_text() for page in document).strip()


def detect_skills(text):
    """Detect skills using word-boundary-aware matching."""
    text = text.lower()
    found = []

    for skill, aliases in SKILLS.items():
        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            if re.search(pattern, text):
                found.append(skill)
                break

    return found


def validate_resume(resume_text):
    """Reject empty, random, or clearly non-resume input."""
    text = resume_text.strip()

    if not text:
        raise ValueError(
            "Enter your resume text or upload a text-based PDF."
        )

    words = re.findall(r"\b[\w+#.-]+\b", text.lower())

    if len(words) < 15:
        raise ValueError(
            "Your resume is too short. Provide at least 15 words "
            "of meaningful resume content."
        )

    # Repeated words alone should not count as meaningful content.
    unique_words = set(words)
    if len(unique_words) < 8:
        raise ValueError(
            "Your text contains too little variety. Enter real resume "
            "details such as skills, education, projects, or experience."
        )

    # Require evidence that the input is actually about a candidate.
    skills = detect_skills(text)
    lower_text = text.lower()

    has_resume_signal = any(
        re.search(r"(?<!\w)" + re.escape(signal) + r"(?!\w)", lower_text)
        for signal in RESUME_SIGNALS
    )

    has_action_verb = any(
        re.search(r"\b" + re.escape(verb) + r"\b", lower_text)
        for verb in ACTION_VERBS
    )

    has_section = any(
        re.search(
            r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
            lower_text,
        )
        for aliases in SECTION_ALIASES.values()
        for alias in aliases
    )

    # A technical resume should show skills or resume-specific content,
    # rather than simply containing an arbitrary block of text.
    if not (has_resume_signal or has_section or (skills and has_action_verb)):
        raise ValueError(
            "This doesn't look like resume content. Add relevant details "
            "about your skills, education, projects, or work experience."
        )

    if len(words) >= 30 and len(unique_words) / len(words) < 0.15:
        raise ValueError(
            "Your text repeats the same words too often. Please provide "
            "clear, meaningful resume details."
        )


def validate_job_description(job_text):
    """Check that a real job description was supplied."""
    if not job_text.strip():
        raise ValueError("Please provide a job description.")

    words = re.findall(r"\b[\w+#.-]+\b", job_text.lower())

    if len(words) < 15 or len(set(words)) < 8:
        raise ValueError(
            "The job description is too short or repetitive. "
            "Paste the responsibilities and required skills for the role."
        )

    if not detect_skills(job_text) and not re.search(
        r"\b(developer|engineer|analyst|designer|manager|intern|"
        r"responsibilities|requirements|qualifications)\b",
        job_text,
        re.I,
    ):
        raise ValueError(
            "Please provide a relevant job description with a job role, "
            "responsibilities, or required skills."
        )


def calculate_similarity(resume, job):
    """Calculate text overlap, not a prediction of hiring success."""
    if not resume.strip() or not job.strip():
        return 0

    try:
        matrix = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
        ).fit_transform([resume, job])

        score = cosine_similarity(
            matrix[0:1], matrix[1:2]
        )[0][0]

        return round(float(score) * 100)
    except ValueError:
        return 0


def analyze_resume(resume_text, job_text, job_title="Target Role"):
    validate_resume(resume_text)
    validate_job_description(job_text)

    resume_skills = detect_skills(resume_text)
    job_skills = detect_skills(job_text)

    matched = [skill for skill in job_skills if skill in resume_skills]
    missing = [skill for skill in job_skills if skill not in resume_skills]
    additional = [skill for skill in resume_skills if skill not in job_skills]

    skill_score = (
        round(len(matched) / len(job_skills) * 100)
        if job_skills else 0
    )

    similarity = calculate_similarity(resume_text, job_text)

    lower_resume = resume_text.lower()
    present_sections = []

    for section, aliases in SECTION_ALIASES.items():
        if any(
            re.search(
                r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
                lower_resume,
            )
            for alias in aliases
        ):
            present_sections.append(section)

    # Reward meaningful resume structure, not arbitrary keywords alone.
    section_score = round(
        len(present_sections) / len(SECTION_ALIASES) * 100
    )

    overall = round(
        0.50 * skill_score
        + 0.35 * similarity
        + 0.15 * section_score
    )

    suggestions = []

    if "education" not in present_sections:
        suggestions.append(
            "Add an Education section with your actual qualification."
        )

    if "skills" not in present_sections and not resume_skills:
        suggestions.append(
            "Add a clearly labeled Skills section with relevant, truthful skills."
        )

    if "projects" not in present_sections:
        suggestions.append(
            "Include relevant projects and explain your personal contribution."
        )

    if "experience" not in present_sections and "internship" not in present_sections:
        suggestions.append(
            "Add relevant work or internship experience if you have it. "
            "Otherwise, highlight academic or personal projects."
        )

    if missing:
        suggestions.append(
            "Review these skills from the job description: "
            + ", ".join(missing[:10])
            + ". Include them only if you genuinely have those skills."
        )

    if not any(
        re.search(r"\b" + re.escape(verb) + r"\b", lower_resume)
        for verb in ACTION_VERBS
    ):
        suggestions.append(
            "Describe what you actually did using clear action verbs "
            "such as developed, tested, or implemented."
        )

    if not suggestions:
        suggestions.append(
            "Review your strongest evidence against the role and tailor "
            "your project descriptions to the job requirements."
        )

    return {
        "job_title": job_title,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched": matched,
        "missing": missing,
        "additional": additional,
        "skill_score": skill_score,
        "similarity": similarity,
        "section_score": section_score,
        "overall": overall,
        "suggestions": suggestions,
        "resume_words": len(resume_text.split()),
        "present_sections": present_sections,
    }
