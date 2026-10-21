
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3:latest"


def analyze_job_description(job_description: str) -> dict:
    """
    Analyze a job description using a locally hosted Ollama LLM.

    Returns:
        dict: Job title, required skills, and experience level.

    Raises:
        ValueError: If the input or LLM response is invalid.
        RuntimeError: If Ollama cannot respond successfully.
    """

    # 1. Validate input
    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    # 2. Build the prompt
    prompt = f"""
You are an AI recruitment assistant.

Analyze the following job description:

{job_description}

Return a JSON object containing exactly these fields:

- job_title: string
- required_skills: array of strings
- experience_level: string

Rules:
1. Extract the job title from the description.
2. Identify the important technical and professional skills.
3. If experience is not specified, use "Not specified".
4. Return only valid JSON.
5. Do not include Markdown or explanatory text.
"""

    # 3. Call the local Ollama API
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "format": "json"
            },
            timeout=120
        )

        response.raise_for_status()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "The LLM request timed out. Please try again."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to Ollama. Check that Ollama is running."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Ollama returned an HTTP error: {exc}"
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"An error occurred while calling Ollama: {exc}"
        ) from exc

    # 4. Parse the API response
    try:
        result = response.json()
        content = result["message"]["content"]
        data = json.loads(content)

    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError(
            "Ollama returned an invalid JSON response."
        ) from exc

    # 5. Validate the returned structure
    if not isinstance(data, dict):
        raise ValueError(
            "LLM response must be a JSON object."
        )

    required_fields = {
        "job_title",
        "required_skills",
        "experience_level"
    }

    if not required_fields.issubset(data.keys()):
        raise ValueError(
            "LLM returned an invalid JSON structure."
        )

    # 6. Validate individual fields
    if not isinstance(data["job_title"], str):
        raise ValueError("Invalid job_title.")

    if not isinstance(data["required_skills"], list):
        raise ValueError("Invalid required_skills.")

    if not all(
        isinstance(skill, str) and skill.strip()
        for skill in data["required_skills"]
    ):
        raise ValueError(
            "Skills must be non-empty strings."
        )

    if not isinstance(data["experience_level"], str):
        raise ValueError("Invalid experience_level.")

    # 7. Return the validated result
    return data

