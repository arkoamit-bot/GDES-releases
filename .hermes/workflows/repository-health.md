# Workflow: Repository Health Check

## Objective
Comprehensive health assessment of the GDES repository.

## Required Agents
- Hermes (orchestration)
- Testing Agent (validation)

## Execution Order
1. **Code Quality**
   - Run linting (ruff)
   - Run type checking (mypy)
   - Analyze code complexity
   - Check for dead code

2. **Test Health**
   - Run full test suite
   - Check coverage metrics
   - Identify untested code
   - Review test quality

3. **Dependency Health**
   - Check for outdated packages
   - Check for security vulnerabilities
   - Review dependency graph

4. **Documentation Health**
   - Check documentation currency
   - Verify README accuracy
   - Review API documentation

5. **Git Health**
   - Check branch strategy
   - Review commit history
   - Identify stale branches

6. **Report Generation**
   - Generate health score
   - List findings by priority
   - Recommend improvements

## Quality Gates
- [ ] Health score generated
- [ ] All critical issues identified
- [ ] Recommendations prioritized

## Expected Deliverables
- Repository health report
- Technical debt inventory
- Improvement recommendations
