# Architecture & Design Decisions

## Decision Log

### D1: AI Factory Architecture
- **Date:** 2026-07-21
- **Decision:** Implement Hermes as orchestrator with OpenCode (implementation) and Claude Code (review)
- **Rationale:** Clear separation of concerns, maximum automation
- **Status:** Implemented

### D2: Documentation Location
- **Date:** 2026-07-21
- **Decision:** AI Factory documentation in .hermes/ directory, separate from repo root docs
- **Rationale:** Keep AI Factory infrastructure clean, avoid conflicts with existing docs
- **Status:** Implemented

### D3: Quality Gates
- **Date:** 2026-07-21
- **Decision:** 8 mandatory quality gates (pytest, ruff, mypy, migrations, docs, architecture, security, clinical)
- **Rationale:** Comprehensive quality assurance with clinical safety as highest priority
- **Status:** Implemented

### D4: Workflow Standardization
- **Date:** 2026-07-21
- **Decision:** Standardized workflows for all common development tasks
- **Rationale:** Consistency, reproducibility, auditability
- **Status:** Implemented
