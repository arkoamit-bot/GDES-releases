# Logging Configuration

## Overview
AI Factory v1.0 uses structured logging for all workflow executions, agent activities, and repository validations.

## Log Locations

| Log Type | Location | Retention |
|----------|----------|-----------|
| Workflow execution | `.hermes/logs/workflows/` | 30 days |
| Agent activity | `.hermes/logs/agents/` | 30 days |
| Repository scans | `.hermes/logs/scans/` | 90 days |
| Errors | `.hermes/logs/errors/` | 90 days |
| Performance | `.hermes/logs/performance/` | 30 days |

## Log Format

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [COMPONENT] [MESSAGE]
```

### Levels
- **INFO**: Normal operations (workflow started, task completed)
- **WARN**: Non-critical issues (slow operations, deprecated patterns)
- **ERROR**: Failures requiring attention (test failures, build errors)
- **CRITICAL**: Blocking issues (security vulnerabilities, data corruption)

## Workflow Logging

Every workflow execution logs:
1. Start time and trigger source
2. Each execution step with duration
3. Agent delegations and responses
4. Quality gate results (pass/fail)
5. End time and total duration
6. Success/failure status

### Example
```
[2026-07-21 09:00:01] [INFO] [workflow] Daily startup initiated
[2026-07-21 09:00:02] [INFO] [workflow] Running repository scan...
[2026-07-21 09:00:15] [INFO] [workflow] Scan complete: 30 apps, 86 models
[2026-07-21 09:00:16] [INFO] [workflow] Running quality gates...
[2026-07-21 09:00:45] [WARN] [quality] ruff: 12 warnings found
[2026-07-21 09:01:00] [INFO] [quality] All gates passed (with warnings)
[2026-07-21 09:01:01] [INFO] [workflow] Daily startup completed in 60s
```

## Agent Activity Logging

Each agent delegation logs:
1. Agent name and role
2. Task description
3. Input context summary
4. Execution duration
5. Output summary
6. Success/failure status

## Performance Logging

Track execution times for:
- Repository scans (target: <30s)
- Quality gate validation (target: <60s)
- Test suite execution (target: <120s)
- Documentation generation (target: <60s)
- Release preparation (target: <300s)

## Error Logging

Errors include:
- Full traceback (for Python scripts)
- Stack context (for workflow failures)
- Suggested corrective actions
- Related documentation references

## Log Rotation

Logs are automatically rotated:
- Daily rotation for workflow and agent logs
- Weekly rotation for scan and performance logs
- Monthly cleanup of logs older than retention period

## Dashboard Integration

Log data feeds into the engineering dashboard:
- Recent activity (last 10 workflow executions)
- Error rate (errors per day)
- Average execution times
- Agent utilization metrics
