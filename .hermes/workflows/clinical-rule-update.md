# Workflow: Clinical Rule Update

## Objective
Update clinical decision support rules in the GDES system.

## Required Agents
- Hermes (coordination)
- User (clinical validation)

## Execution Order
1. **Rule Specification**
   - Define the clinical rule change
   - Specify trigger conditions
   - Specify recommendation/action
   - Specify evidence basis

2. **Impact Analysis**
   - Identify affected patients/cases
   - Check for rule conflicts
   - Assess clinical safety impact

3. **Implementation**
   - Update clinical reasoning module
   - Update knowledge base
   - Create/update tests

4. **Clinical Validation**
   - Test with sample cases
   - User clinical review
   - Verify against guidelines

5. **Deployment**
   - Apply changes
   - Monitor for issues
   - Document changes

## Quality Gates
- [ ] Rule specification approved
- [ ] No conflicts with existing rules
- [ ] Tests pass
- [ ] Clinical validation complete
- [ ] User approval obtained

## Expected Deliverables
- Updated clinical rules
- Validation test results
- Change documentation

## Failure Recovery
- If rule conflicts → resolve before proceeding
- If clinical concern → escalate to user
- If test failures → fix before deployment
