from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .models import AnalysisResponse
from .parser import extract_text_from_pdf, extract_text_from_docx, parse_resume_text
from .analyzer import analyze_resume

app = FastAPI(title="AI Resume Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_RESUME_TEXT = """AMRUTH C K
Bengaluru, India · amruth@example.com · +91 98765 43210 · linkedin.com/in/amruthck

EXPERIENCE
Frontend Engineering Intern — Studio X (Jan 2024 – Present)
• Built responsive dashboard components in React and Vanilla CSS, reducing bundle size by 35%.
• Worked with the design team on UI improvements and feature rollout across 4 client applications.
• Implemented client-side caching mechanisms that accelerated initial dashboard load time by 40%.
• Assisted in code reviews and sprint planning for the frontend team.

PROJECTS
Personal Portfolio & Design System — React, CSS, Three.js
• Engineered interactive 3D portfolio experience with procedural shaders and WebGL canvas.
• Cut initial page load time 40% on main app webapp by implementing lazy loading and asset compression.
• Authored comprehensive design system guidelines adopted across 3 collaborative projects.

SKILLS
• Languages & Frameworks: JavaScript, TypeScript, React, HTML5, CSS3, Python, Node.js
• Tools & Methodologies: Git, Vite, TailwindCSS, Figma, REST APIs, Agile Development
• Core Competencies: Responsive Design, Performance Optimization, State Management

EDUCATION
Bachelor of Technology in Computer Science & Engineering
Visvesvaraya Technological University, Belagavi (2021 – 2025)
"""


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "AI Resume Analyzer"}


@app.get("/api/sample", response_model=AnalysisResponse)
async def get_sample():
    doc = parse_resume_text(SAMPLE_RESUME_TEXT)
    sample_jd = """Senior Frontend Engineer Requirements:
Looking for strong React and TypeScript experience. Must have demonstrated expertise in automated testing (Jest, Cypress), CI/CD pipelines, state management, and quantifiable performance optimization."""
    return await analyze_resume(doc, sample_jd)


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    raw_text = ""
    if file and file.filename:
        content = await file.read()
        filename_lower = file.filename.lower()
        if filename_lower.endswith(".pdf"):
            try:
                raw_text = extract_text_from_pdf(content)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Couldn't parse PDF: {str(e)}")
        elif filename_lower.endswith(".docx"):
            try:
                raw_text = extract_text_from_docx(content)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Couldn't parse DOCX: {str(e)}")
        else:
            try:
                raw_text = content.decode("utf-8")
            except Exception:
                raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, DOCX, or text file.")

    if not raw_text and text:
        raw_text = text.strip()

    if not raw_text:
        raise HTTPException(
            status_code=400,
            detail="Couldn't read that file — try a text-based PDF or DOCX (scanned images aren't supported yet)."
        )

    doc = parse_resume_text(raw_text)
    return await analyze_resume(doc, job_description)
