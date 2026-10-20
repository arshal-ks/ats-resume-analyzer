"""
Main Streamlit Application for ATS Resume Analyzer.
Provides an ultra-modern, responsive, and privacy-first interface for analyzing
resumes against job descriptions with transparent scoring, formatting audits,
and actionable improvement suggestions.
"""

import io
import streamlit as st

from analyzer import calculate_ats_analysis
from core.extractor import ResumeExtractor
from core.ui_helpers import (
    inject_custom_css,
    render_ats_truth_banner,
    render_hero_banner,
    render_recommendation_card,
    render_score_card,
    render_skills_cloud,
)
from sample_data import SAMPLE_JOBS, SAMPLE_RESUMES

# Streamlit Page Setup
st.set_page_config(
    page_title="ATS Resume Alignment & Skill Coverage Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject modern CSS design system
inject_custom_css()


def main():
    render_hero_banner()

    # --- SIDEBAR CONFIGURATION ---
    with st.sidebar:
        st.markdown("### ⚙️ Quick Demo & Samples")
        load_sample = st.checkbox(
            "Use Built-in Interactive Demo",
            value=True,
            help="Pre-fills a real-world software engineering job and matching resume for instant evaluation.",
        )

        selected_sample_role = None
        selected_sample_resume = None

        if load_sample:
            selected_sample_role = st.selectbox(
                "Select Target Job Posting:",
                list(SAMPLE_JOBS.keys()),
                index=0,
            )
            selected_sample_resume = st.selectbox(
                "Select Candidate Resume:",
                list(SAMPLE_RESUMES.keys()),
                index=0,
            )

        st.markdown("---")
        st.markdown("### 📐 Transparent Scoring Weights")
        with st.expander("Formula Transparency", expanded=True):
            st.markdown(
                """
                - **Skill Coverage**: `50%`
                - **TF-IDF Keyword Fit**: `25%`
                - **Essential Sections**: `15%`
                - **Formatting & Verbs**: `10%`
                
                *No hidden algorithms or black boxes.*
                """
            )

        st.markdown("---")
        st.caption("🔒 **Privacy Guarantee**: 100% local processing. No external paid APIs or cloud databases.")

    # --- INPUT SECTION: 2-COLUMN MODERN DASHBOARD ---
    st.markdown("### 📥 Input Documents")
    col_res, col_jd = st.columns([1, 1], gap="large")

    # Column 1: Resume Upload Area
    with col_res:
        st.markdown("#### 📄 1. Resume Document")
        input_type = st.radio(
            "Resume Source:",
            ["Upload File (.pdf, .docx)", "Paste Resume Text"],
            horizontal=True,
            label_visibility="collapsed",
        )

        uploaded_file = None
        extracted_text = ""
        meta_info = {}
        resume_label = "Sample Resume"

        if input_type == "Upload File (.pdf, .docx)":
            uploaded_file = st.file_uploader(
                "Upload Resume File",
                type=["pdf", "docx"],
                help="PDF parsed via PyMuPDF; DOCX parsed via python-docx. Files never leave your local environment.",
            )
            if uploaded_file is not None:
                resume_label = uploaded_file.name
                try:
                    bytes_data = uploaded_file.getvalue()
                    extracted_text, meta_info = ResumeExtractor.extract_text(
                        bytes_data, filename=uploaded_file.name
                    )
                except Exception as e:
                    st.error(f"Error parsing resume: {str(e)}")
                    extracted_text = ""
        else:
            default_paste = (
                SAMPLE_RESUMES[selected_sample_resume]
                if (load_sample and selected_sample_resume)
                else ""
            )
            extracted_text = st.text_area(
                "Paste Resume Text:",
                value=default_paste,
                height=220,
                placeholder="Paste the full text of your resume here...",
            )
            resume_label = "Pasted Resume Text"

        # If sample mode was checked and no file uploaded, fallback to sample text
        if not extracted_text and load_sample and selected_sample_resume and input_type == "Upload File (.pdf, .docx)":
            extracted_text = SAMPLE_RESUMES[selected_sample_resume]
            resume_label = selected_sample_resume
            st.info(f"Loaded demo resume: **{selected_sample_resume}**")

        # Live Resume Stats Badge Bar
        if extracted_text:
            w_count = len(extracted_text.split())
            p_count = meta_info.get("page_count", max(1, round(w_count / 400)))
            f_type = meta_info.get("file_type", "text").upper()

            st.markdown(
                f"""
                <div style="display: flex; gap: 8px; margin-top: 6px; margin-bottom: 12px; flex-wrap: wrap;">
                    <span style="background: #f1f5f9; color: #475569; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                        Format: {f_type}
                    </span>
                    <span style="background: #f1f5f9; color: #475569; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                        Words: {w_count}
                    </span>
                    <span style="background: #f1f5f9; color: #475569; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                        Est. Pages: {p_count}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("👁️ View Extracted Resume Text", expanded=False):
            st.text_area(
                "Extracted Text Preview",
                value=extracted_text,
                height=160,
                disabled=True,
                label_visibility="collapsed",
            )

    # Column 2: Job Description Box
    with col_jd:
        st.markdown("#### 💼 2. Target Job Description")
        default_jd = (
            SAMPLE_JOBS[selected_sample_role]
            if (load_sample and selected_sample_role)
            else ""
        )
        jd_input = st.text_area(
            "Target Job Description:",
            value=default_jd,
            height=265,
            placeholder="Paste the target job description (responsibilities, required qualifications, tech stack)...",
            label_visibility="collapsed",
        )

        if jd_input:
            jd_words = len(jd_input.split())
            st.markdown(
                f"""
                <div style="display: flex; gap: 8px; margin-top: 6px; margin-bottom: 12px;">
                    <span style="background: #f1f5f9; color: #475569; padding: 3px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                        Job Description Length: {jd_words} words
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --- ACTION BUTTON ---
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button(
        "🚀 Run Complete ATS Alignment Analysis",
        type="primary",
        use_container_width=True,
    )

    # Trigger analysis
    if analyze_btn or (extracted_text and jd_input and "has_run" in st.session_state):
        st.session_state["has_run"] = True

        if not extracted_text.strip():
            st.error("Please upload or paste a resume first.")
            return

        if not jd_input.strip():
            st.error("Please enter a job description to perform alignment analysis.")
            return

        with st.spinner("Analyzing skills, parsing sections, and computing keyword alignment..."):
            results = calculate_ats_analysis(extracted_text, jd_input)

        st.markdown("---")

        # Educational Truth Banner
        render_ats_truth_banner()

        # Score Hero Card
        score = results["total_score"]
        render_score_card(score)

        # FORMATTING WARNINGS (Always Prominently Rendered)
        st.markdown("### ⚠️ Resume Formatting & Parsing Warnings")
        warnings_found = []

        # 1. Scanned Warning
        if meta_info.get("is_scanned_warning"):
            warnings_found.append({
                "type": "Critical Formatting Warning",
                "title": "Potential Scanned / Image-Only PDF Detected",
                "text": "Very little textual content was extracted from this PDF. If your resume was exported as an image scan, standard ATS parsers cannot read your qualifications, rendering your application blank in recruiter searches. Please re-export from Word/Docs as a selectable text PDF.",
            })

        # 2. Missing Essential Sections
        essential = ["Contact Information", "Work Experience", "Education", "Skills"]
        missing_sec = [s for s in essential if not results["sections"].get(s, {}).get("found", False)]
        if missing_sec:
            warnings_found.append({
                "type": "Structural Warning",
                "title": f"Missing Core Section Headers: {', '.join(missing_sec)}",
                "text": f"Your resume appears to be missing standard headings for: {', '.join(missing_sec)}. ATS parsers categorize your tenure and credentials by looking for standard heading titles. Avoid creative names like 'Where I Have Worked' or embedding titles in graphics.",
            })

        # 3. Missing Contact Info
        contact = results["contact_info"]
        if not contact["has_email"] or not contact["has_phone"]:
            missing_c = []
            if not contact["has_email"]:
                missing_c.append("Email Address")
            if not contact["has_phone"]:
                missing_c.append("Phone Number")
            warnings_found.append({
                "type": "Contact Info Warning",
                "title": f"Unparsed Contact Details: {', '.join(missing_c)}",
                "text": "No plain-text email or phone number was detected. Ensure contact details are placed in the main body text at the top, rather than hidden inside Word header/footer bands which many ATS parsers discard.",
            })

        # 4. Length / Brevity
        if results["word_count"] < 250:
            warnings_found.append({
                "type": "Length Warning",
                "title": "Resume Is Too Brief (<250 words)",
                "text": "A standard professional resume typically contains between 350 and 1,000 words. Add detailed accomplishments and bullet points highlighting your impact.",
            })
        elif results["word_count"] > 1400:
            warnings_found.append({
                "type": "Length Warning",
                "title": "Resume Exceeds Recommended Length (>1400 words)",
                "text": "Your resume is over 1,400 words (likely 3+ pages). Unless you are in academia or executive leadership, aim for a punchy 1–2 page format to prevent recruiter scanning fatigue.",
            })

        # Render warnings
        if warnings_found:
            for w in warnings_found:
                st.markdown(
                    f"""
                    <div class="warning-alert-card">
                        <strong>🚨 {w['title']}</strong><br>
                        {w['text']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="info-alert-card">
                    <strong>✅ Clean Formatting Audit</strong><br>
                    No structural formatting red flags detected. Standard section headers, readable text encoding, and contact details are all in place!
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # --- DETAILED DASHBOARD TABS ---
        tab_skills, tab_breakdown, tab_sections, tab_suggestions = st.tabs(
            [
                "🎯 Matched & Missing Skills",
                "📊 Score Breakdown & Metrics",
                "📋 Section & Contact Audit",
                "💡 Suggestions for Improvement",
            ]
        )

        # TAB 1: MATCHED AND MISSING SKILLS
        with tab_skills:
            st.markdown("### 🎯 Job-Specific Skill Coverage")

            col_m1, col_m2 = st.columns(2, gap="large")
            with col_m1:
                st.markdown(
                    f"#### ✅ Matched Target Skills ({len(results['matched_skills'])})"
                )
                st.caption("Skills found in both the target job description and your resume:")
                st.markdown(
                    render_skills_cloud(results["matched_skills"], "matched"),
                    unsafe_allow_html=True,
                )

            with col_m2:
                st.markdown(
                    f"#### ⚠️ Missing Target Skills ({len(results['missing_skills'])})"
                )
                st.caption("Key requirements from the job description not detected in your resume:")
                st.markdown(
                    render_skills_cloud(results["missing_skills"], "missing"),
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"#### ➕ Additional Skills on Resume ({len(results['additional_skills'])})"
            )
            st.caption("Skills you possess that provide extra breadth beyond the job description:")
            st.markdown(
                render_skills_cloud(results["additional_skills"], "extra"),
                unsafe_allow_html=True,
            )

            st.markdown("---")
            st.markdown("### 🔬 Salient Job Keywords (TF-IDF N-Gram Analysis)")
            st.caption(
                "Key industry terms extracted dynamically from the job description using scikit-learn TF-IDF:"
            )

            kw_col1, kw_col2 = st.columns(2, gap="large")
            with kw_col1:
                st.markdown("##### ✅ Present Role Keywords")
                matched_kws = [k[0] for k in results["matched_keywords"]]
                st.markdown(render_skills_cloud(matched_kws, "matched"), unsafe_allow_html=True)

            with kw_col2:
                st.markdown("##### ❌ Missing Role Keywords")
                missing_kws = [k[0] for k in results["missing_keywords"]]
                st.markdown(render_skills_cloud(missing_kws, "missing"), unsafe_allow_html=True)

            # Categorized Breakdown
            if results["categorized_skill_breakdown"]:
                st.markdown("---")
                st.markdown("### 📂 Domain-by-Domain Skill Breakdown")
                for cat, c_data in results["categorized_skill_breakdown"].items():
                    with st.expander(f"📁 {cat} (Matched: {len(c_data['matched'])}, Missing: {len(c_data['missing'])})"):
                        cL, cR = st.columns(2)
                        with cL:
                            st.write("**Matched:**")
                            st.markdown(render_skills_cloud(c_data["matched"], "matched"), unsafe_allow_html=True)
                        with cR:
                            st.write("**Missing:**")
                            st.markdown(render_skills_cloud(c_data["missing"], "missing"), unsafe_allow_html=True)

        # TAB 2: SCORE BREAKDOWN
        with tab_breakdown:
            b = results["score_breakdown"]
            st.markdown("### 🧮 Mathematical Scoring Breakdown")
            st.markdown(
                "Your score is calculated deterministically from four weighted components:"
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric(
                label=f"Skills ({b['skills']['weight']}%)",
                value=f"{b['skills']['score']}%",
                delta=f"{b['skills']['weighted_points']} pts",
            )
            c2.metric(
                label=f"Keywords ({b['keywords']['weight']}%)",
                value=f"{b['keywords']['score']}%",
                delta=f"{b['keywords']['weighted_points']} pts",
            )
            c3.metric(
                label=f"Sections ({b['sections']['weight']}%)",
                value=f"{b['sections']['score']}%",
                delta=f"{b['sections']['weighted_points']} pts",
            )
            c4.metric(
                label=f"Hygiene ({b['hygiene']['weight']}%)",
                value=f"{b['hygiene']['score']}%",
                delta=f"{b['hygiene']['weighted_points']} pts",
            )

            st.markdown("<br>", unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2, gap="large")
            with col_f1:
                st.markdown("#### 📐 Calculation Summary")
                st.markdown(
                    f"""
                    - **Skill Match**: `{b['skills']['score']}% × 0.50 = {b['skills']['weighted_points']} pts`  
                      *{b['skills']['details']}*
                    - **TF-IDF Keywords**: `{b['keywords']['score']}% × 0.25 = {b['keywords']['weighted_points']} pts`  
                      *{b['keywords']['details']}*
                    - **Sections**: `{b['sections']['score']}% × 0.15 = {b['sections']['weighted_points']} pts`  
                      *{b['sections']['details']}*
                    - **Hygiene & Action Verbs**: `{b['hygiene']['score']}% × 0.10 = {b['hygiene']['weighted_points']} pts`  
                      *{b['hygiene']['details']}*
                    - **Total Alignment**: **{results['total_score']}%**
                    """
                )

            with col_f2:
                st.markdown("#### 📏 Resume Vital Signs")
                st.markdown(
                    f"""
                    - **Word Count**: `{results['word_count']}` words
                    - **Unique Action Verbs**: `{results['verbs_data']['unique_count']}`
                    - **Action Verb Density**: `{results['verbs_data']['density_pct']}%`
                    - **Email**: `{results['contact_info']['email'] or 'Not Detected ⚠️'}`
                    - **Phone**: `{results['contact_info']['phone'] or 'Not Detected ⚠️'}`
                    - **LinkedIn**: `{results['contact_info']['linkedin'] or 'Not Detected'}`
                    - **GitHub**: `{results['contact_info']['github'] or 'Not Detected'}`
                    """
                )

        # TAB 3: SECTIONS AUDIT
        with tab_sections:
            st.markdown("### 📋 Resume Section Parser Audit")
            st.markdown(
                "Applicant Tracking Systems scan for standard section headers to parse employment dates, job titles, and educational history into database records."
            )

            s_col1, s_col2 = st.columns(2, gap="large")
            sec_items = list(results["sections"].items())
            midpoint = (len(sec_items) + 1) // 2

            def render_sec_block(items):
                for name, data in items:
                    pill = (
                        '<span class="status-found-pill">✓ DETECTED</span>'
                        if data["found"]
                        else '<span class="status-missing-pill">✕ MISSING</span>'
                    )
                    snippet = f"<span style='color: #64748b; font-size: 0.8rem;'>({data['matched_term']})</span>" if data["matched_term"] else ""
                    html = f"""
                    <div class="section-audit-row">
                        <div>
                            <strong>{name}</strong> {snippet}
                        </div>
                        <div>{pill}</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)

            with s_col1:
                render_sec_block(sec_items[:midpoint])
            with s_col2:
                render_sec_block(sec_items[midpoint:])

        # TAB 4: SUGGESTIONS FOR IMPROVEMENT
        with tab_suggestions:
            st.markdown("### 💡 Prioritized Suggestions for Improvement")
            st.caption(
                "Targeted, honest suggestions based directly on your resume's gap analysis and formatting audit:"
            )

            if results["suggestions"]:
                for rec in results["suggestions"]:
                    render_recommendation_card(rec)
            else:
                st.success("🎉 Excellent! No critical gaps or missing sections were identified.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### ⚡ Impact Action Verbs Found in Resume")
            if results["verbs_data"]["unique_verbs"]:
                verbs_str = ", ".join(results["verbs_data"]["unique_verbs"])
                st.info(f"**Identified Power Verbs**: {verbs_str}")
            else:
                st.warning("No strong accomplishment verbs were detected. Try beginning bullet points with active verbs like *Engineered, Spearheaded, Accelerated, Automated, Optimized*.")

            st.markdown("---")
            st.markdown("### 📥 Export Audit Report")
            report_content = f"""# ATS Resume Alignment Audit Report
Document: {resume_label}
Overall Alignment Score: {results['total_score']}%

## Mathematical Breakdown:
- Skill Coverage (50%): {b['skills']['score']}% ({b['skills']['weighted_points']} pts)
- Keyword Fit (25%): {b['keywords']['score']}% ({b['keywords']['weighted_points']} pts)
- Section Audit (15%): {b['sections']['score']}% ({b['sections']['weighted_points']} pts)
- Hygiene & Verbs (10%): {b['hygiene']['score']}% ({b['hygiene']['weighted_points']} pts)

## Matched Skills ({len(results['matched_skills'])}):
{', '.join(results['matched_skills']) if results['matched_skills'] else 'None'}

## Missing Target Skills ({len(results['missing_skills'])}):
{', '.join(results['missing_skills']) if results['missing_skills'] else 'None'}

## Formatting & Section Checklist:
{chr(10).join([f"- {k}: {'Found' if v['found'] else 'Missing'}" for k, v in results['sections'].items()])}

## Tailored Suggestions:
{chr(10).join([f"- [{s['priority']} Priority] {s['title']}: {s['message']}" for s in results['suggestions']])}

---
Disclaimer: This analysis reflects textual alignment against the target job description and does not guarantee ATS acceptance or interview invitation.
"""
            st.download_button(
                label="📄 Download Markdown Audit Report",
                data=report_content,
                file_name="ats_resume_audit.md",
                mime="text/markdown",
            )


if __name__ == "__main__":
    main()
