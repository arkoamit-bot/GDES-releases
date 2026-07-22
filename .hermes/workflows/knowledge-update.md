# Workflow: Knowledge Update

## Objective
Update the GDES medical knowledge base with new clinical information.

## Required Agents
- Hermes (coordination)
- User (clinical validation)

## Execution Order
1. **Clinical Review**
   - Receive new clinical information
   - Validate source credibility
   - Check against current guidelines

2. **Knowledge Integration**
   - Identify affected knowledge files
   - Update clinical rules and protocols
   - Update drug databases if needed
   - Update diagnostic criteria if needed

3. **Clinical Safety Check**
   - Verify no contradictory information
   - Check interaction with existing rules
   - Validate clinical logic

4. **User Approval**
   - Present changes for clinical review
   - Await approval before implementation

5. **Implementation**
   - Apply knowledge base updates
   - Run validation tests
   - Update documentation

## Quality Gates
- [ ] Clinical accuracy verified
- [ ] No contradictions with existing knowledge
- [ ] User approval obtained
- [ ] Validation tests pass
- [ ] Documentation updated

## Expected Deliverables
- Updated knowledge base
- Change documentation
- Clinical validation report

## Failure Recovery
- If contradiction found → flag for user resolution
- If clinical uncertainty → escalate to user
- If integration fails → rollback and investigate
