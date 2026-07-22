# Agent Roles Configuration

## Delegation Matrix

| Task Type | Primary Agent | Review Agent | Approval |
|-----------|---------------|--------------|----------|
| Feature Implementation | OpenCode | Hermes | User (if clinical) |
| Bug Fix | OpenCode | Hermes | Auto |
| Architecture Change | Claude Code | Hermes | User |
| Clinical Rule Update | OpenCode | Claude Code | User (required) |
| Documentation | OpenCode/Hermes | Self-review | Auto |
| Testing | Testing Agent | Hermes | Auto |
| Release | Release Agent | Hermes | User |
| Emergency Hotfix | OpenCode | Hermes | User (if time permits) |

## Escalation Paths

### Technical Issues
1. Low severity → OpenCode fixes directly
2. Medium severity → Hermes reviews, OpenCode implements
3. High severity → Claude Code reviews, OpenCode implements
4. Critical → All agents involved, user notified

### Clinical Issues
1. Any clinical concern → Immediate escalation to user
2. Clinical rule changes → User approval required
3. Patient safety → Stop everything, escalate

### Security Issues
1. Vulnerability found → Immediate report to user
2. Secret exposed → Rotate immediately
3. Access control issue → Fix and document
