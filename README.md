# AI Browser Automation Agent 🤖🌐

Production-ready, autonomous AI Browser Automation Agent built with **FastAPI**, **React**, **Playwright**, and **LLMs (Gemini / OpenAI)**. The agent receives natural-language task instructions, plans step-by-step milestones, inspects web pages via DOM & accessibility trees, executes Playwright browser actions, verifies state changes, automatically recovers from errors, and enforces Human-in-the-Loop (HITL) safety for sensitive actions.

---

## 🌟 Core Features

1. **Natural-Language Task Input & Interactive Dashboard**
   - Enter tasks like *"Search for Python courses and collect top 5 results"*, *"Fill out sample registration form"*, *"Find and download PDF document"*.
   - Live activity timeline, browser viewport preview, step-by-step progress, and structured result viewer.

2. **AI Task Planner & Structured Tool Calling**
   - Decomposes instructions into executable milestones.
   - Selects precise browser actions (`open_url`, `click`, `type`, `select`, `scroll`, `press`, `extract_text`, `screenshot`, `download`) using structured JSON schema.

3. **DOM Analysis & Page Understanding**
   - Inspects interactive elements (buttons, inputs, dropdowns, links, forms, tables) using DOM accessibility properties rather than fragile raw pixel coordinates.

4. **Observe → Plan → Act → Verify → Recover Loop**
   - Continuously monitors page state change after every action.
   - If an action fails, the **Failure Recovery Engine** automatically tries alternative selectors, popup dismissal, scrolling, or page reloads before declaring failure.

5. **Human-in-the-Loop (HITL) Safety Guard**
   - Detects sensitive actions (purchases, payments, emails, account deletions, important form submissions).
   - Pauses execution and prompts the user with an **Approve / Reject** modal dialog in real-time.

6. **Short-Term Task Memory & Result Extraction**
   - Tracks current URL, completed actions, failed retries, and extracted data.
   - Formats final output into structured JSON results.

---

## 🏗 Project Architecture

```
Frontend (React + Vite + Tailwind CSS)
    ↓ (REST & WebSockets)
FastAPI Backend Server
    ↓
Agent Orchestrator
    ├── Task Planner (Gemini / OpenAI LLM)
    ├── Page Analyzer (DOM & Accessibility Parser)
    ├── Browser Controller (Playwright Chromium Engine)
    ├── Action Result Verifier
    ├── Failure Recovery Engine
    └── Human-in-the-Loop Safety System
    ↓
Database (SQLAlchemy + SQLite / PostgreSQL)
```

---

## 🚀 Required Backend & Project Structure

```
/
├── backend/
│   ├── agent/
│   │   ├── planner.py         # AI Task Decomposition & Next Action Selector
│   │   ├── orchestrator.py    # Main Observe->Plan->Act->Verify->Recover Loop
│   │   ├── memory.py          # Short-term Memory & Sensitive Action Guard
│   │   ├── verifier.py        # Action Verification Engine
│   │   └── recovery.py        # Failure Recovery Strategies
│   ├── browser/
│   │   ├── controller.py      # Playwright Browser Context & Lifecycle
│   │   ├── actions.py         # 10+ Low-level Playwright Browser Actions
│   │   ├── page_analyzer.py   # DOM & Accessibility Tree Parser
│   │   └── screenshots.py     # Real-time Screenshot Capture Manager
│   ├── api/
│   │   ├── tasks.py           # REST endpoints for tasks, controls, logs, results
│   │   └── websocket.py       # Live WebSocket Event Streaming Manager
│   ├── models/
│   │   ├── database.py        # Async SQLAlchemy ORM Models
│   │   └── schemas.py         # Pydantic Schemas & Action Definitions
│   ├── config.py              # Environment Configuration
│   └── main.py                # FastAPI Application Entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/        # TaskInput, AgentStatus, BrowserPreview, ActionLog, etc.
│   │   ├── pages/             # Dashboard Layout Page
│   │   └── services/          # Axios API & WebSocket Stream Handlers
│   ├── package.json
│   └── vite.config.js
├── tests/                     # Comprehensive Unit & Integration Test Suite
├── Dockerfile                 # Multi-stage Backend Docker Container
├── docker-compose.yml         # Full Stack Docker Services (Backend, Frontend, Postgres)
└── README.md
```

---

## 🛠 Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Axios.
- **Backend**: Python 3.12, FastAPI, Uvicorn.
- **Browser Automation**: Playwright (Async API, Chromium).
- **AI & LLM**: Google Gemini API (`google-genai`), OpenAI API, Heuristic Rule Fallback.
- **Database**: Async SQLAlchemy, PostgreSQL / SQLite (aiosqlite).
- **Real-Time Communication**: WebSockets (`WS /api/tasks/{task_id}/stream`).

---

## 📦 Quick Start Guide

### 1. Prerequisites
- Python 3.12+
- Node.js 18+
- Git

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt # or pip install fastapi uvicorn playwright ...

# Install Playwright browser binaries
python -m playwright install chromium

# Copy environment template
cp .env.example .env

# Run FastAPI Backend Server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173` to open the AI Agent Dashboard.

---

## 🧪 Running Test Suite

Run all automated unit and integration tests:
```bash
.\venv\Scripts\python.exe -m pytest
```

Included Test Suites:
- `tests/test_database.py`: Database models, relationship mapping, and JSON persistence.
- `tests/test_browser.py`: Playwright browser controller and action execution handlers.
- `tests/test_page_analyzer.py`: DOM parsing, interactive element extraction, and LLM prompt formatting.
- `tests/test_planner.py`: Step decomposition and sequential tool selection logic.
- `tests/test_verifier_recovery.py`: Verification rules and failure recovery fallback strategies.
- `tests/test_memory.py`: Short-term memory tracking and HITL sensitive action detection.
- `tests/test_orchestrator.py`: Full agent execution loop and event callback.
- `tests/test_api.py`: FastAPI REST routes and health check endpoint.

---

## 🐳 Docker Deployment

Run the entire production stack (Backend + Frontend + PostgreSQL) via Docker Compose:
```bash
docker-compose up --build
```
- **Dashboard**: `http://localhost:5173`
- **FastAPI API Documentation**: `http://localhost:8000/docs`

---

## 📄 License
MIT License. Created for AI Browser Automation Agent project.