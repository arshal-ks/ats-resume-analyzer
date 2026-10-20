# ATS Resume Analyzer 📄

An ATS-friendly resume analyzer that compares a resume with a job description, identifies missing keywords, and provides suggestions to improve a resume.

## Features

- Upload resumes in PDF or DOCX format
- Analyze resumes against job descriptions
- Calculate a resume–job description similarity score
- Identify missing keywords and skills
- Provide suggestions for resume improvement
- Simple and user-friendly interface

## Tech Stack

- Python
- Streamlit
- PyMuPDF
- python-docx
- scikit-learn

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/ats-resume-analyzer.git
cd ats-resume-analyzer
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

## How to Use

1. Start the application.
2. Upload your resume.
3. Paste the job description.
4. Run the analysis.
5. Review the match score, missing keywords, and suggestions.

## Future Improvements

- Downloadable analysis reports
- Improved skill extraction
- Resume formatting recommendations
- Online deployment

## Disclaimer

This tool provides estimates and general recommendations. It does not guarantee that a resume will pass any specific employer's ATS.
