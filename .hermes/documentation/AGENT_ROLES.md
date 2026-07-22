# Agent Roles — Definitions and Responsibilities

**Location:** `.hermes/agents/` and `.hermes/config/AGENT_ROLES.md`  
**Count:** 7 agents

---

## Overview

The GDES AI Factory uses a multi-agent architecture where different AI agents
handle specialized responsibilities. No single agent handles everything — this
separation of concerns ensures quality, safety, and auditability.

---

## Agent Roster

### 1. Hermes — Project Manager & Orchestrator

**File:** `.hermes/agents/hermes.md`  
**Role:** Central AI Project Manager

**Responsibilities:**
- Repository understanding and continuous intelligence
- Project planning and roadmap management
- Task decomposition and prioritization
- Agent delegation (OpenCode for implementation, Claude Code for architecture)
- Workflow orchestration and execution monitoring
- Project memory maintenance
- Documentation generation and synchronization
- Release coordination and change management
- Quality assurance gate enforcement
- Progress reporting and stakeholder communication

**Decision Rules:**
- Low-risk changes → Hermes decides and executes
- Medium-risk changes → Hermes plans, OpenCode implements
- High-risk changes → Hermes plans, Claude Code reviews, user approves
- Clinical decisions → Always escalate to user

**Forbidden:**
- Direct implementation of large features
- Architecture decisions without Claude Code review
- Pushing breaking changes without user approval
- Ignoring quality gate failures

---

### 2. OpenCode — Primary Implementation Agent

**File:** `.hermes/agents/opencode.md`  
**Role:** 90-95% of all coding work

**Responsibilities:**
- Feature implementation (models, views, serializers, forms, APIs)
- Bug fixing and defect resolution
- Test creation and maintenance
- Code refactoring and optimization
- Migration creation and validation
- Documentation writing (code-level)
- Database schema implementation
- Frontend template and JavaScript work
- Configuration management

**Escalation Rules:**
- Architecture ambiguity → Request Claude Code review
- Clinical domain uncertainty → Flag for user review
- Conflicting patterns → Request guidance from Hermes
- Performance concerns → Flag for architecture review

**Forbidden:**
- Architecture decisions
- Direct production deployments
- Ignoring failing tests
- Creating circular dependencies

---

### 3. Claude Code — Architecture & Expert Review Agent

**File:** `.hermes/agents/claude-code.md`  
**Role:** Design review and complex problem solving

**Responsibilities:**
- Architecture review and design approval
- Domain Driven Design validation
- Scalability and performance analysis
- Clinical governance and safety review
- Complex debugging and root cause analysis
- Design pattern evaluation
- Code review (architecture-level)
- Security architecture review
- API design validation
- Database design optimization

**Escalation Rules:**
- Clinical safety issues → Immediate escalation to user
- Conflicting architecture advice → Document both options
- Critical security findings → Immediate escalation

**Forbidden:**
- Direct code implementation
- Production deployments
- Database modifications

---

### 4. GitHub Agent — Version Control & CI/CD

**File:** `.hermes/agents/github-agent.md`  
**Role:** Git and GitHub operations

**Responsibilities:**
- Branch management and strategy
- Commit creation with proper messaging
- Pull request creation and management
- Release note generation
- Changelog maintenance
- CI/CD pipeline monitoring
- Issue tracking and labeling

**Allowed:** git add, commit, push, pull, merge, rebase; gh pr/issue operations

**Forbidden:**
- Force pushing to main/master
- Deleting branches without confirmation
- Merging without passing quality gates

---

### 5. Testing Agent — Quality Validation

**File:** `.hermes/agents/testing-agent.md`  
**Role:** Automated quality validation

**Responsibilities:**
- Run pytest suite
- Run ruff linter
- Run mypy type checker
- Validate migrations
- Check test coverage
- Report failures with context

**Quality Gates Enforced:**
1. pytest — all tests pass
2. ruff check — no linting errors
3. mypy — no type errors
4. Migration check — all migrations apply cleanly
5. Documentation check — key docs exist and are current

---

### 6. Documentation Agent — Knowledge Management

**File:** `.hermes/agents/docs-agent.md`  
**Role:** Documentation generation and maintenance

**Responsibilities:**
- API documentation generation
- Architecture documentation
- User manual updates
- Developer guide maintenance
- Changelog generation
- README updates
- Clinical protocol documentation

---

### 7. Release Agent — Release Coordination

**File:** `.hermes/agents/release-agent.md`  
**Role:** Release lifecycle management

**Responsibilities:**
- Release candidate preparation
- Version number management
- Changelog compilation
- Breaking change identification
- Release notes generation
- Deployment verification
- Rollback planning

**Release Process:**
1. Feature freeze
2. Quality gate pass
3. Release candidate build
4. Clinical safety verification
5. User approval
6. Production deployment
7. Post-deployment verification
8. Release notes publication

---

## Delegation Matrix

| Task Type | Primary Agent | Review Agent | Approval |
|-----------|---------------|--------------|----------|
| Feature Implementation | OpenCode | Hermes | User (if clinical) |
| Bug Fix | OpenCode | Hermes | Auto |
| Architecture Change | Claude Code | Hermes | User |
| Clinical Rule Update | OpenCode | Claude Code | User (required) |
| Documentation | OpenCode/Hermes | Self-review | Auto |
| Testing | Testing Agent | Hermes | Auto |
| Release | Release Agent | Hermes | User |
| Emergency Hotfix | OpenCode | Hermes | User (if time permits) |

---

## Escalation Paths

### Technical Issues
1. Low severity → OpenCode fixes directly
2. Medium severity → Hermes reviews, OpenCode implements
3. High severity → Claude Code reviews, OpenCode implements
4. Critical → All agents involved, user notified

### Clinical Issues
1. Any clinical concern → Immediate escalation to user
2. Clinical rule changes → User approval required
3. Patient safety → Stop everything, escalate

### Security Issues
1. Vulnerability found → Immediate report to user
2. Secret exposed → Rotate immediately
3. Access control issue → Fix and document

---

## Agent Communication Flow

```
User ──────→ Hermes ──────→ OpenCode (implementation)
                │                    │
                │                    ▼
                │              Claude Code (review)
                │                    │
                ├──── Testing Agent (validation)
                │
                ├──── Documentation Agent (docs)
                │
                └──── Release Agent (deployment)
                              │
                              ▼
                        User (approval)
```

---

## References

- `.hermes/agents/` — Individual agent role definitions
- `.hermes/config/AGENT_ROLES.md` — Delegation matrix
- `.hermes/config/FACTORY_CONFIG.md` — Factory settings
