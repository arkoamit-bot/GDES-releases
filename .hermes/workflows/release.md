# Workflow: Release

## Objective
Prepare and execute a GDES release.

## Required Agents
- Release Agent (preparation)
- Testing Agent (validation)
- User (approval)

## Execution Order
1. **Release Planning**
   - Determine version number
   - Review all changes since last release
   - Identify breaking changes

2. **Quality Validation**
   - Full test suite execution
   - Performance validation
   - Security scan
   - Documentation review

3. **Release Artifacts**
   - Update version numbers
   - Generate changelog
   - Create release notes
   - Tag release in git

4. **Deployment Preparation**
   - Verify migrations
   - Check deployment configuration
   - Prepare rollback plan

5. **User Approval**
   - Present release for approval
   - Address any concerns

6. **Deployment**
   - Execute deployment
   - Verify deployment success
   - Monitor for issues

7. **Post-Deployment**
   - Verify production functionality
   - Update documentation
   - Notify stakeholders

## Quality Gates
- [ ] All tests pass
- [ ] No critical/high bugs open
- [ ] Documentation complete
- [ ] User approval obtained
- [ ] Rollback plan ready
- [ ] Deployment verified

## Expected Deliverables
- Release artifacts (tag, changelog, notes)
- Deployment verification
- Post-deployment report

## Failure Recovery
- If deployment fails → execute rollback
- If critical bug found → hotfix process
- If user rejects → address concerns and reschedule
