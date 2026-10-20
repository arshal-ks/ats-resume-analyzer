"""
Modern UI styling, CSS injection, badge renderers, and visual components
for the ATS Resume Analyzer Streamlit application.
"""

import streamlit as st
from typing import Dict, List, Tuple


def inject_custom_css():
    """Injects high-end, responsive custom styling into Streamlit."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container max width & polish */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* Hero Header Banner */
    .hero-container {
        background: linear-gradient(135deg, #090d16 0%, #1e1b4b 45%, #2e1065 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 2.2rem 2.8rem;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 25px 30px -10px rgba(0, 0, 0, 0.35);
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -60px;
        right: -60px;
        width: 340px;
        height: 340px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.28) 0%, rgba(168, 85, 247, 0.15) 50%, transparent 75%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.6rem;
        background: linear-gradient(90deg, #ffffff 0%, #c7d2fe 60%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        max-width: 760px;
        line-height: 1.6;
        margin: 0;
    }
    .hero-pills {
        display: flex;
        gap: 10px;
        margin-top: 1.2rem;
        flex-wrap: wrap;
    }
    .hero-pill-item {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 9999px;
        padding: 4px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #e2e8f0;
        backdrop-filter: blur(8px);
    }

    /* Glassmorphism Dashboard Cards */
    .dashboard-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .dashboard-card:hover {
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.08);
    }
    @media (prefers-color-scheme: dark) {
        .dashboard-card {
            background: #131b2e;
            border-color: #23304a;
            color: #f1f5f9;
        }
    }

    /* Score Hero Gauge Card */
    .score-hero-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.8rem;
        position: relative;
    }
    @media (prefers-color-scheme: dark) {
        .score-hero-card {
            background: linear-gradient(135deg, #131b2e 0%, #0f172a 100%);
            border-color: #23304a;
        }
    }
    .score-display {
        font-size: 4.2rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.04em;
        margin: 0.75rem 0;
    }
    .score-high {
        background: linear-gradient(135deg, #10b981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-med {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-low {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Metric progress bar */
    .custom-progress-track {
        background: #e2e8f0;
        border-radius: 9999px;
        height: 10px;
        overflow: hidden;
        margin-top: 8px;
    }
    @media (prefers-color-scheme: dark) {
        .custom-progress-track {
            background: #1e293b;
        }
    }
    .custom-progress-fill-emerald {
        background: linear-gradient(90deg, #10b981, #34d399);
        height: 100%;
        border-radius: 9999px;
    }
    .custom-progress-fill-amber {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        height: 100%;
        border-radius: 9999px;
    }
    .custom-progress-fill-indigo {
        background: linear-gradient(90deg, #6366f1, #818cf8);
        height: 100%;
        border-radius: 9999px;
    }

    /* Pill Badges */
    .badge-matched {
        display: inline-flex;
        align-items: center;
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.84rem;
        font-weight: 600;
        margin: 4px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .badge-missing {
        display: inline-flex;
        align-items: center;
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.84rem;
        font-weight: 600;
        margin: 4px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .badge-extra {
        display: inline-flex;
        align-items: center;
        background: #f0fdf4;
        color: #1e40af;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.84rem;
        font-weight: 600;
        margin: 4px;
    }

    /* Warnings Banner & Cards */
    .warning-alert-card {
        background: #fff1f2;
        border-left: 5px solid #f43f5e;
        border-radius: 12px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1rem;
        color: #9f1239;
        font-size: 0.92rem;
    }
    @media (prefers-color-scheme: dark) {
        .warning-alert-card {
            background: #2b0b14;
            color: #ffe4e6;
            border-left-color: #fb7185;
        }
    }

    .info-alert-card {
        background: #eff6ff;
        border-left: 5px solid #3b82f6;
        border-radius: 12px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1rem;
        color: #1e40af;
        font-size: 0.92rem;
    }
    @media (prefers-color-scheme: dark) {
        .info-alert-card {
            background: #0f1f38;
            color: #dbeafe;
            border-left-color: #60a5fa;
        }
    }

    /* Section Checklist Cards */
    .section-audit-row {
        padding: 12px 18px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        transition: all 0.2s ease;
    }
    @media (prefers-color-scheme: dark) {
        .section-audit-row {
            background: #111827;
            border-color: #1f2937;
        }
    }
    .status-found-pill {
        background: #dcfce7;
        color: #15803d;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #86efac;
    }
    .status-missing-pill {
        background: #fee2e2;
        color: #b91c1c;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #fca5a5;
    }

    /* ATS Truth Disclaimer Box */
    .ats-truth-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-left: 5px solid #f59e0b;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin: 1.6rem 0;
        color: #92400e;
        font-size: 0.92rem;
        line-height: 1.55;
    }
    @media (prefers-color-scheme: dark) {
        .ats-truth-box {
            background: #381a04;
            color: #fef3c7;
            border-color: #78350f;
            border-left-color: #fbbf24;
        }
    }

    /* Action Recommendation Card */
    .rec-item-card {
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        background: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    @media (prefers-color-scheme: dark) {
        .rec-item-card {
            background: #131b2e;
            border-color: #23304a;
        }
    }
    .rec-p-high { border-left: 5px solid #ef4444; }
    .rec-p-medium { border-left: 5px solid #f59e0b; }
    .rec-p-low { border-left: 5px solid #3b82f6; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_hero_banner():
    """Renders the top hero banner with branding and value proposition."""
    banner = """
    <div class="hero-container">
        <div class="hero-title">
            <span>🎯</span> ATS Resume Alignment & Coverage Engine
        </div>
        <div class="hero-subtitle">
            An intelligent, privacy-first resume optimization dashboard. Evaluate resume compatibility against
            target job descriptions with mathematical skill coverage, keyword relevance, formatting audits,
            and honest, actionable recommendations.
        </div>
        <div class="hero-pills">
            <span class="hero-pill-item">🔒 100% Local Processing</span>
            <span class="hero-pill-item">⚡ PyMuPDF & python-docx</span>
            <span class="hero-pill-item">📊 Scikit-Learn TF-IDF</span>
            <span class="hero-pill-item">⚖️ Zero Artificial Black-Boxes</span>
        </div>
    </div>
    """
    st.markdown(banner, unsafe_allow_html=True)


def render_ats_truth_banner():
    """Renders the prominent educational disclaimer regarding real ATS operations."""
    disclaimer = """
    <div class="ats-truth-box">
        <div style="font-weight: 700; font-size: 0.98rem; margin-bottom: 4px;">
            ⚖️ ATS Reality & Score Transparency Notice
        </div>
        Real Applicant Tracking Systems (e.g. Workday, Greenhouse, Lever, Taleo) are indexed search databases
        used by human recruiters. They do <strong>not</strong> operate universal AI robots that auto-reject candidates
        based on a single composite score. This score measures your <strong>transparent textual and skill alignment</strong>
        against the provided job posting so human recruiters can quickly find your qualifications. It does not guarantee
        an interview or job selection.
    </div>
    """
    st.markdown(disclaimer, unsafe_allow_html=True)


def render_score_card(score: float):
    """Renders the primary score gauge with color coding."""
    if score >= 75:
        score_class = "score-high"
        rating_text = "Strong Alignment (75%+)"
        rating_badge = "background: #dcfce7; color: #15803d; border: 1px solid #86efac;"
        rating_desc = "Your resume demonstrates comprehensive coverage of core requirements and job keywords."
    elif score >= 50:
        score_class = "score-med"
        rating_text = "Moderate Alignment (50–74%)"
        rating_badge = "background: #fef3c7; color: #b45309; border: 1px solid #fde68a;"
        rating_desc = "Key foundational requirements match, but specific target skills or keywords are absent."
    else:
        score_class = "score-low"
        rating_text = "Low Alignment (<50%)"
        rating_badge = "background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;"
        rating_desc = "Significant gaps detected in target skills, critical sections, or job keywords."

    card_html = f"""
    <div class="score-hero-card">
        <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b;">
            Transparent Skill Coverage Score
        </div>
        <div class="score-display {score_class}">{score:.1f}%</div>
        <div style="display: inline-block; padding: 4px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem; margin-bottom: 0.5rem; {rating_badge}">
            {rating_text}
        </div>
        <div style="font-size: 0.9rem; color: #64748b; max-width: 520px; margin: 0 auto; line-height: 1.5;">
            {rating_desc}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_skills_cloud(skills: List[str], badge_type: str = "matched") -> str:
    """Generates HTML string of pill badges for skills."""
    if not skills:
        return "<span style='color: #94a3b8; font-style: italic; font-size: 0.85rem;'>None detected</span>"

    css_class = f"badge-{badge_type}"
    prefix = "✓ " if badge_type == "matched" else ("✕ " if badge_type == "missing" else "+ ")
    badges = [f"<span class='{css_class}'>{prefix}{skill}</span>" for skill in skills]
    return " ".join(badges)


def render_recommendation_card(rec: Dict[str, str]):
    """Renders a single actionable recommendation card."""
    priority = rec.get("priority", "Medium")
    p_class = f"rec-p-{priority.lower()}"
    p_color = "#ef4444" if priority == "High" else ("#f59e0b" if priority == "Medium" else "#3b82f6")

    card_html = f"""
    <div class="rec-item-card {p_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: 700; font-size: 1.05rem; color: #1e293b;">
                {rec.get('title')}
            </div>
            <span style="font-size: 0.75rem; font-weight: 700; color: {p_color}; background: #f8fafc; border: 1px solid #e2e8f0; padding: 3px 9px; border-radius: 6px;">
                {priority} Priority
            </span>
        </div>
        <div style="font-size: 0.92rem; line-height: 1.55; color: #475569;">
            {rec.get('message')}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
