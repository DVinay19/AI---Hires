#  AI Hires — Resume Analyzer & Resume Studio

<p align="center">
  <strong>Build Better Resumes. Discover Better Opportunities.</strong>
  <br/>
  An intelligent resume analysis and creation platform that helps users evaluate their resumes against job descriptions, identify skill gaps, and build professional, tailored resumes.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Active%20Development-success?style=for-the-badge" />
</p>

---

##  Overview

**AI Hires** is a Python-based resume analysis and resume-building platform designed to make the job application process more structured and accessible.

The application allows users to upload an existing resume or paste resume content, compare it against a target job description, identify matching skills and potential skill gaps, and generate an analysis report.

It also provides a resume-building workspace where users can enter their professional information, preview a structured resume, edit its sections, and export the finished document.

AI Hires brings resume evaluation and resume creation together in one application.

##  Key Features

| Feature | Description |
|---|---|
|  Resume Upload | Upload text-based PDF resumes |
|  Resume Input | Paste resume content directly |
|  Job Matching | Compare resume content against job descriptions |
|  Skill Extraction | Identify recognized skills in resume and job requirements |
|  Gap Analysis | Highlight skills mentioned in the job description but missing from the resume |
|  Similarity Score | Calculate text similarity using TF-IDF and cosine similarity |
|  PDF Reports | Generate downloadable resume analysis reports |
|  Resume Builder | Create structured resumes using personal and professional information |
|  Resume Preview | Preview resumes using HTML and CSS |
|  Resume Editing | Modify resume sections before exporting |
|  Multiple Exports | Download completed resumes as PDF or HTML |

##  Technology Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| Web Framework | Streamlit |
| PDF Extraction | PyMuPDF |
| Text Analysis | scikit-learn |
| Similarity Algorithm | TF-IDF + Cosine Similarity |
| PDF Generation | ReportLab |
| Frontend | HTML5 and CSS3 |
| Styling | Custom CSS |

##  How It Works

```text
          User Opens AI Hires
                  |
          ┌───────┴────────┐
          ▼                ▼
    Resume Analyzer    Resume Studio
          |                |
     Upload Resume     Enter Details
          |                |
     Add Job Posting   Select Template
          |                |
     Extract Text      Build Resume
          |                |
     Extract Skills    HTML/CSS Preview
          |                |
     TF-IDF Matching   Edit Sections
          |                |
     Skill Gap Analysis    |
          |                |
     Generate Report       |
          |                |
          ▼                ▼
       PDF Report      PDF / HTML Export
```

##  Getting Started

Follow these instructions to run AI Hires locally.

### Prerequisites

- Python 3.10 or later
- pip
- Git

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate into the project directory:

```bash
cd AI-Hires
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the Application

```bash
python -m streamlit run app.py
```

### 6. Open in Your Browser

Visit:

**http://localhost:8501**

The AI Hires workspace will be available in your browser.

##  Project Structure

```text
AI-Hires/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   └── css/
│       └── style.css
│
├── templates/
│   └── resume.html
│
└── utils/
    ├── __init__.py
    ├── analyzer.py
    └── pdf_generator.py
```

##  Resume Matching Methodology

AI Hires uses a combination of text-processing and statistical techniques to compare resume content with job descriptions.

**1. Text Extraction**

Resume content is extracted from text-based PDF documents using PyMuPDF.

**2. Skill Extraction**

Recognized skills are identified from resume content and job descriptions using keyword-based extraction.

**3. TF-IDF Vectorization**

The text is converted into numerical representations using Term Frequency–Inverse Document Frequency.

**4. Cosine Similarity**

Cosine similarity measures how closely the resume text matches the job description.

**5. Skill Gap Identification**

Recognized skills required by the job description but not detected in the resume are highlighted for review.

**Important:** The similarity score is a heuristic text-matching measure. It is not an official ATS score, a hiring probability, or a guarantee of interview selection. The current implementation does not use a generative AI model.

##  Privacy & Data Handling

Resumes contain personal and professional information. Handle them carefully.

- Use sample resumes during development and testing.
- Avoid committing personal resumes or sensitive information to GitHub.
- Review file handling and temporary storage behaviour.
- Implement appropriate access controls before public deployment.
- Review logging and data-retention practices.
- Use secure deployment and storage configurations.

##  Future Enhancements

Potential improvements for future versions:

- **AI-Assisted Resume Rewriting:** Optional LLM integration for improving resume descriptions.
- **Advanced Skill Analysis:** Better skill recognition and contextual matching.
- **Multiple Resume Templates:** Additional professional layouts and customization options.
- **ATS-Oriented Recommendations:** Structured suggestions for improving resume readability and keyword coverage.
- **Automated Testing:** Expanded test coverage and improved error handling.
- **Cloud Deployment:** Secure access to resume tools across devices.
- **Export Improvements:** Additional document formats and layout customization.

##  Project Objectives

- Simplify resume evaluation against job descriptions.
- Help users identify relevant skills and potential skill gaps.
- Provide a structured resume-building experience.
- Apply NLP techniques to practical text analysis.
- Generate professional, downloadable resume documents.
- Demonstrate Python, Streamlit, machine learning libraries and frontend development skills.

##  License

Add a `LICENSE` file to specify the terms under which this project can be used, modified and distributed.

---

<p align="center">
  <strong> AI Hires</strong>
  <br/>
  <em>Your Skills. Your Story. Your Next Opportunity.</em>
  <br/><br/>
  Built with Python, Streamlit and scikit-learn.
</p>
