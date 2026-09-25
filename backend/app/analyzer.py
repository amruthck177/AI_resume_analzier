import json
import os
import re
from typing import List, Optional, Tuple
import httpx
from .models import ParsedDocument, Annotation, Scores, AnalysisResponse


# ---------------------------------------------------------------------------
# Contextual suggestion engine – maps keywords in a bullet to specific advice
# ---------------------------------------------------------------------------

METRIC_CONTEXTS = [
    # (keyword_pattern, what_to_measure, metric_example)
    (r'\b(dashboard|panel|report|visualization)\b',
     "dashboard or data UI work",
     'e.g. "Reduced average time-to-insight from 4 min → 45 sec for 200 daily users."'),
    (r'\b(load time|performance|speed|latency|slow|fast|opti)\w*',
     "performance optimization",
     'e.g. "Cut p95 API latency from 1.8 s → 320 ms, improving throughput by 4×."'),
    (r'\b(component|ui|interface|design|frontend|react|vue|angular|svelte)\b',
     "frontend/UI component work",
     'e.g. "Shipped 12 reusable components adopted across 3 product teams, eliminating ~800 lines of duplicate code."'),
    (r'\b(auth|login|signup|onboarding|register)\w*',
     "authentication or onboarding flow",
     'e.g. "Streamlined signup flow from 6 steps → 3, lifting weekly sign-up conversion by 22%."'),
    (r'\b(api|endpoint|rest|graphql|webhook|integrat)\w*',
     "API or integration development",
     'e.g. "Built 8 REST endpoints handling 50 k+ req/day with < 200 ms p99 latency."'),
    (r'\b(database|sql|query|postgres|mysql|mongo|redis|cache)\w*',
     "database / caching work",
     'e.g. "Optimized 3 slow N+1 queries, reducing DB CPU load by 35% and saving $120/month."'),
    (r'\b(deploy|ci|cd|pipeline|docker|kubernetes|infra|devops|terraform)\w*',
     "deployment or DevOps work",
     'e.g. "Automated deployment pipeline from 45-min manual release → 8-min CI/CD, saving ~6 engineer-hours/week."'),
    (r'\b(test|coverage|unit|integration|e2e|cypress|jest|pytest)\w*',
     "testing or quality assurance",
     'e.g. "Raised test coverage from 42% → 91%, catching 15 regressions before production."'),
    (r'\b(bug|fix|patch|hotfix|issue|incident|debugging)\w*',
     "bug-fixing or incident resolution",
     'e.g. "Resolved 3 critical P0 bugs causing 4-hr outage, restoring service for 12 k active users."'),
    (r'\b(feature|product|ship|launch|release)\w*',
     "feature shipping or product work",
     'e.g. "Shipped dark-mode feature in 3-week sprint, adopted by 68% of users within 2 weeks of launch."'),
    (r'\b(team|cross.functional|collaborat|coordinat|mentor)\w*',
     "team or cross-functional collaboration",
     'e.g. "Coordinated with 3 squads (Design, Backend, QA) to deliver v2 milestone 1 week ahead of schedule."'),
    (r'\b(scrap|scrape|data|etl|pipeline|ingestion|migration)\w*',
     "data pipeline or ETL work",
     'e.g. "Built ingestion pipeline processing 2 M records/hour with < 0.01% error rate."'),
    (r'\b(mobile|app|android|ios|react native|flutter)\w*',
     "mobile app development",
     'e.g. "Reduced app startup time from 3.2 s → 1.1 s; improved App Store rating from 3.8 → 4.5 ★."'),
    (r'\b(ml|model|train|inference|accuracy|predict|classif)\w*',
     "machine learning or model development",
     'e.g. "Trained classifier achieving 94.2% accuracy on held-out test set, deployed to serve 50 k inferences/day."'),
    (r'\b(cost|saving|budget|efficiency|reduce cost|revenue)\w*',
     "cost reduction or efficiency gain",
     'e.g. "Renegotiated vendor contract, cutting monthly cloud spend by $2.4 k (18%)."'),
    (r'\b(mentor|review|onboard|train|teach|lead|managed)\w*',
     "leadership or people development",
     'e.g. "Mentored 2 junior engineers; both promoted within 6 months."'),
    (r'\b(website|landing|page|seo|conversion|traffic|click)\w*',
     "web presence or SEO/conversion work",
     'e.g. "Refactored landing page, improving Lighthouse score from 62 → 98 and boosting sign-up CTR by 17%."'),
    (r'\b(automat|script|workflow|tool|cli|bot)\w*',
     "automation or tooling",
     'e.g. "Automated weekly report generation, freeing 3 hours of manual analyst time per week."'),
]

# Fallback when no context matches
FALLBACK_METRIC_ADVICE = [
    "What did it save? Add time (hours/week), cost ($), or error rate reduction.",
    "Who benefited? Add user count, team size, or client reach impacted.",
    "How big was the scope? Add records processed, requests/sec, or deployment frequency.",
    "How fast was delivery? Add sprint length, days-to-ship, or release cadence.",
    "What did it improve? Add a before/after comparison: 'reduced X from A → B'.",
]
_fallback_idx = 0  # cycle through fallbacks so each bullet gets a different one


def _get_contextual_metric_advice(text: str, item_index: int) -> str:
    """Return a specific, contextual metric suggestion based on keywords in the bullet."""
    text_lower = text.lower()
    for pattern, area, example in METRIC_CONTEXTS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return (
                f"This bullet describes {area} but has no measurable outcome. "
                f"Add scale and impact — {example}"
            )
    # Cycle through fallbacks for variety
    advice = FALLBACK_METRIC_ADVICE[item_index % len(FALLBACK_METRIC_ADVICE)]
    return advice


# ---------------------------------------------------------------------------
# ATS-specific structural rules
# ---------------------------------------------------------------------------

ATS_RULES = [
    # (check_fn(text) -> bool, label, fixText)
    (
        lambda t: bool(re.search(r'\b(table|column|two.column|multi.column|sidebar)\b', t.lower())),
        "ATS Layout Risk",
        "Multi-column or table layouts are commonly mis-parsed by ATS scanners. "
        "Convert to a single-column, top-to-bottom bullet structure."
    ),
    (
        lambda t: len(t) > 220,
        "Bullet Too Long",
        f"This bullet exceeds ~180 chars — ATS systems truncate or mis-score long lines. "
        "Break into 2 separate achievements, each with its own action verb."
    ),
    (
        lambda t: bool(re.search(r'\b(reference|see page|refer to|appendix)\b', t.lower())),
        "Cross-Reference Found",
        "Avoid in-document references ('see page 2', 'appendix'). "
        "ATS parses each bullet in isolation with no page context."
    ),
    (
        lambda t: bool(re.search(r'[•●◦▪▸▹►◄❯❮→←]', t)) and len(t) < 15,
        "Orphan Symbol",
        "Short lines containing only a symbol or special character confuse ATS. "
        "Remove standalone decorative symbols."
    ),
]


def _check_ats_rules(text: str) -> Optional[Tuple[str, str]]:
    for check, label, advice in ATS_RULES:
        if check(text):
            return label, advice
    return None


# ---------------------------------------------------------------------------
# Passive / weak-language patterns with line-specific wording
# ---------------------------------------------------------------------------

PASSIVE_PATTERNS = [
    (r'\bworked with\b',
     '"Worked with" is passive — it hides who drove the outcome. '
     'Try: "Partnered with [X] to build [Y], delivering [Z]."'),
    (r'\bhelped (to |with )',
     '"Helped to/with" obscures your direct ownership. '
     'State your specific deliverable: start with a strong past-tense verb.'),
    (r'\bresponsible for\b',
     '"Responsible for" reads as a job description, not an achievement. '
     'Rewrite starting with an action verb: "Owned", "Built", "Delivered".'),
    (r'\bassisted (in|with)',
     '"Assisted in/with" de-prioritises your role. '
     'If you contributed meaningfully, own it: "Co-designed", "Implemented", "Contributed [specific part]."'),
    (r'\binvolved in\b',
     '"Involved in" is ambiguous. Name your exact task: did you design, build, review, or test?'),
    (r'\bwas (responsible|tasked|asked)\b',
     'Passive voice (was responsible/tasked/asked). Rewrite in active voice: "Owned…", "Led…", "Built…"'),
    (r'\b(managed|handling) (the|a) team\b',
     '"Managed the team" is vague. Add the team size, tenure, and a measurable outcome.'),
    (r'\bensured (that |the )?',
     '"Ensured" is weak without proof. Replace with a concrete action and outcome: "Established CI checks that caught 98% of regressions pre-merge."'),
    (r'\bcontributed to\b',
     '"Contributed to" lacks specificity. Clarify your exact contribution scope and the feature or component you owned.'),
]

ACTION_VERBS = [
    "built", "designed", "engineered", "implemented", "shipped", "spearheaded",
    "optimized", "architected", "developed", "led", "automated", "reduced",
    "increased", "launched", "scaled", "refactored", "deployed", "created",
    "migrated", "established", "authored", "delivered", "accelerated", "co-designed",
    "integrated", "diagnosed", "resolved", "streamlined", "replaced", "rewrote",
]

NUMBER_PATTERN = re.compile(
    r'(\d[\d,\.]*\s*%|\$\s*\d[\d,\.,]*|\b\d+\s*(?:ms|s\b|sec|min|hr|hrs|hours|days|weeks|users|clients|'
    r'requests|req|rps|k\b|m\b|gb|tb|lines?|engineers?|devs?|teams?)|\b[2-9]\d+\b|\b1\d{2,}\b)',
    re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Main heuristic engine
# ---------------------------------------------------------------------------

def _analyze_with_editorial_rules(doc: ParsedDocument, jd: Optional[str] = None) -> AnalysisResponse:
    annotations: List[Annotation] = []
    ann_counter = 1

    quantified_count = 0
    passive_count = 0
    strong_bullets_count = 0
    total_bullets = 0
    missing_metric_bullet_count = 0  # Track how many bullets we've flagged for metric

    has_skills_section = False
    has_experience_section = False
    all_text = ""

    # First pass: gather all_text for JD matching
    for section in doc.sections:
        for item in section.items:
            all_text += " " + item.text

    # Second pass: annotate
    for section in doc.sections:
        title_upper = section.title.upper()
        if "SKILL" in title_upper:
            has_skills_section = True
        if any(k in title_upper for k in ("EXPERIENCE", "WORK", "EMPLOYMENT", "PROFESSIONAL")):
            has_experience_section = True

        is_experience_section = any(
            k in title_upper for k in ("EXPERIENCE", "WORK", "EMPLOYMENT", "PROFESSIONAL", "PROJECT")
        )

        for i, item in enumerate(section.items):
            if item.itemType not in ("bullet", "text"):
                continue

            total_bullets += 1
            text = item.text
            text_lower = text.lower()
            has_numbers = bool(NUMBER_PATTERN.search(text))
            starts_with_action = any(text_lower.strip().startswith(v) for v in ACTION_VERBS)

            # ── 1. ATS structural issues (highest priority) ──────────────────
            ats_issue = _check_ats_rules(text)
            if ats_issue and is_experience_section:
                label, advice = ats_issue
                annotations.append(Annotation(
                    id=f"ann-{ann_counter}",
                    anchorId=item.id,
                    flagType="amber",
                    symbol="⚠",
                    label=label,
                    fixText=advice,
                ))
                ann_counter += 1
                continue  # don't stack multiple flags on one bullet

            # ── 2. Passive / weak language ───────────────────────────────────
            flagged_passive = False
            for pattern, recommendation in PASSIVE_PATTERNS:
                if re.search(pattern, text_lower):
                    annotations.append(Annotation(
                        id=f"ann-{ann_counter}",
                        anchorId=item.id,
                        flagType="amber",
                        symbol="⚠",
                        label="Passive Phrasing",
                        fixText=recommendation,
                    ))
                    ann_counter += 1
                    passive_count += 1
                    flagged_passive = True
                    break

            # ── 3. Quantified strength ───────────────────────────────────────
            if has_numbers and starts_with_action:
                quantified_count += 1
                strong_bullets_count += 1
                if not flagged_passive:
                    annotations.append(Annotation(
                        id=f"ann-{ann_counter}",
                        anchorId=item.id,
                        flagType="green",
                        symbol="✓",
                        label="High-Impact Metric",
                        fixText="Quantified outcome with a strong action verb — excellent anchor for an interview story.",
                    ))
                    ann_counter += 1

            # ── 4. Missing metric (contextual, per-bullet) ───────────────────
            elif (
                not has_numbers
                and is_experience_section
                and not flagged_passive
                and len(text) > 30
                and missing_metric_bullet_count < 6  # cap so header/skills don't flood
            ):
                advice = _get_contextual_metric_advice(text, missing_metric_bullet_count)
                annotations.append(Annotation(
                    id=f"ann-{ann_counter}",
                    anchorId=item.id,
                    flagType="amber",
                    symbol="⚠",
                    label="Add Measurable Outcome",
                    fixText=advice,
                ))
                ann_counter += 1
                missing_metric_bullet_count += 1

    # ── 5. JD skill gap ─────────────────────────────────────────────────────
    jd_score = 75
    skill_gap_score = 78

    if jd and jd.strip():
        jd_lower = jd.lower()
        SKILLS_CATALOG = [
            "typescript", "react", "next.js", "python", "fastapi", "node.js", "express",
            "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "github actions",
            "graphql", "tailwind", "sql", "postgresql", "mongodb", "redis", "kafka",
            "jest", "cypress", "pytest", "system design", "agile", "scrum",
            "terraform", "elasticsearch", "websocket", "microservices", "rest api",
            "machine learning", "data engineering", "spark", "airflow",
        ]
        missing_skills = [s for s in SKILLS_CATALOG if s in jd_lower and s not in all_text.lower()]
        matched_skills = [s for s in SKILLS_CATALOG if s in jd_lower and s in all_text.lower()]

        if missing_skills:
            # Find the last item in SKILLS or EXPERIENCE section to attach to
            target_anchor = None
            for s in reversed(doc.sections):
                if any(k in s.title.upper() for k in ("SKILL", "EXPERIENCE", "PROJECT")):
                    if s.items:
                        target_anchor = s.items[-1].id
                        break
            if not target_anchor and doc.sections and doc.sections[0].items:
                target_anchor = doc.sections[0].items[0].id

            if target_anchor:
                top_missing = missing_skills[:5]
                annotations.append(Annotation(
                    id=f"ann-{ann_counter}",
                    anchorId=target_anchor,
                    flagType="red",
                    symbol="✗",
                    label="Skill Gap vs. JD",
                    fixText=(
                        f"The target JD prioritises these keywords absent from your resume: "
                        f"{', '.join(t.title() for t in top_missing)}. "
                        "Add any that genuinely apply to your experience."
                    ),
                ))
                ann_counter += 1

            total = len(missing_skills) + len(matched_skills) or 1
            match_ratio = len(matched_skills) / total
            jd_score = max(45, int(match_ratio * 95))
            skill_gap_score = max(45, int(match_ratio * 90))

    else:
        # General baseline: check common industry-standard keywords
        BASELINE = {
            "git": "Version control (Git) isn't mentioned. Add if you use it — it's expected on every engineering resume.",
            "testing": "Testing (unit/integration) isn't referenced. Mention your test coverage practice or testing tools.",
            "ci/cd": "No CI/CD mention. If you've used GitHub Actions, CircleCI, or similar, add it.",
            "typescript": "TypeScript isn't listed under Skills. It's now a near-mandatory skill for frontend roles.",
        }
        for skill, tip in BASELINE.items():
            if skill not in all_text.lower():
                # Find skills section
                for s in doc.sections:
                    if "SKILL" in s.title.upper() and s.items:
                        annotations.append(Annotation(
                            id=f"ann-{ann_counter}",
                            anchorId=s.items[-1].id,
                            flagType="red",
                            symbol="✗",
                            label="Industry Baseline Gap",
                            fixText=tip,
                        ))
                        ann_counter += 1
                        break

    # ── 6. Structural completeness checks ───────────────────────────────────
    if not has_skills_section:
        if doc.sections:
            annotations.append(Annotation(
                id=f"ann-{ann_counter}",
                anchorId=doc.sections[0].id,
                flagType="red",
                symbol="✗",
                label="Missing Skills Section",
                fixText="Add a dedicated SKILLS section. ATS systems parse keyword lists here to match JD requirements.",
            ))
            ann_counter += 1

    if not has_experience_section:
        if doc.sections:
            annotations.append(Annotation(
                id=f"ann-{ann_counter}",
                anchorId=doc.sections[0].id,
                flagType="amber",
                symbol="⚠",
                label="No Experience Section",
                fixText="Add a WORK EXPERIENCE or PROFESSIONAL EXPERIENCE section. This is the primary signal ATS and recruiters evaluate.",
            ))
            ann_counter += 1

    # ── Score calculation ────────────────────────────────────────────────────
    general_score = min(95, max(55, 70 + (strong_bullets_count * 5) - (passive_count * 4)))
    ats_score = 88
    if not has_skills_section:
        ats_score -= 18
    if not has_experience_section:
        ats_score -= 22
    if total_bullets < 4:
        ats_score -= 12
    ats_score = max(50, min(97, ats_score))

    overall = int(
        general_score * 0.30
        + ats_score * 0.25
        + jd_score * 0.25
        + skill_gap_score * 0.20
    )

    return AnalysisResponse(
        scores=Scores(
            overall=overall,
            general=general_score,
            ats=ats_score,
            jdMatch=jd_score,
            skillGap=skill_gap_score,
        ),
        document=doc,
        annotations=annotations,
    )


# ---------------------------------------------------------------------------
# LLM back-ends (Gemini primary, Anthropic / OpenAI stubs)
# ---------------------------------------------------------------------------

async def analyze_resume(doc: ParsedDocument, job_description: Optional[str] = None) -> AnalysisResponse:
    gemini_key = os.getenv("GEMINI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if gemini_key:
        try:
            return await _analyze_with_gemini(doc, job_description, gemini_key)
        except Exception as e:
            print(f"[Analyzer] Gemini failed ({e}), falling back to heuristic engine.")

    if anthropic_key:
        try:
            return await _analyze_with_anthropic(doc, job_description, anthropic_key)
        except Exception as e:
            print(f"[Analyzer] Anthropic failed ({e}), falling back to heuristic engine.")

    if openai_key:
        try:
            return await _analyze_with_openai(doc, job_description, openai_key)
        except Exception as e:
            print(f"[Analyzer] OpenAI failed ({e}), falling back to heuristic engine.")

    return _analyze_with_editorial_rules(doc, job_description)


async def _analyze_with_gemini(doc: ParsedDocument, jd: Optional[str], api_key: str) -> AnalysisResponse:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    sections_payload = []
    for s in doc.sections:
        items_desc = [f"[{it.id}] ({it.itemType}) {it.text}" for it in s.items]
        sections_payload.append(f"## {s.title}\n" + "\n".join(items_desc))

    prompt = f"""You are an expert, meticulous editorial proofreader analyzing a candidate's resume.

Return ONLY a JSON object matching this schema exactly:
{{
  "scores": {{
    "overall": <int 0-100>,
    "general": <int 0-100>,
    "ats": <int 0-100>,
    "jdMatch": <int 0-100>,
    "skillGap": <int 0-100>
  }},
  "annotations": [
    {{
      "id": "ann-1",
      "anchorId": "<exact item ID from the resume below>",
      "flagType": "amber" | "red" | "green",
      "symbol": "⚠" | "✗" | "✓",
      "label": "<8 words max>",
      "fixText": "<Specific, actionable, unique suggestion for THIS bullet. Never repeat the same fixText across annotations. Include a concrete example metric or rewrite.>"
    }}
  ]
}}

Flag meanings:
- amber ⚠ : formatting risk, passive voice ("worked with", "helped"), vague language, missing quantifiable outcome
- red ✗ : missing skills vs JD, structural absence (no skills section), critical content gaps
- green ✓ : quantified achievement, strong action verb + metric, leadership with outcome

CRITICAL RULE: Every annotation must have a UNIQUE, SPECIFIC fixText tailored to that exact bullet's content.
Never generate the same suggestion twice. Each annotation should name what specifically could be improved for THAT line.

Job Description (if provided):
{jd or "None — evaluate against modern software engineering standards."}

Resume Document (use these IDs for anchorId):
{chr(10).join(sections_payload)}
"""

    async with httpx.AsyncClient(timeout=35.0) as client:
        resp = await client.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
        )

    if resp.status_code != 200:
        raise RuntimeError(f"Gemini returned {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    raw = data["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(raw)

    return AnalysisResponse(
        scores=Scores(**parsed["scores"]),
        document=doc,
        annotations=[Annotation(**a) for a in parsed["annotations"]],
    )


async def _analyze_with_anthropic(doc: ParsedDocument, jd: Optional[str], api_key: str) -> AnalysisResponse:
    # Falls back to heuristic engine for now
    return _analyze_with_editorial_rules(doc, jd)


async def _analyze_with_openai(doc: ParsedDocument, jd: Optional[str], api_key: str) -> AnalysisResponse:
    # Falls back to heuristic engine for now
    return _analyze_with_editorial_rules(doc, jd)
