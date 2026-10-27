
const $ = (id) => document.getElementById(id);

let latestAnalysis = null;
let latestResume = null;

async function requestDownload(url, data, filename) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Download failed.");
  }

  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
}

function showError(id, message) {
  const element = $(id);
  if (!element) return;

  element.textContent = message;
  element.classList.remove("hidden");
}

function hideError(id) {
  const element = $(id);
  if (element) element.classList.add("hidden");
}

function showPage(page) {
  const analyzer = page === "analyzer";

  $("analyzer-page").classList.toggle("hidden", !analyzer);
  $("builder-page").classList.toggle("hidden", analyzer);

  document.querySelectorAll(".nav-item").forEach(button => {
    button.classList.toggle("active", button.dataset.page === page);
  });

  $("crumb").textContent = analyzer ? "Resume Analyzer" : "Resume Studio";
  $("page-title").textContent = analyzer
    ? "Make your next move count."
    : "Build a resume that tells your story.";
  $("page-subtitle").textContent = analyzer
    ? "Understand your resume. Find the gaps. Move forward with clarity."
    : "Organize your experience into a clear, job-focused resume.";
  $("heading-mark").textContent = analyzer ? "AH / 01" : "AH / 02";
}

document.querySelectorAll(".nav-item").forEach(button => {
  button.addEventListener("click", () => showPage(button.dataset.page));
});

 const resumeFileInput = $("resume_pdf");
const uploadZone = document.querySelector(".upload-zone");

resumeFileInput.addEventListener("change", event => {
  const file = event.target.files[0];

  $("file-name").textContent = file
    ? file.name
    : "Choose a resume PDF";

  if (file && file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")) {
    showError("analysis-error", "Please choose a PDF file.");
    resumeFileInput.value = "";
    $("file-name").textContent = "Choose a resume PDF";
    return;
  }

  hideError("analysis-error");
});

// Allow keyboard users to open the file picker.
if (uploadZone) {
  uploadZone.setAttribute("tabindex", "0");
  uploadZone.setAttribute("role", "button");

  uploadZone.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      resumeFileInput.click();
    }
  });
}

function renderTags(id, values, missing = false) {
  const container = $(id);
  container.replaceChildren();

  if (!values || !values.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = "No skills detected.";
    container.appendChild(empty);
    return;
  }

  values.forEach(value => {
    const tag = document.createElement("span");
    tag.className = missing ? "tag missing" : "tag";
    tag.textContent = value;
    container.appendChild(tag);
  });
}

$("analysis-form").addEventListener("submit", async event => {
  event.preventDefault();

  hideError("analysis-error");
  $("results").classList.add("hidden");
  $("analysis-loading").classList.remove("hidden");
  $("analyze-button").disabled = true;

  try {
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: form
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Analysis failed.");

    latestAnalysis = result;

    $("overall").textContent = `${result.overall}%`;
    $("skill-score").textContent = `${result.skill_score}%`;
    $("similarity").textContent = `${result.similarity}%`;
    $("word-count").textContent = result.resume_words.toLocaleString();

    renderTags("matched", result.matched);
    renderTags("missing", result.missing, true);

    const list = $("suggestions");
    list.replaceChildren();

    result.suggestions.forEach(suggestion => {
      const item = document.createElement("li");
      item.textContent = suggestion;
      list.appendChild(item);
    });

    $("results").classList.remove("hidden");
    $("results").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showError("analysis-error", error.message);
  } finally {
    $("analysis-loading").classList.add("hidden");
    $("analyze-button").disabled = false;
  }
});

$("download-analysis").addEventListener("click", async () => {
  if (!latestAnalysis) return;

  try {
    await requestDownload(
      "/api/analysis-pdf",
      latestAnalysis,
      "AI_Hires_Analysis_Report.pdf"
    );
  } catch (error) {
    showError("analysis-error", error.message);
  }
});

function collectResume() {
  const fields = [
    "name", "email", "phone", "location", "linkedin", "github",
    "summary", "skills", "experience", "projects",
    "education", "certifications", "target_role", "target_description"
  ];

  return Object.fromEntries(
    fields.map(id => [id, $(id).value.trim()])
  );
}

function addResumeSection(container, title, value) {
  if (!value) return;

  const section = document.createElement("section");
  section.className = "resume-section";

  const heading = document.createElement("h3");
  heading.textContent = title;

  const content = document.createElement("p");
  content.textContent = value;

  section.append(heading, content);
  container.appendChild(section);
}

/* ---------- Resume Studio content validation ---------- */

const BAD_PHRASES = [
  "fuck",
  "shit",
  "motherfucker",
  "bitch",
  "placeholder text",
  "lorem ipsum",
  "replace this section",
  "insert your details",
  "add your actual",
  "your name here",
  "sample project experience",
  "todo:",
  "xxx"
];

const SECTION_LABELS = {
  summary: "Professional summary",
  skills: "Skills",
  experience: "Experience",
  projects: "Projects",
  education: "Education",
  certifications: "Certifications"
};

function validateResumeContent(data) {
  const errors = [];
  const contentFields = [
    "summary", "skills", "experience",
    "projects", "education", "certifications"
  ];

  const populated = contentFields.filter(key => data[key]);

  if (!data.name) {
    errors.push("Enter your full name.");
  } else if (data.name.length < 2 || /\d/.test(data.name)) {
    errors.push("Enter a valid name without numbers.");
  }

  if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push("Check the email address format.");
  }

  if (data.phone && !/^[+\d\s().-]{7,20}$/.test(data.phone)) {
    errors.push("Check the phone number format.");
  }

  if (!populated.length) {
    errors.push("Add at least one section describing your background.");
    return errors;
  }

  for (const key of populated) {
    const value = data[key];
    const lower = value.toLowerCase();

    const badPhrase = BAD_PHRASES.find(phrase =>
      new RegExp(
        `(^|[^a-z])${phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}([^a-z]|$)`,
        "i"
      ).test(lower)
    );

    if (badPhrase) {
      errors.push(
        `${SECTION_LABELS[key]} contains inappropriate or placeholder text. Remove "${badPhrase}" and enter genuine details.`
      );
      continue;
    }

    const words = value.match(/\b[\w+#.-]+\b/g) || [];
    const uniqueWords = new Set(words.map(word => word.toLowerCase()));

    if (words.length < 3 || uniqueWords.size < 3) {
      errors.push(
        `${SECTION_LABELS[key]} needs more meaningful detail. Please expand it.`
      );
    } else if (
      words.length >= 15 &&
      uniqueWords.size / words.length < 0.25
    ) {
      errors.push(
        `${SECTION_LABELS[key]} repeats words too often. Rewrite it clearly.`
      );
    }

    if (/https?:\/\/\S+/i.test(value) && key !== "projects") {
      // URLs may be valid in descriptions, so do not reject them automatically.
    }
  }

  return errors;
}

/* ---------- Resume preview ---------- */

function renderResume(data) {
  const preview = $("resume-preview");
  preview.replaceChildren();

  const name = document.createElement("h2");
  name.textContent = data.name;
  preview.appendChild(name);

  const contact = document.createElement("div");
  contact.className = "resume-contact";
  contact.textContent = [
    data.email,
    data.phone,
    data.location,
    data.linkedin,
    data.github
  ].filter(Boolean).join("  ·  ");

  preview.appendChild(contact);

  [
    ["Professional Summary", "summary"],
    ["Skills", "skills"],
    ["Experience", "experience"],
    ["Projects", "projects"],
    ["Education", "education"],
    ["Certifications", "certifications"]
  ].forEach(([title, key]) => {
    addResumeSection(preview, title, data[key]);
  });
}

function updateSkillGaps(data) {
  const panel = $("skill-gaps");
  panel.classList.add("hidden");
  panel.textContent = "";

  if (!data.target_description) return;

  const resumeText = [
    data.summary, data.skills, data.experience,
    data.projects, data.education, data.certifications
  ].join(" ").toLowerCase();

  const commonSkills = [
    "python", "java", "javascript", "sql", "html", "css",
    "react", "flask", "fastapi", "django", "streamlit",
    "machine learning", "docker", "aws", "git", "github",
    "rest api", "testing", "pandas", "numpy"
  ];

  const escapeRegex = text =>
    text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const missing = commonSkills.filter(skill => {
    const pattern = new RegExp(`\\b${escapeRegex(skill)}\\b`, "i");
    return pattern.test(data.target_description) && !pattern.test(resumeText);
  });

  if (missing.length) {
    panel.textContent =
      "Potential gaps to review: " + missing.join(", ") +
      ". Include a skill only if you genuinely have it.";
    panel.classList.remove("hidden");
  }
}

$("builder-form").addEventListener("submit", event => {
  event.preventDefault();
  hideError("builder-error");

  const data = collectResume();
  const errors = validateResumeContent(data);

  if (errors.length) {
    showError("builder-error", errors.join(" "));
    return;
  }

  // Only save or render after validation succeeds.
  latestResume = data;
  renderResume(data);
  updateSkillGaps(data);

  $("resume-preview").scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
});

$("download-resume").addEventListener("click", async () => {
  if (!latestResume) {
    showError("builder-error", "Update a valid resume preview first.");
    return;
  }

  try {
    await requestDownload(
      "/api/resume-pdf",
      latestResume,
      "AI_Hires_Resume.pdf"
    );
  } catch (error) {
    showError("builder-error", error.message);
  }
});

$("download-html").addEventListener("click", async () => {
  if (!latestResume) {
    showError("builder-error", "Update a valid resume preview first.");
    return;
  }

  try {
    await requestDownload(
      "/api/resume-html",
      latestResume,
      "AI_Hires_Resume.html"
    );
  } catch (error) {
    showError("builder-error", error.message);
  }
});
