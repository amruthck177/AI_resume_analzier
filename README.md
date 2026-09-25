# AI Resume Analyzer

An editorial-style AI resume analyzer — treats your resume like a manuscript under review. Feedback lives in the **margin**, anchored to the exact line it critiques.

## Architecture

```
AI_resume_analzier/
├── frontend/        # React + Vite  (http://localhost:5173)
├── backend/         # Python FastAPI (http://127.0.0.1:8000)
├── DESIGN.md        # Full design system spec
├── start_dev.js     # Single command to start both servers
└── package.json
```

## Design System (from DESIGN.md)

| Token | Hex | Role |
|---|---|---|
| `paper` | `#F1F2EE` | Background |
| `ink` | `#1B1D22` | Primary text |
| `flag-amber` | `#9C6B14` | Formatting / ATS warnings |
| `flag-red` | `#8C3230` | Skill gaps |
| `flag-green` | `#33593C` | Quantified strengths |

**Typography:** `Source Serif 4` (document) · `IBM Plex Mono` (UI, margins, scores)

## Quick Start

### 1. Backend (Python 3.13)

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend (Node.js)

```bash
cd frontend
npm install
npm run dev
```

### 3. Both at once (from project root)

```bash
npm install        # installs root package.json
node start_dev.js
```

## Optional: LLM-Powered Analysis

Set any of these environment variables to upgrade from the heuristic engine to LLM analysis:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Without an API key, the app runs a high-fidelity heuristic editorial engine.

## Screens

1. **Upload** — Drop PDF/DOCX or paste plain text; optional job description
2. **Loading** — 4-step sequential analysis checklist
3. **Results** — Sticky score ribbon + two-column manuscript layout with margin annotations
4. **Error** — Contextual recovery prompt

## Features

- ✅ PDF & DOCX parsing (`pypdf`, `python-docx`)
- ✅ Line-anchored margin annotations (⚠ amber, ✗ red, ✓ green)
- ✅ Scores: Overall, General, ATS, JD Match, Skill Gap
- ✅ Contextual fix suggestions per bullet/section
- ✅ JD-based skill gap detection
- ✅ Passive voice detection
- ✅ Responsive — mobile annotations collapse inline
- ✅ Keyboard accessible
