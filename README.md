# Medical Coverage Assistant — HackIAthon Challenge 3

A conversational agent that helps patients understand their medical coverage before visiting a doctor. The patient describes their symptom, the agent identifies the appropriate specialty, calculates the copay based on their insurance plan, and recommends the most convenient hospital within their network.

## Live Demo

[Public agent link](No available)

## Features

- Login with username and password linked to the patient's policy
- Welcome message with policy status and deductible summary
- AI-powered symptom classification into medical specialty
- Exact copay calculation based on contracted plan (basic, medium, premium)
- Hospital recommendations filtered by patient's city
- Detection of expired policies and exhausted deductibles
- Automatic referral to emergency care for critical symptoms
- Conversation history with up to 14 turns of context per session

## Tech Stack

- Backend: Python with FastAPI
- AI: Claude API (claude-opus-4-5)
- Data: JSON files (policies, hospitals, copays, users)
- Frontend: HTML, CSS and vanilla JavaScript
- Deployment: Railway

## Project Structure

```
hackiathon-reto3/
├── data/
│   ├── polizas.json       # Patient policies and data
│   ├── hospitales.json    # Hospital network with cities and specialties
│   ├── copagos.json       # Copay table by specialty and plan
│   └── usuarios.json      # Login credentials
├── main.py                # FastAPI backend with /login and /chat endpoints
├── index.html             # Agent web interface
├── requirements.txt       # Python dependencies
├── Procfile               # Railway deployment config
└── .env                   # Environment variables (not included in repo)
```

## Local Setup

Clone the repository:

```bash
git clone https://github.com/kpaulfran/hackiathon-reto3.git
cd hackiathon-reto3
```

Create and activate virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the `.env` file with your API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Start the server:

```bash
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## Test Credentials

| Username | Password | Plan | City |
|---|---|---|---|
| carlos.mendoza | carlos123 | Premium | Guayaquil |
| maria.torres | maria123 | Medium | Samborondón |
| juan.perez | juan123 | Basic | Quito |
| ana.jimenez | ana123 | Premium (expired) | Quito |
| roberto.salinas | roberto123 | Medium | Milagro |

## Environment Variables

| Variable | Description |
|---|---|
| ANTHROPIC_API_KEY | Anthropic API key |

## Author
Kevin Franco
Alejandra Cruz

Developed for HackIAthon — Viamatica 2025
