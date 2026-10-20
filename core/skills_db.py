"""
Curated skills taxonomy and normalization database for ATS Resume Analyzer.
Contains categorized technical and soft skills, synonyms/aliases, and matching logic.
"""

import re
from typing import Dict, List, Set, Tuple

# Comprehensive taxonomy categorized for structured reporting
SKILL_CATEGORIES: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL",
        "Bash", "Shell", "PowerShell", "Dart", "Perl", "Haskell", "Elixir", "Lua", "HTML5", "CSS3"
    ],
    "Frameworks & Web Technologies": [
        "React", "React.js", "Angular", "Vue.js", "Next.js", "Nuxt.js", "Svelte",
        "Node.js", "Express.js", "NestJS", "Django", "Flask", "FastAPI",
        "Spring Boot", "Spring", "ASP.NET", ".NET Core", "Ruby on Rails", "Laravel",
        "GraphQL", "RESTful APIs", "REST API", "gRPC", "WebSockets", "Tailwind CSS",
        "Bootstrap", "Material-UI", "Redux", "Zustand", "Webpack", "Vite"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "Google Cloud", "GCP",
        "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Jenkins", "GitHub Actions",
        "GitLab CI", "CI/CD", "Helm", "Prometheus", "Grafana", "Linux", "Unix",
        "CloudFormation", "Serverless", "Nginx", "Apache", "ArgoCD", "Pulumi"
    ],
    "Databases & Storage": [
        "PostgreSQL", "Postgres", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra",
        "DynamoDB", "Oracle Database", "Microsoft SQL Server", "Elasticsearch", "Snowflake",
        "BigQuery", "Firebase", "Neo4j", "Supabase", "Prisma", "SQLAlchemy"
    ],
    "AI, ML & Data Science": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "NLP",
        "Natural Language Processing", "Computer Vision", "Generative AI", "LLM", "LLMs",
        "Large Language Models", "Prompt Engineering", "PyTorch", "TensorFlow", "Keras",
        "Scikit-Learn", "Pandas", "NumPy", "OpenCV", "Hugging Face", "LangChain",
        "LlamaIndex", "Apache Spark", "Apache Kafka", "Airflow", "ETL", "Tableau",
        "Power BI", "Data Modeling", "Statistical Analysis"
    ],
    "Architecture & Methodologies": [
        "Microservices", "System Design", "Agile", "Scrum", "Kanban", "Jira",
        "Git", "GitHub", "GitLab", "Test-Driven Development", "TDD", "Unit Testing",
        "Clean Code", "Design Patterns", "Object-Oriented Programming", "OOP",
        "Functional Programming", "Domain-Driven Design", "DDD", "Event-Driven Architecture",
        "SDLC", "Code Review", "API Design", "Security Best Practices", "OAuth", "JWT"
    ],
    "Soft Skills & Leadership": [
        "Leadership", "Mentoring", "Code Review", "Communication", "Problem Solving",
        "Critical Thinking", "Cross-Functional Collaboration", "Team Leadership",
        "Project Management", "Stakeholder Management", "Time Management", "Adaptability",
        "Analytical Thinking", "Ownership", "Public Speaking", "Documentation"
    ]
}

# Alias/normalization map: maps variation -> canonical standard name
SKILL_ALIASES: Dict[str, str] = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "golang": "Go",
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angularjs": "Angular",
    "angular": "Angular",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "expressjs": "Express.js",
    "express": "Express.js",
    "k8s": "Kubernetes",
    "kube": "Kubernetes",
    "kubernetes": "Kubernetes",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "google cloud": "Google Cloud",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "tf": "Terraform",
    "terraform": "Terraform",
    "docker": "Docker",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "generative ai": "Generative AI",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "tdd": "Test-Driven Development",
    "test driven development": "Test-Driven Development",
    "oop": "Object-Oriented Programming",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "ci-cd": "CI/CD",
    "rest api": "RESTful APIs",
    "restful api": "RESTful APIs",
    "rest apis": "RESTful APIs",
    "restful apis": "RESTful APIs",
    "rest": "RESTful APIs",
    "scikit learn": "Scikit-Learn",
    "scikitlearn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "dotnet": ".NET Core",
    ".net": ".NET Core",
    ".net core": ".NET Core",
}

# Words requiring strict token boundary or casing to avoid common false positives
# e.g., "Go", "C", "R" should not match common english words "go", "c", "r"
SPECIAL_SHORT_SKILLS: Dict[str, str] = {
    r"\b[Gg]o\b|\b[Gg]olang\b": "Go",
    r"(?<![a-zA-Z0-9])C\+\+(?![a-zA-Z0-9+])": "C++",
    r"(?<![a-zA-Z0-9])C#(?![a-zA-Z0-9#])|\b[Cc]-sharp\b": "C#",
    r"(?<![A-Za-z0-9])C(?![A-Za-z0-9+#])": "C",  # Strict isolated C
    r"(?<![A-Za-z0-9])R(?![A-Za-z0-9])": "R",    # Strict isolated R
    r"(?<![a-zA-Z0-9])\.NET\b|(?<![a-zA-Z0-9])\.NET Core\b": ".NET Core",
    r"\bCI/CD\b|\bCI-CD\b": "CI/CD",
}


def get_all_canonical_skills() -> Set[str]:
    """Returns a flat set of all unique canonical skills across all categories."""
    all_skills = set()
    for skills in SKILL_CATEGORIES.values():
        for skill in skills:
            canonical = SKILL_ALIASES.get(skill.lower(), skill)
            all_skills.add(canonical)
    return all_skills


def normalize_skill_name(skill: str) -> str:
    """Normalizes any skill variation to its canonical title."""
    clean = skill.strip().lower()
    return SKILL_ALIASES.get(clean, skill.strip())


def get_skill_category(skill_name: str) -> str:
    """Finds which category a given skill belongs to."""
    canonical = normalize_skill_name(skill_name)
    for category, skills in SKILL_CATEGORIES.items():
        canonical_skills = [normalize_skill_name(s) for s in skills]
        if canonical in canonical_skills or skill_name in skills:
            return category
    return "Other Technical / Domain"


def extract_skills_from_text(text: str) -> Dict[str, Set[str]]:
    """
    Extracts recognized skills from text, categorized by domain.
    Returns: Dict[category_name -> Set[canonical_skill_names]]
    """
    if not text:
        return {cat: set() for cat in SKILL_CATEGORIES.keys()}

    found_skills_by_cat: Dict[str, Set[str]] = {cat: set() for cat in SKILL_CATEGORIES.keys()}
    found_skills_by_cat["Other Technical / Domain"] = set()
    lowered_text = text.lower()

    # 1. Check special short skills with regex
    for pattern, canonical in SPECIAL_SHORT_SKILLS.items():
        if re.search(pattern, text):
            cat = get_skill_category(canonical)
            found_skills_by_cat[cat].add(canonical)

    # 2. Check full category items
    for category, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            if skill in ["C", "Go", "R", "C#", "C++", ".NET Core", "CI/CD"]:
                continue  # Handled by special patterns

            pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9])"
            if re.search(pattern, lowered_text):
                canonical = normalize_skill_name(skill)
                found_skills_by_cat[category].add(canonical)

    # 3. Check alias mapping explicitly
    for alias, canonical in SKILL_ALIASES.items():
        if alias in ["c", "go", "r", "ai"]:  # Avoid ambiguous short tokens
            continue
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(alias) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, lowered_text):
            cat = get_skill_category(canonical)
            found_skills_by_cat[cat].add(canonical)

    return found_skills_by_cat
