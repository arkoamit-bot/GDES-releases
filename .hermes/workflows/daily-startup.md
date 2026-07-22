# Workflow: Daily Startup

## Objective
Initialize a productive development session for the GDES project.

## Required Agents
- Hermes (orchestrator)
- Testing Agent (validation)

## Execution Order
1. **Repository Status Check**
   - Run `git status` and `git log --oneline -10`
   - Check for uncommitted changes
   - Review recent branch activity

2. **Quality Gate Validation**
   - Run `pytest` — verify all tests pass
   - Run `ruff check .` — verify no linting errors
   - Run `mypy .` — verify no type errors
   - Report any failures

3. **Dependency Check**
   - Verify requirements.txt is current
   - Check for security advisories
   - Verify virtual environment is active

4. **Project Memory Refresh**
   - Read `.hermes/memory/PROJECT_MEMORY.md`
   - Check for any stale entries
   - Update with current state

5. **Work Prioritization**
   - Review open issues
   - Check roadmap for current phase
   - Suggest today's priorities

## Quality Gates
- [ ] Git status clean or WIP properly documented
- [ ] All tests passing
- [ ] No linting errors
- [ ] No type errors
- [ ] Project memory current

## Expected Deliverables
- Daily startup report
- Priority list for the session
- Any blocking issues identified

## Failure Recovery
- If tests fail → diagnose and fix before proceeding
- If dependencies outdated → update and re-validate
- If project memory stale → refresh from codebase
