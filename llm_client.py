
import json
import requests

from logging_config import logger


# ==========================================
# Ollama Configuration
# ==========================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3:latest"


# ==========================================
# Analyze Job Description
# ==========================================

def analyze_job_description(job_description: str) -> dict:
    """
    Analyze a job description using the Ollama LLM.

    Returns:
        dict: job_title, required_skills, experience_level

    Raises:
        ValueError: Invalid input or invalid JSON response.
        RuntimeError: Request failure or invalid response structure.
    """

    # 1. Validate input
    if not isinstance(job_description, str):
        raise ValueError("Job description must be a string.")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    logger.info("Starting job description analysis")

    # 2. Create the LLM prompt
    prompt = f"""
Analyze the following job description.

Return only a valid JSON object with these fields:
- job_title: string
- required_skills: list of strings
- experience_level: string

Rules:
- job_title must be a string.
- required_skills must be a list of strings.
- experience_level must be a string.
- If experience information is unavailable, use "Not specified".
- Do not include Markdown formatting or explanations.

Job description:
{job_description}
"""

    # 3. Prepare the Ollama request
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "format": "json",
        "stream": False,
    }

    # 4. Send request to Ollama
    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        logger.info("Ollama request completed successfully")

    except requests.exceptions.Timeout as exc:
        logger.error("Ollama request timed out")

        raise RuntimeError(
            "Ollama request timed out. Please try again."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        logger.error(
            "Unable to connect to Ollama: %s",
            type(exc).__name__,
        )

        raise RuntimeError(
            "Cannot connect to Ollama. Check that Ollama is running."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        logger.error("Ollama returned an HTTP error")

        raise RuntimeError(
            "Ollama returned an HTTP error."
        ) from exc

    except requests.exceptions.RequestException as exc:
        logger.error(
            "Ollama request failed: %s",
            type(exc).__name__,
        )

        raise RuntimeError(
            "Failed to communicate with Ollama."
        ) from exc

    # 5. Parse the HTTP response
    try:
        response_data = response.json()

    except (ValueError, AttributeError, TypeError) as exc:
        logger.error("Ollama returned an invalid HTTP response")

        raise ValueError(
            "Ollama returned an invalid JSON response."
        ) from exc

    # 6. Extract the model's content
    try:
        message = response_data.get("message", {})
        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Empty response content")

        result = json.loads(content)

    except (ValueError, AttributeError, TypeError) as exc:
        logger.error(
            "Failed to parse Ollama response: %s",
            type(exc).__name__,
        )

        raise ValueError(
            "Ollama returned an invalid JSON response."
        ) from exc

    # 7. Validate the response structure
    if not isinstance(result, dict):
        logger.error("Ollama response must be a JSON object")

        raise RuntimeError(
            "Ollama response must be a JSON object."
        )

    required_fields = [
        "job_title",
        "required_skills",
        "experience_level",
    ]

    for field in required_fields:
        if field not in result:
            logger.error(
                "Ollama response is missing field: %s",
                field,
            )

            raise RuntimeError(
                f"Ollama response is missing the '{field}' field."
            )

    # 8. Validate job title
    if not isinstance(result["job_title"], str):
        raise RuntimeError(
            "The job_title field must be a string."
        )

    # 9. Validate required skills
    if not isinstance(result["required_skills"], list):
        raise RuntimeError(
            "The required_skills field must be a list."
        )

    if not all(
        isinstance(skill, str)
        for skill in result["required_skills"]
    ):
        raise RuntimeError(
            "Every required skill must be a string."
        )

    # 10. Normalize experience level
    experience_level = result["experience_level"]

    if isinstance(experience_level, (int, float)):
        result["experience_level"] = str(experience_level)

    elif not isinstance(experience_level, str):
        raise RuntimeError(
            "The experience_level field must be a string."
        )

    # 11. Log successful analysis
    logger.info(
        "Job description analysis completed successfully"
    )

    # 12. Return validated result
    return result

