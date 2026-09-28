# AI Factory — GDES Engineering Platform

## Overview

The GDES AI Factory is a production-quality AI Software Factory capable of performing **90-95% of the engineering workflow** with minimal human intervention. It serves as the permanent engineering infrastructure for the Glomerular Disease Expert System (GDES).

---

## Mission

Build and operate an AI Software Factory that:

- Minimizes manual engineering work
- Maximizes software quality
- Ensures reproducibility
- Maintains clinical safety
- Provides auditability for all changes

---

## System Architecture

### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Hermes** | AI Project Manager & Orchestrator | `.hermes/agents/hermes.md` |
| **OpenCode** | Primary Implementation Agent | `.hermes/agents/implementation-agent.md` |
| **Claude Code** | Architecture Agent | `.hermes/agents/architecture-agent.md` |
| **Testing Agent** | Quality Validation | `.hermes/agents/testing-agent.md` |
| **Documentation Agent** | Knowledge Management | `.hermes/agents/docs-agent.md` |
| **Release Agent** | Release Coordination | `.hermes/agents/release-agent.md` |
| **Repository Intelligence** | Codebase Analysis | `.hermes/agents/repo-intelligence-agent.md` |

### Infrastructure

| Component | Purpose | Location |
|-----------|---------|----------|
| **Agent Definitions** | Agent specifications | `.hermes/agents/` |
| **Workflow Library** | Reusable engineering workflows | `.hermes/workflows/` |
| **Prompt Library** | Production-ready prompts | `.hermes/prompts/` |
| **Project Memory** | Knowledge base | `.hermes/memory/` |
| **Quality Gates** | Validation requirements | `.hermes/workflows/QUALITY_GATES.md` |
| **Automation Scripts** | Operational scripts | `.hermes/scripts/` |
| **Intelligence Reports** | Repository analysis | `.hermes/reports/` |
| **Documentation** | Engineering documentation | `.hermes/documentation/` |

---

## Delegation Workflow

```
Hermes (Planning)
    ↓
Implementation Agent (OpenCode)
    ↓
Testing Agent (Validation)
    ↓
Architecture Agent (Claude Code)
    ↓
Documentation Agent (Updates)
    ↓
Release Agent (Delivery)
    ↓
Hermes (Summary)
```

---

## Quality Gates

All workflows must pass:

1. **Ruff** — Linting (PEP 8 compliance)
2. **mypy** — Type checking
3. **pytest** — Testing
4. **Migration consistency** — Database schema validation
5. **Documentation completeness** — Required docs present
6. **Architecture consistency** — Design compliance
7. **Coding standards** — Project conventions

**Rule:** If validation fails → Stop, report, recommend corrective actions.

---

## Engineering Principles

The AI Factory prioritizes:

- **Automation** — Reduce manual intervention
- **Maintainability** — Clean, modular code
- **Reproducibility** — Consistent results
- **Modularity** — Component-based architecture
- **Clean Architecture** — Separation of concerns
- **Domain Driven Design** — Business logic clarity
- **Clinical Governance** — Medical safety compliance
- **Testability** — Comprehensive testing
- **Documentation** — Knowledge preservation
- **Auditability** — Change tracking

---

## Git Workflow

- Always use feature branches
- Never work directly on `main`
- Create meaningful commits
- Generate draft pull requests
- Never merge automatically without approval

---

## Safety Rules

The AI Factory enforces:

- Never modify production code without analysis
- Never delete code without verification
- Never bypass tests
- Never ignore failed quality gates
- Never introduce breaking changes without warning
- Never modify clinical knowledge without explicit instruction

---

## Long-Term Vision

Continuously evolve the AI Factory into a self-improving engineering platform that:

- Reduces repetitive manual work
- Improves automation capabilities
- Learns from previous implementations
- Maintains high-quality engineering standards
- Supports long-term clinical software development

---

## Documentation

The AI Factory maintains comprehensive documentation:

- AI_FACTORY.md — System overview
- HERMES_SYSTEM.md — Operating instructions
- ARCHITECTURE.md — Technical architecture
- DEVELOPMENT_GUIDE.md — Development setup
- WORKFLOW_GUIDE.md — Engineering workflows
- QUALITY_GATES.md — Validation requirements
- RELEASE_PROCESS.md — Release procedures
- AGENT_ROLES.md — Agent definitions
- ONBOARDING.md — New developer guide
- PROJECT_MEMORY.md — Project knowledge base
