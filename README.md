# 🔥 AgentCrashLab

> **"Break AI agents before they break production."**

AgentCrashLab is an AI Agent Reliability Testing Platform that allows developers to systematically break, investigate, repair, and prove improvements in AI agent behavior.

## The Problem

AI agents are deployed with impressive demos but fail unpredictably in production. Ambiguous user inputs, adversarial prompts, tool misuse, and environmental failures cause agents to take destructive actions, leak data, or silently fail.

## The Solution

AgentCrashLab provides a **BREAK → INVESTIGATE → REPAIR → PROVE** workflow:

1. **Generate** realistic adversarial test scenarios
2. **Execute** the agent safely in an isolated sandbox
3. **Detect** and classify failures automatically
4. **Analyze** root causes with forensic-level detail
5. **Replay** failures deterministically
6. **Propose** candidate fixes
7. **Test** fixes in the sandbox
8. **Run** regression suites
9. **Prove** reliability improvement with real metrics

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│            React + TypeScript + Vite              │
│         Dark Developer Dashboard (port 3000)      │
└─────────────────┬───────────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────────┐
│                   Backend                        │
│              FastAPI + Python 3.12               │
│      Agents │ Scenarios │ Execution │ Analysis   │
│              Swagger UI (port 8000)              │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│                  PostgreSQL 16                    │
│   agents │ scenarios │ test_runs │ failures      │
└─────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone and enter the project
git clone <repo-url>
cd agentcrashlab

# Copy environment file
cp .env.example .env

# Start everything with Docker Compose
docker compose up --build

# Or use the Makefile
make setup
```

Then open:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Demo Agent

The project comes with a pre-configured **CustomerSupport-v1** demo agent with 6 tools:

| Tool | Description | Destructive |
|------|-------------|:-----------:|
| `get_customer()` | Look up customer info | No |
| `get_order()` | Look up order details | No |
| `check_refund_eligibility()` | Check refund eligibility | No |
| `process_refund()` | Process a refund | ⚠️ **Yes** |
| `send_email()` | Send customer email | No |
| `update_ticket()` | Update support ticket | No |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL 16 |
| Infra | Docker, Docker Compose |

## Project Structure

```
agentcrashlab/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── core/         # Config, database
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── seed.py       # Demo data seeding
│   ├── alembic/          # DB migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── layouts/      # Page layouts
│   │   ├── pages/        # Route pages
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── docs/                 # Documentation
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Development

```bash
# Start services
make up

# View logs
make logs

# Run migrations
make migrate

# Seed demo data
make seed

# Run tests
make test

# Stop everything
make down

# Full reset (destroys DB)
make clean
```

## Roadmap

- [x] Phase 1: Repository, Docker, Backend, Frontend, Database
- [ ] Phase 2: Agent execution engine, Sandbox, Trace engine
- [ ] Phase 3: Scenario engine, 25 scenarios, Evaluators
- [ ] Phase 4: Failure detection, Classification, Forensics
- [ ] Phase 5: Dashboard pages, Test runs, Failure detail
- [ ] Phase 6: Replay
- [ ] Phase 7: Repair suggestions
- [ ] Phase 8: Regression testing
- [ ] Phase 9: Reliability scoring
- [ ] Phase 10: Demo mode, Polish, Documentation

## License

MIT
