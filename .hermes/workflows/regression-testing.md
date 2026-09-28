# Workflow: Regression Testing

## Objective
Verify that recent changes have not broken existing functionality.

## Required Agents
- Testing Agent (execution)
- Hermes (coordination)

## Execution Order
1. **Test Suite Execution**
   - Run full pytest suite
   - Run ruff check
   - Run mypy
   - Check migration status

2. **Result Analysis**
   - Categorize failures by module
   - Identify new vs pre-existing failures
   - Assess impact on clinical functionality

3. **Report Generation**
   - Generate test summary report
   - Highlight critical failures
   - List warnings and deprecations

4. **Remediation**
   - Fix critical failures
   - Document known issues
   - Update test suite as needed

## Quality Gates
- [ ] All critical tests pass
- [ ] No new regressions
- [ ] Linting clean
- [ ] Type checking clean

## Expected Deliverables
- Test execution report
- Regression analysis
- Remediation actions
