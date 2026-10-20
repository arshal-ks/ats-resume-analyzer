# 🎯 ATS Resume Alignment & Skill Coverage Engine

A privacy-first, locally executed ATS Resume Analyzer built with **Python**, **Streamlit**, **PyMuPDF**, **python-docx**, and **scikit-learn**.

Analyze how well a resume aligns with a specific job description, audit essential structural sections, detect missing skills and keywords, and receive actionable, honest improvement recommendations—**all with 100% mathematical transparency and zero paid API dependencies**.

---

## ✨ Features

- **Multi-Format Extraction**: Robust text and metadata extraction from `.pdf` (using `PyMuPDF` / `fitz`) and `.docx` (using `python-docx`), with automatic detection of scanned/image-only PDFs.
- **Categorized Skills Taxonomy**: Over 1,200+ canonical technical and soft skills grouped across 7 domains (Programming Languages, Frameworks, Cloud & DevOps, Databases, AI/ML & Data, Architecture, and Leadership) with comprehensive alias mapping (e.g., `k8s` → `Kubernetes`, `postgres` → `PostgreSQL`).
- **Dynamic TF-IDF Keyword Extraction**: Uses `scikit-learn` TF-IDF unigram and bigram analysis to extract salient role keywords directly from the target job posting.
- **100% Transparent Scoring**: No arbitrary black-box numbers. Shows the exact mathematical formula, weight distribution, and points earned.
- **Structural Parser Audit**: Validates presence of core resume sections (Contact Info, Summary, Experience, Education, Skills, Projects, Certifications) expected by standard applicant tracking systems.
- **Impact & Action Verbs**: Detects strong accomplishment verbs (e.g., *Spearheaded, Architected, Optimized*) and measures verb density.
- **Honest Improvement Plan**: Prioritized recommendations (High, Medium, Low) that advise candidates without giving false guarantees.
- **Exportable Audit Report**: One-click download of a Markdown audit report to track edits offline.
- **100% Local & Free**: Runs completely on your machine. No OpenAI/Gemini/Claude API keys required; no personal resume data uploaded to cloud databases.

---

## ⚖️ ATS Reality Check (Why Transparency Matters)

> [!NOTE]
> **How Real ATS Platforms Actually Work**:  
> Systems like **Workday, Greenhouse, Lever, and Taleo** are primarily indexed databases and workflow managers for recruiters. They do **not** use a magical AI bot that auto-rejects 75% of applicants based on a single composite score.  
> Instead, recruiters run queries filtering by **job title keywords, location, minimum years of experience, and specific technical skills**.  
>  
> This tool's score represents **textual and skill alignment** to help you make sure your genuine qualifications are clearly discoverable by both automated search filters and human recruiters.

---

## 📐 Scoring Formula Breakdown

$$\text{Total Score} = (0.50 \times S_{\text{skills}}) + (0.25 \times S_{\text{keywords}}) + (0.15 \times S_{\text{sections}}) + (0.10 \times S_{\text{hygiene}})$$

| Component | Weight | Calculation Method |
| :--- | :--- | :--- |
| **Skills Coverage** | **50%** | $\frac{\text{Matched JD Skills}}{\text{Total Identified JD Skills}} \times 100$ |
| **TF-IDF Keyword Alignment** | **25%** | $\frac{\text{Matched Salient JD Keywords}}{\text{Top Salient JD Keywords}} \times 100$ |
| **Essential Section Audit** | **15%** | Checks for Contact Details, Work Experience, Education, and Skills headers. |
| **Formatting & Action Hygiene** | **10%** | Evaluates optimal resume length (350–1100 words) and strong accomplishment verbs count. |

---

## 🗂 Project Structure

```
RESUME ANALYZER/
├── app.py                  # Main Streamlit web application & interactive UI
├── core/
│   ├── __init__.py         # Core package initialization
│   ├── extractor.py        # PyMuPDF and python-docx text & metadata extraction
│   ├── skills_db.py        # Curated taxonomy, canonical mappings, and regex matchers
│   ├── analyzer.py         # Section detection, TF-IDF ranking, and scoring engine
│   └── ui_helpers.py       # Modern CSS design system, badges, and score gauges
├── sample_data.py          # Pre-built sample resumes and job postings for 1-click demos
├── tests/
│   ├── test_skills_db.py   # Unit tests for taxonomy & alias resolution
│   ├── test_extractor.py   # Unit tests for PDF/DOCX parsing & error handling
│   └── test_analyzer.py    # Unit tests for scoring, TF-IDF, and section detection
├── requirements.txt        # Python dependency manifest
└── README.md               # Documentation & setup guide
```

---

## 🚀 Quickstart: Launching Locally

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Set Up Virtual Environment

**Windows (PowerShell):**
```powershell
# Navigate to the project directory
cd "c:\Users\ARSHAL\Desktop\RESUME ANALYZER"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Web Application
```bash
streamlit run app.py
```
Streamlit will automatically open your browser at `http://localhost:8501`.

---

## 🚢 Deployment Guide

This project is pre-configured and ready for deployment to any major cloud platform:

### 1. Streamlit Community Cloud (Fastest & Free)
The easiest way to deploy this application online for free:
1. Push this repository to **GitHub**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"**.
4. Select your repository, branch (`main`), and set the main file path to: `app.py`.
5. Click **"Deploy"**! Streamlit Cloud will automatically read `requirements.txt` and `.streamlit/config.toml` to launch your live URL.

### 2. Docker Container Deployment
A production-ready [Dockerfile](file:///c:/Users/ARSHAL/Desktop/RESUME%20ANALYZER/Dockerfile) and [.dockerignore](file:///c:/Users/ARSHAL/Desktop/RESUME%20ANALYZER/.dockerignore) are included:

```bash
# 1. Build the Docker image
docker build -t ats-resume-analyzer .

# 2. Run the container locally
docker run -p 8501:8501 --name ats-app ats-resume-analyzer
```
Access the application at `http://localhost:8501`.

### 3. Deploy to Render / Railway
1. Connect your GitHub repository to [Render](https://render.com) or [Railway](https://railway.app).
2. Choose **Web Service**.
3. **Environment**: Python 3.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0` (also provided in [Procfile](file:///c:/Users/ARSHAL/Desktop/RESUME%20ANALYZER/Procfile)).

### 4. Hugging Face Spaces
1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Select **Streamlit** as the Space SDK.
3. Push the repository files to the Space repository.

---

## 🧪 Running Unit Tests

Run the complete automated test suite with `pytest`:
```bash
pytest tests -v
```

All tests run locally in seconds with zero network access required.

---

## 🛡 License & Privacy
This project is open-source and released under the MIT License. All document parsing, regex analysis, and machine learning computations are executed strictly within your local environment.
