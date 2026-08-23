# AgentCrashLab — Architecture

## System Overview

AgentCrashLab is structured as a three-tier application:

1. **Frontend** — React SPA served by Vite
2. **Backend** — FastAPI REST API
3. **Database** — PostgreSQL 16

All components run in Docker containers orchestrated by Docker Compose.

## Data Flow

```
User → Frontend (React)
         ↓ fetch()
       Backend (FastAPI)
         ↓ SQLAlchemy
       PostgreSQL
```

## Backend Architecture

The backend follows clean architecture principles:

```
app/
├── api/        → HTTP handlers (thin layer, delegates to services)
├── core/       → Configuration, database engine, shared utilities
├── models/     → SQLAlchemy ORM models (data layer)
├── schemas/    → Pydantic models (validation + serialization)
├── services/   → Business logic (orchestration layer)
├── evaluators/ → Deterministic failure evaluators (Phase 3+)
├── sandbox/    → Isolated execution environment (Phase 2+)
├── scenarios/  → Scenario generation engine (Phase 3+)
├── agents/     → Agent provider abstraction (Phase 2+)
├── analysis/   → Failure forensics (Phase 4+)
├── repair/     → Fix generation engine (Phase 7+)
├── regression/ → Regression testing engine (Phase 8+)
└── scoring/    → Reliability scoring model (Phase 9+)
```

## Database Schema

### Core Tables (Phase 1)

- `agents` — registered AI agents
- `agent_versions` — versioned agent configurations
- `tools` — tools available to each agent version
- `scenarios` — test scenarios
- `test_runs` — execution records
- `execution_steps` — individual steps in a trace
- `failures` — detected and classified failures

### Relationships

```
Agent 1:N AgentVersion 1:N Tool
                        1:N TestRun 1:N ExecutionStep
                                    1:N Failure
Scenario 1:N TestRun
```

## Security

- All agent execution happens in Docker containers
- Mock/synthetic data only — no real payments, emails, or customer data
- Sandbox enforces execution timeout and tool-call limits
- No secrets in source code
- Environment variables for all configuration
