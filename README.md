<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/shield-alert.svg" width="80" alt="Agent Crash Lab Logo">
  
  # Agent Crash Lab
  
  **Break AI agents before they break production.**

  [![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
  [![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Frontend: React](https://img.shields.io/badge/Frontend-React_Vite-61DAFB.svg?logo=react)](https://react.dev/)

</div>

<br />

Agent Crash Lab is a premium, enterprise-grade AI reliability testing platform. It allows developers to deploy, test, and analyze LLM-based autonomous agents against adversarial attacks, ambiguous instructions, and edge-case scenarios in a secure, sandboxed environment.

---

## ⚡ Core Features

- 🎯 **Agent Roster (Bento Box Grid):** Deploy custom target agents, configure system prompts, and manage tool access.
- 🛠 **Scenario Forge:** Automatically synthesize novel attack vectors and edge-cases (e.g., prompt injections, unauthorized escalation, ambiguous requests).
- 💻 **Terminal Trace Viewer:** A highly styled chat/terminal hybrid execution trace. Inspect internal agent thoughts, watch real-time tool executions, and expand JSON payloads in sleek mini-consoles.
- 📊 **System Reliability Reports:** Dynamically aggregate execution data into a beautiful dashboard. View overall pass rates, analyze failure heatmaps by category, and check the agent leaderboard.
- 📉 **Regression Analytics:** Track reliability deltas between agent versions. Audit A/B system prompt modifications with visual diff viewers to ensure patches don't introduce new regressions.

## 🎨 Premium UI / UX

The frontend features a dark-mode cyberpunk aesthetic, heavily utilizing **glassmorphism**, neon glows (cyan/purple), micro-animations, and `lucide-react` iconography for a truly modern, Command Center feel.

---

## 🏗 Architecture

- **Backend:** Python / FastAPI
  - ORM: SQLAlchemy with Alembic for migrations.
  - SQLite database for persistent tracking.
  - Modular sandbox execution environment.
- **Frontend:** React / Vite
  - Typescript enabled.
  - CSS-based design system (`index.css`) for seamless global tokens.

---

## 🚀 Getting Started

### 1. Backend Setup

Navigate to the backend directory and set up your Python environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set up your environment variables by copying the example file:
```bash
cp ../.env.example .env
```

Apply database migrations and seed the initial mock data:
```bash
alembic upgrade head
python fix_db.py
python seed_agents.py
python seed_scenarios.py
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

### 2. Frontend Setup

Open a new terminal, navigate to the frontend directory, and install dependencies:

```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```

Visit **http://localhost:5173** to access the Command Center!

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── core/         # Config and database setup
│   │   ├── models/       # SQLAlchemy DB models
│   │   ├── sandbox/      # Agent execution environment
│   │   ├── schemas/      # Pydantic validation schemas
│   │   └── services/     # Business logic layer
│   └── alembic/          # DB Migrations
│
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components (Sidebar, TraceViewer)
│   │   ├── pages/        # Main route views (Dashboard, Regression, etc.)
│   │   ├── services/     # API integration (api.ts)
│   │   ├── types/        # TypeScript interfaces
│   │   └── index.css     # Global design tokens and glassmorphism styles
```

---

## 🛡 License

This project is licensed under the MIT License.
