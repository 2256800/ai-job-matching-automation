import pytest
import requests
from unittest.mock import patch

from llm_client import analyze_job_description


def test_analyze_job_description():
    """Test successful job description analysis using Ollama."""

    description = (
        "We need a Python developer with SQL, FastAPI, "
        "REST API development, and machine learning skills."
    )

    result = analyze_job_description(description)

    assert isinstance(result["job_title"], str)
    assert isinstance(result["required_skills"], list)
    assert isinstance(result["experience_level"], str)

    print(result)


def test_ollama_connection_error():
    """Test behavior when Ollama cannot be reached."""

    with patch(
        "llm_client.requests.post",
        side_effect=requests.exceptions.ConnectionError(
            "Connection failed"
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="Cannot connect to Ollama",
        ):
            analyze_job_description(
                "Looking for a Python developer"
            )


def test_ollama_timeout():
    """Test behavior when the LLM request times out."""

    with patch(
        "llm_client.requests.post",
        side_effect=requests.exceptions.Timeout(
            "Request timed out"
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="request timed out",
        ):
            analyze_job_description(
                "Looking for a Python developer"
            )


def test_invalid_llm_json():
    """Test behavior when Ollama returns invalid JSON."""

    mock_response = type(
        "MockResponse",
        (),
        {
            "json": lambda self: {
                "message": {
                    "content": "{invalid json}"
                }
            },
            "raise_for_status": lambda self: None,
        },
    )()

    with patch(
        "llm_client.requests.post",
        return_value=mock_response,
    ):
        with pytest.raises(
            ValueError,
            match="invalid JSON response",
        ):
            analyze_job_description(
                "Looking for a Python developer"
            )