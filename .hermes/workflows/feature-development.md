# Workflow: Feature Development

## Objective
Implement a new feature for the GDES system following best practices.

## Required Agents
- Hermes (planning, coordination)
- OpenCode (implementation)
- Claude Code (architecture review, if needed)
- Testing Agent (validation)

## Execution Order
1. **Requirements Analysis**
   - Understand the feature request
   - Identify affected modules
   - Check existing patterns in codebase
   - Estimate complexity

2. **Architecture Planning**
   - Design the solution
   - Identify model changes
   - Plan API endpoints
   - Plan UI changes
   - If complex → request Claude Code review

3. **Implementation (OpenCode)**
   - Create/update Django models
   - Create migrations
   - Implement views/serializers
   - Add URL routing
   - Add admin configuration
   - Create templates/JS as needed

4. **Testing**
   - Write unit tests
   - Write integration tests
   - Run full test suite
   - Verify edge cases

5. **Documentation**
   - Update API documentation
   - Update code comments
   - Update relevant .md files

6. **Review & Quality Gates**
   - Run pytest
   - Run ruff check
   - Run mypy
   - Self-review diff

7. **Commit & Report**
   - Create descriptive commit
   - Update project memory
   - Generate completion report

## Quality Gates
- [ ] All tests pass (existing + new)
- [ ] ruff check clean
- [ ] mypy clean
- [ ] Migrations created and testable
- [ ] Documentation updated
- [ ] Clinical safety reviewed

## Expected Deliverables
- Working feature code
- Test suite
- Documentation updates
- Completion report

## Failure Recovery
- If architecture concerns arise → escalate to Claude Code
- If clinical safety issue → stop and escalate to user
- If tests fail → fix before proceeding
- If migration conflicts → resolve and re-test
