# WebPilot AI — Setup & Deployment Guide

## 1. Local Development Setup

### System Prerequisites
- Python 3.12+
- Node.js 18+
- Playwright Chromium browser binaries

### Step 1: Environment Configuration
Create `.env` from template:
```bash
cp .env.example .env
```

Set your preferred LLM provider and API key in `.env`:
```env
LLM_PROVIDER=gemini       # Options: gemini, openai, local
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

### Step 2: Backend Setup
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` to access the dashboard.

---

## 2. Running Automated Tests

Run the full automated test suite (15+ unit & integration tests):
```bash
.\venv\Scripts\python.exe -m pytest
```

---

## 3. Docker Deployment

Deploy full stack via Docker Compose:
```bash
docker-compose up --build
```
Services started:
- **Backend API**: `http://localhost:8000`
- **Frontend Dashboard**: `http://localhost:5173`
- **PostgreSQL Database**: `localhost:5432`
