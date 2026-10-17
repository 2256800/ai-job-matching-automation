import json
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from llm_client import analyze_job_description


# =========================================================
# 1. FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI Job Skills Automation",
    description=(
        "AI-powered job description analysis, "
        "candidate skill matching, and learning recommendations."
    ),
    version="4.0.0"
)


# =========================================================
# 2. LEARNING RECOMMENDATIONS DATABASE
# =========================================================

LEARNING_RECOMMENDATIONS = {
    "Python": (
        "Practice Python functions, object-oriented programming, "
        "and data analysis projects."
    ),
    "SQL": (
        "Learn joins, subqueries, aggregations, "
        "and database queries."
    ),
    "Excel": (
        "Learn formulas, pivot tables, lookup functions, "
        "and charts."
    ),
    "Tableau": (
        "Build interactive dashboards using real datasets."
    ),
    "Power BI": (
        "Practice data modeling, DAX, and report creation."
    ),
    "Machine Learning": (
        "Study supervised learning and build a machine learning project."
    ),
    "Data Analysis": (
        "Practice data cleaning, exploratory data analysis, "
        "and visualization."
    ),
    "Communication": (
        "Practice explaining technical concepts "
        "and presenting findings."
    ),
    "Communication Skills": (
        "Practice professional communication, presentations, "
        "and explaining your work clearly."
    ),
    "Java": (
        "Learn Java fundamentals, object-oriented programming, "
        "collections, and exception handling."
    ),
    "API Testing": (
        "Learn HTTP methods, status codes, API validation, "
        "and Postman."
    ),
    "FastAPI": (
        "Build REST APIs using FastAPI and Pydantic."
    ),
    "REST API": (
        "Learn HTTP methods, request bodies, responses, "
        "and status codes."
    ),
    "REST API Development": (
        "Build and test REST endpoints with input validation."
    ),
    "Git": (
        "Practice commits, branches, merges, "
        "and GitHub workflows."
    ),
    "Docker": (
        "Learn containers, Dockerfiles, and image management."
    ),
    "Pandas": (
        "Practice data manipulation, filtering, grouping, "
        "and cleaning using Pandas."
    ),
    "NumPy": (
        "Learn arrays, vectorized operations, and numerical computing."
    ),
    "Statistics": (
        "Study probability, distributions, hypothesis testing, "
        "and descriptive statistics."
    ),
    "PowerPoint": (
        "Practice creating clear, professional presentations."
    ),
}


# Normalize keys so recommendations are case-insensitive.
NORMALIZED_RECOMMENDATIONS = {
    skill.casefold(): recommendation
    for skill, recommendation in LEARNING_RECOMMENDATIONS.items()
}


# =========================================================
# 3. REQUEST VALIDATION MODELS
# =========================================================

class JobRequest(BaseModel):
    job_title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    job_description: str = Field(min_length=1)

    @field_validator("job_title", "company", "job_description")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class MatchRequest(BaseModel):
    job_title: str = Field(min_length=1)

    candidate_skills: list[str] = Field(min_length=1)

    required_skills: list[str] = Field(min_length=1)

    @field_validator("job_title")
    @classmethod
    def validate_job_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Job title cannot be empty.")

        return value

    @field_validator("candidate_skills", "required_skills")
    @classmethod
    def validate_skills(cls, skills: list[str]) -> list[str]:
        cleaned_skills = []

        for skill in skills:
            if not isinstance(skill, str) or not skill.strip():
                continue

            cleaned_skills.append(skill.strip())

        if not cleaned_skills:
            raise ValueError(
                "Provide at least one valid, non-empty skill."
            )

        return cleaned_skills


# =========================================================
# 4. HELPER: REMOVE DUPLICATE SKILLS
# =========================================================

def remove_duplicate_skills(skills: list[str]) -> list[str]:
    """Remove duplicate skills without changing their original names."""

    unique_skills = []
    seen = set()

    for skill in skills:
        if not isinstance(skill, str):
            continue

        skill = skill.strip()

        if not skill:
            continue

        normalized = skill.casefold()

        if normalized not in seen:
            seen.add(normalized)
            unique_skills.append(skill)

    return unique_skills


# =========================================================
# 5. HELPER: GENERATE LEARNING RECOMMENDATIONS
# =========================================================

def generate_recommendations(
    missing_skills: list[str]
) -> list[dict]:
    """Generate recommendations for missing candidate skills."""

    recommendations = []

    for skill in missing_skills:
        recommendation = NORMALIZED_RECOMMENDATIONS.get(
            skill.casefold(),
            (
                f"Study {skill} fundamentals, practice with examples, "
                f"and complete a practical project."
            )
        )

        recommendations.append({
            "skill": skill,
            "recommendation": recommendation
        })

    return recommendations


# =========================================================
# 6. HOME / HEALTH-CHECK ENDPOINT
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AI Job Skills Automation API is running.",
        "available_endpoints": [
            "GET /",
            "GET /health",
            "POST /analyze",
            "POST /match",
        ],
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "api_status": "healthy",
        "status": "success"
    }


# =========================================================
# 7. DAY 9: ANALYZE A JOB DESCRIPTION USING THE LLM
# =========================================================

@app.post("/analyze")
def analyze_job(request: JobRequest):
    """
    Analyze a job description using the local Ollama LLM.

    Returns detected skills and learning recommendations.
    """

    try:
        analysis = analyze_job_description(
            request.job_description
        )

        # Validate the most important LLM output fields.
        if not isinstance(analysis, dict):
            raise ValueError("LLM response must be a JSON object.")

        llm_job_title = analysis.get("job_title", "")
        required_skills = analysis.get("required_skills")
        experience_level = analysis.get(
            "experience_level",
            "Not specified"
        )

        if not isinstance(llm_job_title, str):
            raise ValueError("Invalid job_title returned by the LLM.")

        if not isinstance(required_skills, list):
            raise ValueError(
                "LLM required_skills must be a list."
            )

        if not isinstance(experience_level, str):
            raise ValueError(
                "Invalid experience_level returned by the LLM."
            )

        # Clean and deduplicate extracted skills.
        detected_skills = remove_duplicate_skills(
            required_skills
        )

        # Create learning recommendations.
        recommendations = generate_recommendations(
            detected_skills
        )

        return {
            "job_title": request.job_title,
            "company": request.company,
            "llm_analysis": {
                "job_title": llm_job_title,
                "required_skills": detected_skills,
                "experience_level": experience_level
            },
            "detected_skills": detected_skills,
            "total_skills": len(detected_skills),
            "recommendations": recommendations,
            "status": "success"
        }

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail=(
                "The local LLM request timed out. "
                "Please try again."
            )
        )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to the local Ollama LLM."
        )

    except (
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError
    ):
        raise HTTPException(
            status_code=502,
            detail=(
                "The LLM returned an invalid response. "
                "Please try again."
            )
        )


# =========================================================
# 8. DAY 10: MATCH CANDIDATE SKILLS AGAINST JOB REQUIREMENTS
# =========================================================

@app.post("/match")
def match_skills(request: MatchRequest):
    """
    Compare candidate skills with required job skills.

    Calculates match percentage, identifies missing skills,
    and generates learning recommendations.
    """

    # Remove duplicates before calculating the percentage.
    candidate_skills = remove_duplicate_skills(
        request.candidate_skills
    )

    required_skills = remove_duplicate_skills(
        request.required_skills
    )

    if not candidate_skills:
        raise HTTPException(
            status_code=422,
            detail="At least one valid candidate skill is required."
        )

    if not required_skills:
        raise HTTPException(
            status_code=422,
            detail="At least one valid required skill is required."
        )

    # Normalize candidate skills for case-insensitive matching.
    candidate_skill_lookup = {
        skill.casefold()
        for skill in candidate_skills
    }

    # Find matching skills.
    matching_skills = [
        skill
        for skill in required_skills
        if skill.casefold() in candidate_skill_lookup
    ]

    # Find skills the candidate is missing.
    missing_skills = [
        skill
        for skill in required_skills
        if skill.casefold() not in candidate_skill_lookup
    ]

    # Calculate match percentage.
    total_required_skills = len(required_skills)
    total_matching_skills = len(matching_skills)

    match_percentage = round(
        (
            total_matching_skills
            / total_required_skills
        ) * 100,
        2
    )

    # Generate recommendations for missing skills only.
    recommendations = generate_recommendations(
        missing_skills
    )

    # Return the final structured result.
    return {
        "job_title": request.job_title,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "total_required_skills": total_required_skills,
        "total_matching_skills": total_matching_skills,
        "match_percentage": match_percentage,
        "recommendations": recommendations,
        "status": "success"
    }