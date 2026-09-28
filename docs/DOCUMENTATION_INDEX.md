# GDES Documentation Index

## Overview
This document provides a comprehensive index of all documentation in the GDES repository.

## Documentation Structure

### Root Documentation (`/`)
- `README.md` — Project overview and getting started
- `PROJECT_CONSTITUTION.md` — Project governance and standards
- `PROJECT_CONTEXT.md` — Project context and background
- `TRACK.md` — Project tracking and milestones
- `CHANGELOG_2026-07-16.md` — Recent changes
- `AI_FACTORY_STATUS.md` — AI Factory status

### Documentation Directory (`/docs/`)
- `architecture/` — System architecture documentation
- `clinical/` — Clinical documentation
- `development/` — Development guides
- `deployment/` — Deployment documentation
- `releases/` — Release notes and changelogs
- `reports/` — Technical reports
- `workflows/` — Workflow documentation

### Clinical Documentation (`/docs/clinical/`)
- `diseases/` — Disease-specific documentation (195 files)
  - Organized by disease name (alport, ANCA, etc.)
  - Contains clinical cases, pathways, guidelines, knowledge
- General clinical governance and validation documentation

### AI Factory Documentation (`/.hermes/documentation/`)
- `AI_FACTORY.md` — AI Factory system overview
- `ARCHITECTURE.md` — Technical architecture
- `DEVELOPMENT_GUIDE.md` — Development setup
- `WORKFLOW_GUIDE.md` — Engineering workflows
- `QUALITY_GATES.md` — Validation requirements
- `RELEASE_PROCESS.md` — Release procedures
- `AGENT_ROLES.md` — Agent definitions
- `ONBOARDING.md` — New developer guide
- `PROJECT_MEMORY.md` — Project knowledge base

## Documentation Guidelines

### Adding New Documentation
1. Place in appropriate directory based on content type
2. Use descriptive filenames with underscores
3. Include metadata header with title, date, author
4. Update this index when adding significant documentation

### Documentation Maintenance
- Review documentation quarterly
- Archive outdated documentation
- Keep documentation synchronized with code changes
- Ensure documentation is accessible and searchable

## Documentation Standards

### File Naming
- Use lowercase with underscores: `clinical_workflow.md`
- Use descriptive names: `diabetic_kidney_disease_guidelines.md`
- Avoid special characters and spaces

### Content Structure
- Title and metadata
- Overview/purpose
- Detailed content
- References/links
- Version history

### Version Control
- Commit documentation with related code changes
- Use meaningful commit messages
- Review documentation in pull requests
