# Workflow: Repository Audit

## Purpose
Perform comprehensive repository audit to assess code quality, security, and compliance.

## Input
- Repository structure
- Code quality metrics
- Security scan results
- Documentation status
- Test coverage data

## Output
- Repository audit report
- Security assessment
- Compliance verification
- Improvement recommendations
- Priority action items

## Execution Steps

### 1. Preparation
- Verify repository access
- Check current branch status
- Ensure all tools are available
- Review previous audit results

### 2. Code Quality Audit
- Run Ruff linting: `ruff check .`
- Run mypy type checking: `mypy .`
- Analyze code complexity
- Identify code smells and anti-patterns

### 3. Security Audit
- Scan for hardcoded credentials
- Check for SQL injection vulnerabilities
- Verify access control patterns
- Validate data handling practices

### 4. Documentation Audit
- Check documentation completeness
- Verify accuracy of existing docs
- Identify documentation gaps
- Validate clinical terminology usage

### 5. Test Coverage Audit
- Run test suite: `pytest`
- Measure test coverage
- Identify untested critical paths
- Recommend coverage improvements

### 6. Dependency Audit
- Check for outdated dependencies
- Identify security vulnerabilities
- Verify license compliance
- Validate version constraints

### 7. Migration Audit
- Check for pending migrations
- Validate migration consistency
- Test migration reversibility
- Document schema changes

### 8. Report Generation
- Compile audit findings
- Prioritize recommendations
- Generate action items
- Update project memory

## Agent Responsibilities

### Hermes (Orchestrator)
- Coordinate audit activities
- Assign tasks to appropriate agents
- Validate audit results
- Generate final report

### Repository Intelligence Agent
- Perform code quality analysis
- Generate technical metrics
- Identify improvement opportunities

### Testing Agent
- Execute test suite
- Measure test coverage
- Validate test quality

### Documentation Agent
- Audit documentation completeness
- Verify documentation accuracy
- Recommend documentation updates

## Quality Gates
- ✅ All quality gates pass (Ruff, mypy, pytest)
- ✅ No critical security vulnerabilities
- ✅ Documentation completeness > 90%
- ✅ Test coverage > 80%
- ✅ No pending migrations

## Failure Handling
- Document all failures
- Prioritize critical issues
- Generate corrective action plan
- Schedule follow-up audit

## Frequency
- **Monthly:** Full repository audit
- **Weekly:** Quick health check
- **Before release:** Comprehensive audit
- **After major changes:** Targeted audit
