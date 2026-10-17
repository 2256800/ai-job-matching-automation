# AI Job Description Analyzer and Candidate Skill Matching System

## 📌 Project Overview

This project is an AI-powered job analysis and candidate skill-matching system.
It analyzes job descriptions, extracts required skills using a Large Language Model (LLM),
compares candidate skills with job requirements, calculates a match percentage,
and recommends learning resources for missing skills.

## 🚀 Features

- AI-based job description analysis
- Automatic extraction of required skills
- Candidate skill matching
- Match percentage calculation
- Identification of missing skills
- Learning recommendations for missing skills
- REST API integration using FastAPI
- Automated testing using Pytest
- Workflow automation using n8n
- Local LLM integration using Ollama

## 🛠️ Technologies Used

- Python
- FastAPI
- Ollama
- Llama 3
- Pydantic
- Requests
- Pytest
- n8n
- REST APIs

## 🏗️ Architecture

```text
User
  |
  v
n8n Workflow
  |
  v
FastAPI Application
  |
  +----------------------+
  |                      |
  v                      v
/analyze                /match
  |                      |
  v                      v
Ollama LLM          Skill Matching
  |                      |
  v                      v
Extract Skills      Calculate Match %
  |                      |
  v                      v
Analysis Result     Missing Skills
                         |
                         v
                Learning Recommendations