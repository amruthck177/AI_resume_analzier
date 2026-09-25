# AI Resume Analyzer — Design System Specification

> **Project ID**: `4584011876220879738`  
> **Source Platform**: Google Stitch  
> **Core Concept**: Editorial Manuscript Review ("The Meticulous Proofreader")

---

## 1. Executive Summary & Design Philosophy

The **AI Resume Analyzer** is an intentional departure from generic marketing-style dashboards, bloated analytics widgets, and card-shadow-heavy SaaS templates.

Instead, it treats a candidate's resume like a **manuscript under review**. Feedback lives in the **margin, directly adjacent to the exact line or bullet point it critiques**, mirroring the physical experience of a senior editor annotating a proof with red and amber pens.

### Guiding Principles
- **No Score Without a Next Step**: Every flagged item clearly describes the actionable correction.
- **Direct Anchor Proximity**: Margin annotations align vertically with the exact bullet or heading they analyze.
- **Print-Like Restraint**: Rules, borders, and generous whitespace provide structure—no heavy gradient cards or drop-shadow chrome.
- **Document as Hero**: The resume remains central, crisp, and legible at all times without modal overlays or distracting popups.

---

## 2. Color Palette & Tokens

The color system leans into a quiet, focused "editorial reading room" atmosphere. The paper background is softer than harsh white, ink is dark slate rather than pitch black, and annotation flags are deeply saturated to remain readable as small text against paper.

| Token | Hex | Role & Usage | Sample |
| :--- | :--- | :--- | :--- |
| `paper` | `#F1F2EE` | Primary app & canvas background | Subtle warm grey-white |
| `ink` | `#1B1D22` | Primary body typography, document headings | Deep near-black slate |
| `ink-soft` | `#5B5F66` | Secondary labels, metadata, muted dates | Muted charcoal |
| `rule` | `#D6D7D1` | Structural hairline borders, connecting guide lines | Quiet divider grey |
| `flag-amber` | `#9C6B14` | Formatting, layout issues, and ATS parse warnings | Deep editorial amber |
| `flag-red` | `#8C3230` | Skill gaps, missing JD requirements, critical flaws | Crimson markup red |
| `flag-green` | `#33593C` | High-impact bullets, quantified achievements, strengths | Sage proofreader green |

### Flag Accessibility & Styling Rules
- **Non-Color Reliance**: Every flag token is paired with an explicit icon/symbol (`⚠`, `✗`, `✓`) and clear descriptive copy.
- **Border Treatment**: Notes in the margin do not use colored background boxes. Instead, they use a **2px solid left border** in the respective flag color. This maintains legibility even when several notes stack closely.

---

## 3. Typography Hierarchy

The system establishes a clean distinction between the **Subject Document** and the **Review Tool Chrome**.

```
Document Content (Resume)  ───►  Source Serif 4  (Literary, authoritative, editorial)
UI Chrome & Margin Notes   ───►  IBM Plex Mono   (Precision, tabular numbers, proofreader notes)
```

### Type Specs

| Element | Font Family | Size | Weight | Line Height | Letter Spacing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Score Header** | `IBM Plex Mono` | `28px` | `600` (SemiBold) | `1.2` | `-0.02em` |
| **Score Metric Labels** | `IBM Plex Mono` | `13px` | `500` (Medium) | `1.4` | `0.05em` (Caps) |
| **Document Candidate Name** | `Source Serif 4` | `24px` | `700` (Bold) | `1.2` | `0.08em` (Caps) |
| **Document Section Headings** | `Source Serif 4` | `15px` | `600` (SemiBold) | `1.3` | `0.06em` (Caps) |
| **Document Body & Bullets** | `Source Serif 4` | `17px` | `400` (Regular) | `1.6` | `normal` |
| **Document Metadata** | `IBM Plex Mono` | `13px` | `400` (Regular) | `1.4` | `normal` |
| **Margin Annotation Label** | `IBM Plex Mono` | `13px` | `600` (SemiBold) | `1.3` | `normal` |
| **Margin Annotation Fix** | `IBM Plex Mono` | `14px` | `400` (Regular) | `1.5` | `normal` |

- **Line Length Budget**: Document column text is capped around **68 characters per line** for optimal reading speed.

---

## 4. Spacing & Spatial Layout

- **Base Spacing Grid**: `8px` unit (`8px`, `16px`, `24px`, `32px`, `48px`, `64px`).
- **Section Breaks**: `32px` vertical margin between document sections, reflecting standard printed resume layouts.
- **Annotation Margin Width**: Fixed `280px` desktop margin column.
- **Connecting Guide Lines**: `1px` horizontal rule (`#D6D7D1`) extending from the document anchor point directly to the margin note.

---

## 5. Screen Wireframes & States

### 5.1 Upload Screen (Pre-Analysis State)
Single centered column on paper background. Only screen where the document is absent.

```
┌────────────────────────────────────────────────────────┐
│  AI Resume Analyzer                                    │
│                                                        │
│   ┌────────────────────────────────────────────────┐   │
│   │                                                │   │
│   │            Drop your resume here               │   │
│   │      PDF or DOCX  ·  or paste text below       │   │
│   │                                                │   │
│   └────────────────────────────────────────────────┘   │
│                                                        │
│   Job Description (Optional)                           │
│   ┌────────────────────────────────────────────────┐   │
│   │ Paste target JD to get skill-gap & match marks │   │
│   └────────────────────────────────────────────────┘   │
│                                                        │
│                                   [ Analyze Resume → ] │
└────────────────────────────────────────────────────────┘
```

### 5.2 Results Screen (Primary Split-View)
Two-column split view with a sticky header.
- **Left Column**: Cleanly formatted, parsed resume document (`Source Serif 4`).
- **Right Column**: Vertical annotation margin (`IBM Plex Mono`) pinned to target lines.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Overall: 74/100  │  General: 80  │  ATS: 65  │  JD Match: 71  │  Gap: 72│
├────────────────────────────────────────┬────────────────────────────────┤
│ AMRUTH C K                             │                                │
│ Bengaluru, India · amruth@example.com  │                                │
│                                        │                                │
│ EXPERIENCE                             │ ⚠ Two-column layout under this │
│ ── Frontend Intern, Studio X ──        │   section breaks ATS parsers.  │
│ • Built dashboard components           │   → Switch to single column.   │
│                                        │                                │
│ • Worked with the design team on UI ◄──┼── ⚠ "Worked with… on" is       │
│   improvements and feature rollout     │   passive. Try: "Shipped 6 UI  │
│                                        │   updates with design".        │
│                                        │                                │
│ PROJECTS                               │ ✓ Strong: Quantified impact    │
│ • Cut load time 40% on main app webapp │   clearly stated.              │
│                                        │                                │
│ SKILLS                                 │ ✗ Missing from JD:             │
│ React, Tailwind, Git                   │   TypeScript, Automated Tests  │
└────────────────────────────────────────┴────────────────────────────────┘
```

### 5.3 Loading State (Category Progress)
Avoids generic spinner loops. Displays sequential validation steps:
```
[✓] Parsing document structure & typography
[✓] Evaluating general clarity & syntax
[●] Running ATS parse & readability check...
[○] Comparing skills against Job Description
```

### 5.4 Error State
Direct, non-apologetic feedback with one clear recovery action:
> *"Couldn't read that file — try a text-based PDF or DOCX (scanned images aren't supported yet)."*  
> `[ Choose Another File ]`

---

## 6. Component Inventory

| Component | Responsibility | Props / Key Interfaces |
| :--- | :--- | :--- |
| `UploadDropzone` | Handles drag-and-drop file upload (PDF/DOCX) or plain text paste | `onFileSelect(file)`, `onTextPaste(text)` |
| `JDInput` | Expandable textarea for optional job description matching | `value`, `onChange(jdText)` |
| `ScoreHeader` | Sticky top ribbon showing overall score and category breakdown | `scores: { overall, general, ats, jdMatch, gap }` |
| `ResumeDocument` | Renders parsed resume with distinct section markers & anchors | `documentData`, `activeAnchorId`, `onAnchorHover()` |
| `AnnotationMargin` | Container positioning notes alongside corresponding anchor coordinates | `annotations`, `activeAnchorId` |
| `AnnotationNote` | Single editorial annotation card with icon, rule border, and recommendation | `flagType: 'amber'|'red'|'green'`, `symbol`, `label`, `fixText`, `anchorId` |
| `AnalysisProgress` | 4-step progressive disclosure loading indicator | `currentStep: 1..4`, `stepsList` |
| `ErrorNotice` | Contextual recovery prompt | `message`, `recoveryActionLabel`, `onRetry()` |

---

## 7. Responsive Behavior

- **Desktop (≥ 800px)**:
  - Document and Annotation Margin sit side-by-side.
  - Horizontal guide lines connect line anchors to margin notes.
- **Mobile & Tablet (< 800px)**:
  - Margin column collapses.
  - Annotations render inline directly beneath their referenced bullet or line.
  - Preserves the same 2px colored left-border and monospace styling for consistency.

---

## 8. Accessibility Requirements (WCAG AA)
- **Symbol + Text**: Flag categories use distinct visual glyphs (`⚠`, `✗`, `✓`) alongside high-contrast text labels.
- **Keyboard Traversal**: Users can `Tab` through each flagged anchor in the document, which automatically highlights and scrolls the associated note into focus.
- **Reduced Motion**: Loading checklist ticks state changes immediately when `prefers-reduced-motion: reduce` is active.
