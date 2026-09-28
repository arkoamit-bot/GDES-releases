# Workflow: Technical Debt Review

## Purpose
Identify, assess, and prioritize technical debt in the codebase for systematic reduction.

## Input
- Code complexity metrics
- Code smell detection results
- Duplicate code analysis
- Dead code identification
- Documentation gaps

## Output
- Technical debt inventory
- Debt prioritization matrix
- Refactoring roadmap
- Cost-benefit analysis
- Progress tracking

## Execution Steps

### 1. Debt Identification
- Analyze code complexity metrics
- Identify code smells and anti-patterns
- Detect duplicate code patterns
- Find dead code and unused imports
- Document documentation gaps

### 2. Debt Assessment
- Measure complexity scores
- Calculate maintenance burden
- Estimate refactoring effort
- Assess business impact
- Evaluate risk factors

### 3. Prioritization
- Categorize debt by severity (Critical, High, Medium, Low)
- Consider business value of fixes
- Evaluate technical risk
- Plan remediation timeline
- Allocate resources

### 4. Refactoring Planning
- Create refactoring tasks
- Define acceptance criteria
- Estimate effort and timeline
- Identify dependencies
- Plan testing strategy

### 5. Execution Support
- Provide refactoring guidance
- Support implementation agents
- Validate refactoring results
- Update documentation
- Track progress

### 6. Monitoring
- Track debt reduction progress
- Measure improvement metrics
- Validate refactoring effectiveness
- Update debt inventory
- Report progress

## Agent Responsibilities

### Hermes (Orchestrator)
- Coordinate debt review activities
- Prioritize refactoring tasks
- Allocate resources
- Track progress
- Report to Project Owner

### Repository Intelligence Agent
- Identify technical debt
- Measure complexity metrics
- Detect code smells
- Generate debt reports

### Implementation Agent (OpenCode)
- Perform refactoring tasks
- Implement improvements
- Write tests for refactored code
- Update documentation

### Architecture Agent (Claude Code)
- Review refactoring plans
- Validate architectural improvements
- Provide design guidance
- Ensure quality standards

## Quality Gates
- ✅ Debt inventory is comprehensive
- ✅ Prioritization is data-driven
- ✅ Refactoring plans are actionable
- ✅ Progress is measurable
- ✅ Quality improvements are validated

## Failure Handling
- Document refactoring failures
- Analyze root causes
- Adjust approach as needed
- Reschedule tasks
- Update risk assessment

## Technical Debt Categories

### Code Complexity
- High cyclomatic complexity
- Deep nesting levels
- Long methods/functions
- Large classes/files

### Code Smells
- Duplicate code
- Dead code
- Unused imports
- Inconsistent naming
- Magic numbers/strings

### Architecture Issues
- Tight coupling
- Circular dependencies
- Violation of DDD principles
- Poor separation of concerns

### Documentation Debt
- Missing documentation
- Outdated documentation
- Inconsistent documentation
- Missing code comments

### Testing Debt
- Low test coverage
- Missing integration tests
- Flaky tests
- Slow tests

## Frequency
- **Monthly:** Full technical debt review
- **Quarterly:** Debt reduction planning
- **After major releases:** Debt assessment
- **Continuous:** Debt monitoring
