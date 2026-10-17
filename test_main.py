from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ==========================================
# TEST 1: Root Endpoint
# ==========================================
def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200


# ==========================================
# TEST 2: Health Endpoint
# ==========================================
def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200


# ==========================================
# TEST 3: Successful Skill Matching
# ==========================================
def test_match_skills():
    response = client.post(
        "/match",
        json={
            "job_title": "Data Analyst",
            "candidate_skills": [
                "Excel",
                "SQL",
                "Power BI"
            ],
            "required_skills": [
                "Excel",
                "SQL",
                "Power BI",
                "Python",
                "Tableau"
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_title"] == "Data Analyst"
    assert data["matching_skills"] == [
        "Excel",
        "SQL",
        "Power BI"
    ]
    assert data["missing_skills"] == [
        "Python",
        "Tableau"
    ]
    assert data["total_required_skills"] == 5
    assert data["total_matching_skills"] == 3
    assert data["match_percentage"] == 60
    assert data["status"] == "success"


# ==========================================
# TEST 4: Case-Insensitive Skill Matching
# ==========================================
def test_match_case_insensitive():
    response = client.post(
        "/match",
        json={
            "job_title": "Python Developer",
            "candidate_skills": [
                "python",
                "SQL"
            ],
            "required_skills": [
                "Python",
                "sql"
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["matching_skills"]) == 2
    assert data["missing_skills"] == []
    assert data["match_percentage"] == 100


# ==========================================
# TEST 5: Missing Skills
# ==========================================
def test_match_missing_skills():
    response = client.post(
        "/match",
        json={
            "job_title": "Developer",
            "candidate_skills": [
                "Python"
            ],
            "required_skills": [
                "Python",
                "Docker"
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["matching_skills"] == ["Python"]
    assert data["missing_skills"] == ["Docker"]
    assert data["match_percentage"] == 50


# ==========================================
# TEST 6: Missing Required Fields
# ==========================================
def test_match_missing_fields():
    response = client.post(
        "/match",
        json={
            "job_title": "Data Analyst"
        }
    )

    assert response.status_code == 422


# ==========================================
# TEST 7: Empty Required Skills
# ==========================================
def test_match_empty_required_skills():
    response = client.post(
        "/match",
        json={
            "job_title": "Data Analyst",
            "candidate_skills": [
                "Python",
                "SQL"
            ],
            "required_skills": []
        }
    )

    # The API rejects an empty required-skills list.
    assert response.status_code == 422


# ==========================================
# TEST 8: No Matching Skills
# ==========================================
def test_match_no_matching_skills():
    response = client.post(
        "/match",
        json={
            "job_title": "Java Developer",
            "candidate_skills": [
                "Excel",
                "Tableau"
            ],
            "required_skills": [
                "Java",
                "Python"
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["matching_skills"] == []
    assert data["missing_skills"] == [
        "Java",
        "Python"
    ]
    assert data["match_percentage"] == 0


# ==========================================
# TEST 9: All Required Skills Matched
# ==========================================
def test_match_all_skills():
    response = client.post(
        "/match",
        json={
            "job_title": "Python Developer",
            "candidate_skills": [
                "Python",
                "FastAPI",
                "SQL"
            ],
            "required_skills": [
                "Python",
                "FastAPI",
                "SQL"
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["matching_skills"] == [
        "Python",
        "FastAPI",
        "SQL"
    ]
    assert data["missing_skills"] == []
    assert data["match_percentage"] == 100