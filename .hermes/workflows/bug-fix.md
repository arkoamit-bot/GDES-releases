# Workflow: Bug Fix

## Objective
Identify root cause and resolve a bug in the GDES system.

## Required Agents
- Hermes (coordination)
- OpenCode (implementation)
- Testing Agent (validation)

## Execution Order
1. **Bug Triage**
   - Read and understand the bug report
   - Assess severity and clinical safety impact
   - Identify affected modules

2. **Reproduction**
   - Create minimal reproduction case
   - Identify reproduction steps
   - Document observed vs expected behavior

3. **Root Cause Analysis**
   - Use systematic debugging approach
   - Trace the execution path
   - Identify the exact cause
   - Check for related issues

4. **Fix Implementation (OpenCode)**
   - Implement minimal fix
   - Ensure fix addresses root cause, not symptoms
   - Avoid introducing new issues

5. **Regression Testing**
   - Write regression test
   - Run full test suite
   - Verify fix in relevant scenarios

6. **Review & Commit**
   - Code review (self or peer)
   - Commit with descriptive message
   - Update bug tracker

## Quality Gates
- [ ] Bug reproduced and documented
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Regression test written
- [ ] All tests pass
- [ ] No new issues introduced

## Expected Deliverables
- Bug fix commit
- Regression test
- Root cause documentation

## Failure Recovery
- If fix is complex → request Claude Code review
- If clinical safety affected → immediate escalation
- If fix breaks other tests → iterate
