"""
Core analysis engine for ATS Resume Analyzer.
Performs section detection, contact info extraction, skill matching,
TF-IDF keyword extraction, transparent scoring, and honest recommendations.
"""

import re
from typing import Any, Dict, List, Set, Tuple

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    TfidfVectorizer = None

from core.skills_db import (
    SKILL_CATEGORIES,
    extract_skills_from_text,
    get_skill_category,
    normalize_skill_name,
)

# Standard section header regex patterns commonly parsed by ATS
SECTION_PATTERNS: Dict[str, List[str]] = {
    "Contact Information": [
        r"(contact|phone|email|linkedin|github|portfolio|address)",
    ],
    "Professional Summary": [
        r"(summary|professional summary|executive summary|about me|profile|career objective|objective)",
    ],
    "Work Experience": [
        r"(experience|work experience|employment history|professional experience|work history|career history)",
    ],
    "Education": [
        r"(education|academic background|qualifications|degrees|academics)",
    ],
    "Skills": [
        r"(skills|technical skills|core competencies|technologies|proficiencies|expertise)",
    ],
    "Projects": [
        r"(projects|personal projects|key projects|academic projects|portfolio projects)",
    ],
    "Certifications": [
        r"(certifications|licenses|certificates|credentials|accreditations)",
    ],
}

# Strong action verbs for resume impact analysis
STRONG_ACTION_VERBS: Set[str] = {
    "accelerated", "achieved", "adapted", "administered", "analyzed", "architected",
    "automated", "built", "championed", "collaborated", "conceived", "consolidated",
    "coordinated", "crafted", "decreased", "delivered", "deployed", "designed",
    "developed", "devised", "directed", "doubled", "drove", "eliminated",
    "engineered", "established", "executed", "expanded", "expedited", "formulated",
    "founded", "generated", "guided", "implemented", "improved", "increased",
    "initiated", "innovated", "installed", "instituted", "integrated", "introduced",
    "launched", "led", "managed", "maximized", "mentored", "migrated", "minimized",
    "modernized", "negotiated", "optimized", "orchestrated", "overhauled", "pioneered",
    "programmed", "reduced", "refactored", "resolved", "restructured", "revamped",
    "scaled", "simplified", "spearheaded", "standardized", "streamlined", "strengthened",
    "surpassed", "transformed", "unified", "upgraded", "yielded"
}


def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extracts contact info: emails, phone numbers, and web profiles (LinkedIn, GitHub).
    """
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    phone_pattern = r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4})"
    linkedin_pattern = r"(?:linkedin\.com/(?:in|company)/[a-zA-Z0-9_-]+)"
    github_pattern = r"(?:github\.com/[a-zA-Z0-9_-]+)"

    emails = re.findall(email_pattern, text)
    phones = [p.strip() for p in re.findall(phone_pattern, text) if len(re.sub(r"\D", "", p)) >= 10]
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    github = re.findall(github_pattern, text, re.IGNORECASE)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": f"https://{linkedin[0]}" if linkedin else None,
        "github": f"https://{github[0]}" if github else None,
        "all_emails": emails,
        "has_email": bool(emails),
        "has_phone": bool(phones),
        "has_profiles": bool(linkedin or github),
    }


def detect_sections(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Scans the resume for standard section headings.
    Returns: Dict[section_name -> {'found': bool, 'matched_term': str}]
    """
    results = {}
    lines = text.split("\n")

    for section_name, patterns in SECTION_PATTERNS.items():
        found = False
        matched_term = None

        if section_name == "Contact Information":
            contact = extract_contact_info(text)
            found = contact["has_email"] or contact["has_phone"]
            matched_term = "Email/Phone Found" if found else None
            results[section_name] = {"found": found, "matched_term": matched_term}
            continue

        # Check line headers (lines with few words, typical of headers)
        for line in lines:
            clean_line = line.strip().lower()
            # Headers are usually short (under 7 words)
            if 1 <= len(clean_line.split()) <= 6:
                clean_header = re.sub(r"[^\w\s]", "", clean_line).strip()
                for pattern in patterns:
                    if re.search(rf"^{pattern}$", clean_header):
                        found = True
                        matched_term = line.strip()
                        break
                if found:
                    break

        # Fallback: looser search in text if not found in isolated lines
        if not found:
            for pattern in patterns:
                match = re.search(rf"\b({pattern})[:\s-]", text, re.IGNORECASE)
                if match:
                    found = True
                    matched_term = match.group(0).strip()
                    break

        results[section_name] = {"found": found, "matched_term": matched_term}

    return results


def extract_top_keywords_tfidf(
    job_description: str, top_n: int = 15
) -> List[Tuple[str, float]]:
    """
    Extracts the most salient keywords and n-grams from the Job Description using scikit-learn TF-IDF.
    Returns: List of (keyword, score)
    """
    if not job_description or not job_description.strip():
        return []

    if TfidfVectorizer is None:
        # Fallback simple frequency count if sklearn isn't available
        words = re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower())
        stopwords = {
            "and", "the", "with", "for", "that", "this", "from", "you", "are",
            "will", "have", "our", "your", "work", "team", "role", "must",
            "years", "experience", "looking", "candidate", "about", "what", "their"
        }
        filtered = [w for w in words if w not in stopwords]
        from collections import Counter
        counts = Counter(filtered).most_common(top_n)
        return [(word, float(freq)) for word, freq in counts]

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.-]{1,}\b",
        )
        tfidf_matrix = vectorizer.fit_transform([job_description])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        scored_features = [
            (feature_names[i], float(scores[i]))
            for i in scores.argsort()[::-1]
            if len(feature_names[i]) > 2
        ]
        return scored_features[:top_n]
    except Exception:
        return []


def analyze_action_verbs(text: str) -> Dict[str, Any]:
    """
    Detects use of active, impactful accomplishment verbs.
    """
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    found_verbs = [w for w in words if w in STRONG_ACTION_VERBS]
    unique_verbs = sorted(list(set(found_verbs)))

    # Evaluate action verb density
    total_words = len(words)
    density = (len(found_verbs) / total_words * 100) if total_words > 0 else 0

    return {
        "count": len(found_verbs),
        "unique_count": len(unique_verbs),
        "unique_verbs": unique_verbs,
        "density_pct": round(density, 2),
    }


def calculate_ats_analysis(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Executes full ATS alignment analysis with mathematically transparent scoring.
    """
    # 1. Contact Information & Sections
    contact_info = extract_contact_info(resume_text)
    sections = detect_sections(resume_text)

    # 2. Skill Extraction
    resume_skills_by_cat = extract_skills_from_text(resume_text)
    jd_skills_by_cat = extract_skills_from_text(jd_text)

    all_resume_skills = set()
    for s_set in resume_skills_by_cat.values():
        all_resume_skills.update(s_set)

    all_jd_skills = set()
    for s_set in jd_skills_by_cat.values():
        all_jd_skills.update(s_set)

    matched_skills = sorted(list(all_jd_skills.intersection(all_resume_skills)))
    missing_skills = sorted(list(all_jd_skills - all_resume_skills))
    additional_skills = sorted(list(all_resume_skills - all_jd_skills))

    # Categorized skill matches & gaps
    categorized_skill_breakdown = {}
    for cat in SKILL_CATEGORIES.keys():
        jd_cat_skills = jd_skills_by_cat.get(cat, set())
        res_cat_skills = resume_skills_by_cat.get(cat, set())
        matched = sorted(list(jd_cat_skills.intersection(res_cat_skills)))
        missing = sorted(list(jd_cat_skills - res_cat_skills))

        if jd_cat_skills or res_cat_skills:
            categorized_skill_breakdown[cat] = {
                "jd_skills": sorted(list(jd_cat_skills)),
                "resume_skills": sorted(list(res_cat_skills)),
                "matched": matched,
                "missing": missing,
            }

    # 3. Dynamic TF-IDF Keywords from Job Description
    top_jd_keywords_scored = extract_top_keywords_tfidf(jd_text, top_n=15)
    matched_keywords = []
    missing_keywords = []

    res_lower = resume_text.lower()
    for kw, score in top_jd_keywords_scored:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(kw) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, res_lower):
            matched_keywords.append((kw, score))
        else:
            missing_keywords.append((kw, score))

    # 4. Action Verbs & Hygiene
    verbs_data = analyze_action_verbs(resume_text)
    words = resume_text.split()
    word_count = len(words)

    # Brevity / Word Count Score (1-2 pages standard: ~350 - 1000 words)
    if 350 <= word_count <= 1100:
        brevity_score = 100
        length_feedback = "Optimal resume length (estimated 1-2 pages)."
    elif 200 <= word_count < 350:
        brevity_score = 75
        length_feedback = "Slightly brief. Consider adding quantifiable achievements."
    elif 1100 < word_count <= 1600:
        brevity_score = 80
        length_feedback = "A bit lengthy. Ensure bullet points are concise and impactful."
    elif word_count > 1600:
        brevity_score = 60
        length_feedback = "Over 1600 words. Recruiter scanning fatigue is likely; trim older roles."
    else:
        brevity_score = 40
        length_feedback = "Too short (<200 words). Likely missing critical sections."

    # Section Completeness Score (Weight: 15%)
    # Mandatory essential sections: Contact, Experience, Education, Skills
    essential_sections = ["Contact Information", "Work Experience", "Education", "Skills"]
    found_essential = sum(1 for s in essential_sections if sections.get(s, {}).get("found", False))
    section_score = (found_essential / len(essential_sections)) * 100

    # Skills Match Score (Weight: 50%)
    if len(all_jd_skills) > 0:
        skill_score = (len(matched_skills) / len(all_jd_skills)) * 100
    else:
        # If JD has no detectable standard skills, score neutrally based on keyword presence
        skill_score = 75.0 if len(all_resume_skills) > 0 else 50.0

    # TF-IDF Keyword Match Score (Weight: 25%)
    if len(top_jd_keywords_scored) > 0:
        keyword_score = (len(matched_keywords) / len(top_jd_keywords_scored)) * 100
    else:
        keyword_score = 75.0

    # Formatting & Action Verb Hygiene Score (Weight: 10%)
    verb_points = min(50, verbs_data["unique_count"] * 5)  # up to 50 pts
    brevity_points = brevity_score * 0.5                  # up to 50 pts
    hygiene_score = verb_points + brevity_points

    # Overall Transparent Score Calculation
    # Weights: Skills 50%, Keywords 25%, Sections 15%, Hygiene 10%
    w_skill = 0.50
    w_kw = 0.25
    w_sec = 0.15
    w_hyg = 0.10

    total_score = round(
        (skill_score * w_skill)
        + (keyword_score * w_kw)
        + (section_score * w_sec)
        + (hygiene_score * w_hyg),
        1,
    )

    # Generate Honest Improvement Recommendations
    suggestions: List[Dict[str, str]] = []

    # Missing Skills Recommendations
    if missing_skills:
        top_missing = missing_skills[:6]
        suggestions.append({
            "type": "Skill Gap",
            "priority": "High",
            "title": f"Target Missing Core Skills ({len(missing_skills)} identified)",
            "message": (
                f"The job description highlights key skills that were not detected in your resume: "
                f"**{', '.join(top_missing)}**. "
                "If you possess hands-on experience with any of these, incorporate them into relevant "
                "work experience bullet points with tangible outcomes."
            ),
        })

    # Missing Top Keywords
    if missing_keywords:
        top_missing_kw = [k[0] for k in missing_keywords[:5]]
        suggestions.append({
            "type": "Keyword Alignment",
            "priority": "Medium",
            "title": "Incorporate Salient Role Terms",
            "message": (
                f"Frequently mentioned role keywords missing in your resume include: "
                f"**{', '.join(top_missing_kw)}**. "
                "Mirroring the terminology used by the hiring team helps both ATS search filters and recruiters."
            ),
        })

    # Missing Section Headers
    missing_sections = [
        name for name, data in sections.items() if not data["found"] and name in essential_sections
    ]
    if missing_sections:
        suggestions.append({
            "type": "Structure & Parsing",
            "priority": "High",
            "title": f"Add Standard Section Headers ({', '.join(missing_sections)})",
            "message": (
                f"Standard ATS parsers search for explicit section headers. Your resume appears to lack: "
                f"**{', '.join(missing_sections)}**. Use simple, conventional labels (e.g., 'Work Experience', 'Education') "
                "without fancy creative titles or graphics."
            ),
        })

    # Contact Info Gaps
    if not contact_info["has_email"] or not contact_info["has_phone"]:
        missing_contacts = []
        if not contact_info["has_email"]:
            missing_contacts.append("Email Address")
        if not contact_info["has_phone"]:
            missing_contacts.append("Phone Number")
        suggestions.append({
            "type": "Contact Info",
            "priority": "High",
            "title": f"Contact Details Missing: {', '.join(missing_contacts)}",
            "message": (
                "Ensure your email and phone number are in plain text near the top of the resume. "
                "Avoid placing contact info inside nested header/footer artifacts or graphics."
            ),
        })

    # Action Verbs
    if verbs_data["unique_count"] < 6:
        suggestions.append({
            "type": "Impact & Phrasing",
            "priority": "Medium",
            "title": "Elevate Impact with Strong Action Verbs",
            "message": (
                f"Only {verbs_data['unique_count']} unique action verbs detected. "
                "Begin bullet points with verbs like *Architected, Spearheaded, Accelerated, Optimized* "
                "paired with metric outcomes (e.g., 'increased throughput by 35%')."
            ),
        })

    # Length / Brevity
    if brevity_score < 80:
        suggestions.append({
            "type": "Length & Brevity",
            "priority": "Low",
            "title": "Resume Length Feedback",
            "message": length_feedback,
        })

    return {
        "total_score": min(100.0, max(0.0, total_score)),
        "score_breakdown": {
            "skills": {
                "score": round(skill_score, 1),
                "weight": int(w_skill * 100),
                "weighted_points": round(skill_score * w_skill, 1),
                "details": f"{len(matched_skills)} of {len(all_jd_skills)} JD skills matched",
            },
            "keywords": {
                "score": round(keyword_score, 1),
                "weight": int(w_kw * 100),
                "weighted_points": round(keyword_score * w_kw, 1),
                "details": f"{len(matched_keywords)} of {len(top_jd_keywords_scored)} top TF-IDF keywords found",
            },
            "sections": {
                "score": round(section_score, 1),
                "weight": int(w_sec * 100),
                "weighted_points": round(section_score * w_sec, 1),
                "details": f"{found_essential} of {len(essential_sections)} essential sections found",
            },
            "hygiene": {
                "score": round(hygiene_score, 1),
                "weight": int(w_hyg * 100),
                "weighted_points": round(hygiene_score * w_hyg, 1),
                "details": f"{verbs_data['unique_count']} action verbs; {word_count} words",
            },
        },
        "contact_info": contact_info,
        "sections": sections,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "categorized_skill_breakdown": categorized_skill_breakdown,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "verbs_data": verbs_data,
        "word_count": word_count,
        "suggestions": suggestions,
    }
