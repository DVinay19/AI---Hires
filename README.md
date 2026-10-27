
# AI Hires — Resume Analyzer & Resume Studio

AI Hires is a Python-based web application for analyzing resumes against job descriptions and building tailored, editable resumes.

## Features

- Upload text-based PDF resumes or paste resume text.
- Analyze resume and job-description similarity.
- Identify recognized matching skills and potential skill gaps.
- Generate an analysis report in PDF format.
- Build a structured resume using user-provided information.
- Preview a professional HTML/CSS resume.
- Edit resume sections before exporting.
- Download the finished resume as PDF or HTML.

## Technology Stack

- Python
- Streamlit
- PyMuPDF
- scikit-learn
- ReportLab
- HTML and CSS

## Installation

Install Python 3.10 or later.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the requirements:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python -m streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```text
AI-Hires/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/css/style.css
├── templates/resume.html
└── utils/
    ├── __init__.py
    ├── analyzer.py
    └── pdf_generator.py
```

## Matching Method

Resume matching uses keyword-based skill extraction and TF-IDF cosine similarity. The score is a heuristic estimate and is not an official ATS score or hiring prediction.

The initial resume builder uses user-provided content, an HTML template, and rule-based skill-gap suggestions. It does not currently use a generative AI model to rewrite resume content.

## Privacy

Use sample resumes during development. Review file handling, logging, and access controls before deploying the application publicly. Never publish private resumes, credentials, or personal data.

## Future Improvements

- Optional LLM integration for genuine AI-assisted rewriting.
- Automated tests and improved error handling.
- More resume templates and customization options.
- Deployment with appropriate privacy protections.
