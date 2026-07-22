# Workflow: Emergency Hotfix

## Objective
Rapidly fix critical issues in production.

## Required Agents
- Hermes (coordination)
- OpenCode (implementation)
- User (approval)

## Execution Order
1. **Triage**
   - Assess severity
   - Determine clinical safety impact
   - Identify affected users

2. **Immediate Fix**
   - Implement minimal fix
   - Create regression test
   - Fast-track quality checks

3. **Emergency Review**
   - Code review (accelerated)
   - Clinical safety verification (if applicable)
   - User approval (if time permits)

4. **Emergency Deployment**
   - Deploy fix
   - Verify fix in production
   - Monitor for issues

5. **Post-Incident**
   - Root cause analysis
   - Prevention measures
   - Documentation update

## Quality Gates
- [ ] Fix implemented
- [ ] Regression test created
- [ ] Minimum quality check passed
- [ ] Deployment verified

## Expected Deliverables
- Hotfix commit
- Deployment verification
- Post-incident report
