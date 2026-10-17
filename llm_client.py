import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3:latest"


def analyze_job_description(job_description: str) -> dict:
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    prompt = f"""
You are an AI recruitment assistant.

Analyze this job description:
{job_description}

Return a JSON object with exactly these fields:
- job_title: string
- required_skills: array of strings
- experience_level: string

If experience is not specified, use "Not specified".
Return only JSON without Markdown or explanatory text.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "format": "json"
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()
    content = result["message"]["content"]

    # Convert the model's JSON string into a Python dictionary.
    import json
    data = json.loads(content)

    # Validate the basic output structure.
    required_fields = {
        "job_title",
        "required_skills",
        "experience_level"
    }

    if not isinstance(data, dict) or not required_fields.issubset(data):
        raise ValueError("LLM returned an invalid JSON structure")

    if not isinstance(data["job_title"], str):
        raise ValueError("Invalid job_title")

    if not isinstance(data["required_skills"], list):
        raise ValueError("Invalid required_skills")

    if not all(isinstance(skill, str) for skill in data["required_skills"]):
        raise ValueError("Skills must be strings")

    if not isinstance(data["experience_level"], str):
        raise ValueError("Invalid experience_level")

    return data