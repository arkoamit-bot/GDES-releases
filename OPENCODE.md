# OPENCODE.md

Version: 1.0

Purpose:
Implement and operate according to the Hermes Engineering Manual.

---

# PRIMARY DIRECTIVE

This repository is governed by the global engineering manual:

HERMES_OPENCODE_ENGINEERING_MANUAL.md

Treat that document as the highest-level engineering policy.

Your responsibility is to implement software according to that manual.

Never ignore its requirements.

---

# FIRST ACTION

Before making any code changes:

1. Read the repository.

2. Read all project documentation.

3. Build a complete understanding.

4. Produce an implementation plan.

Only then begin coding.

---

# PROJECT DISCOVERY

Automatically discover and read, if present:

README.md

PROJECT_CONTEXT.md

CLAUDE.md

OPENCODE.md

ARCHITECTURE.md

TECH_STACK.md

SYSTEM.md

CONTRIBUTING.md

CHANGELOG.md

docs/

requirements.txt

pyproject.toml

package.json

Dockerfile

docker-compose.yml

GitHub workflows

Database migrations

If multiple documents conflict:

User instruction

↓

Project documentation

↓

Repository documentation

↓

Hermes Engineering Manual

↓

OpenCode implementation decisions

---

# IMPLEMENTATION WORKFLOW

Every task must follow this workflow.

Understand

↓

Analyze

↓

Plan

↓

Identify affected modules

↓

Determine implementation strategy

↓

Implement

↓

Run tests

↓

Perform regression testing

↓

Review code

↓

Optimize

↓

Update documentation

↓

Prepare release notes

Never skip testing.

Never skip documentation.

---

# ENGINEERING RULES

Always follow:

SOLID

DRY

KISS

Clean Architecture

Repository pattern where appropriate

Service layer

Thin controllers/views

Reusable components

Backward compatibility

Safe database migrations

Meaningful names

Type hints

PEP8 (Python)

Project coding standards

---

# QUALITY GATES

Do not consider work complete until all of the following are satisfied.

✓ Project builds successfully

✓ Tests pass

✓ No regressions

✓ No duplicate logic

✓ No dead code

✓ Safe migrations

✓ Security reviewed

✓ Performance reviewed

✓ Documentation updated

✓ Changelog updated

If any quality gate fails,

continue working until resolved.

---

# AI PROVIDER POLICY

Use only FREE AI providers.

Preferred order:

1. Google AI Studio (Gemini Free)

2. OpenRouter Free

3. Groq Free

4. GitHub Models

5. Cloudflare AI

6. HuggingFace Free

Never use a paid API automatically.

If a provider becomes unavailable,

automatically use the next FREE provider.

Never incur cost without explicit user approval.

---

# COST PROTECTION

Before using any provider verify:

• Free tier available

• No billing required

• Model available

• Within quota

If verification fails,

switch providers automatically.

---

# AUTOMATIC FAILOVER

On

429

Timeout

Quota exceeded

Billing required

Unavailable

Authentication error

Retry using the next provider.

Never stop after the first failure.

---

# REPOSITORY UNDERSTANDING

Before implementation identify:

Programming language

Framework

Architecture

Database

Testing framework

Deployment strategy

Packaging

Installer

CI/CD

Security model

Dependency graph

Risk areas

Document your findings before implementation.

---

# TESTING

Always execute:

Unit tests

Integration tests

Regression tests

Migration tests

Packaging verification

Installer verification

Desktop startup verification (if applicable)

Do not release untested code.

---

# DOCUMENTATION

Every significant engineering change must update:

README

Architecture

API documentation

Deployment guide

Developer guide

User documentation

Release notes

Changelog

Documentation is mandatory.

---

# RELEASE PROCESS

Before every release:

Run complete test suite.

Verify migrations.

Verify packaging.

Verify installer.

Verify documentation.

Generate release notes.

Confirm version number.

Prepare Git commit.

Prepare Git tag.

Prepare GitHub Release.

---

# FAILURE HANDLING

If uncertain:

Do not guess.

Investigate.

Read project code.

Read documentation.

Search existing implementation.

Preserve existing behaviour.

If behaviour cannot be determined,

report uncertainty clearly.

---

# PROJECT IMPROVEMENT

Whenever possible improve:

Architecture

Performance

Security

Maintainability

Documentation

Testing

Developer experience

Deployment

without introducing regressions.

---

# SUCCESS CRITERIA

Every completed task should result in:

✓ Better code quality

✓ Better maintainability

✓ Better architecture

✓ Better documentation

✓ Better testing

✓ Better deployment

✓ Zero regressions

✓ Production-ready implementation

Do not optimize for speed.

Optimize for correctness, maintainability, and long-term reliability.

End of File