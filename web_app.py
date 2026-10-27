
from io import BytesIO
from pathlib import Path

import fitz
from flask import Flask, jsonify, render_template, request, send_file

from utils.analyzer import analyze_resume
from utils.pdf_generator import analysis_pdf, resume_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


@app.get("/")
def home():
    return render_template("index.html")


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "File is too large. Maximum size is 8 MB."}), 413


@app.post("/api/analyze")
def analyze():
    resume_text = request.form.get("resume_text", "").strip()
    job_title = request.form.get("job_title", "Target Role").strip()
    job_description = request.form.get("job_description", "").strip()

    uploaded = request.files.get("resume_pdf")

    if uploaded and uploaded.filename:
        try:
            pdf_bytes = uploaded.read()
            with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
                resume_text = "\n".join(
                    page.get_text() for page in pdf
                ).strip()
        except Exception:
            return jsonify({"error": "Could not read this PDF."}), 400

    try:
        result = analyze_resume(resume_text, job_description, job_title)
        return jsonify(result)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("Resume analysis failed")
        return jsonify({"error": "Analysis failed. Check the supplied files and text."}), 500


@app.post("/api/analysis-pdf")
def download_analysis():
    result = request.get_json(silent=True)
    if not isinstance(result, dict) or "overall" not in result:
        return jsonify({"error": "Run an analysis first."}), 400

    pdf_bytes = analysis_pdf(result)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="AI_Hires_Analysis_Report.pdf",
    )


@app.post("/api/resume-pdf")
def download_resume():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data.get("name", "").strip():
        return jsonify({"error": "Enter your name before downloading."}), 400

    pdf_bytes = resume_pdf(data)
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="AI_Hires_Resume.pdf",
    )


@app.post("/api/resume-html")
def download_resume_html():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data.get("name", "").strip():
        return jsonify({"error": "Enter your name before downloading."}), 400

    html = render_template("resume.html", **{
        key: str(data.get(key, ""))
        for key in [
            "name", "email", "phone", "location", "linkedin", "github",
            "summary", "skills", "experience", "projects",
            "education", "certifications"
        ]
    })

    return send_file(
        BytesIO(html.encode("utf-8")),
        mimetype="text/html",
        as_attachment=True,
        download_name="AI_Hires_Resume.html",
    )



if __name__ == "__main__":
    import threading
    import webbrowser

    url = "http://127.0.0.1:5000"

    threading.Timer(
        1.0,
        lambda: webbrowser.open(url)
    ).start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

