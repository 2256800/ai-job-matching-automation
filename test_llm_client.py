import pytest

from llm_client import analyze_job_description


def test_analyze_job_description():
    description = (
        "We need a Python developer with SQL, FastAPI, "
        "REST API development, and machine learning skills."
    )

    result = analyze_job_description(description)

    assert isinstance(result["job_title"], str)
    assert isinstance(result["required_skills"], list)
    assert isinstance(result["experience_level"], str)

    print(result)


def test_empty_job_description():
    with pytest.raises(ValueError):
        analyze_job_description("   ")