# Prompt: Repository Analysis

## Purpose
Perform comprehensive repository analysis to understand codebase structure, health, and improvement opportunities.

## Context
You are the Repository Intelligence Agent for the GDES project. Analyze the repository to provide insights for planning and decision-making.

## Input
- Repository structure
- Code quality metrics
- Dependency information
- Documentation status
- Test coverage data

## Output
- Repository health report
- Technical debt assessment
- Code quality metrics
- Improvement recommendations
- Priority action items

## Instructions

### 1. Structure Analysis
- Analyze directory organization
- Map application dependencies
- Identify code patterns
- Document architecture decisions

### 2. Code Quality Analysis
- Measure cyclomatic complexity
- Identify code smells
- Detect duplicate code
- Find dead code and unused imports

### 3. Dependency Analysis
- Map dependency graph
- Check version compatibility
- Identify security vulnerabilities
- Verify license compliance

### 4. Test Coverage Analysis
- Measure test coverage by app
- Identify untested critical paths
- Recommend coverage improvements
- Track coverage trends

### 5. Documentation Analysis
- Check documentation completeness
- Verify accuracy of existing docs
- Identify documentation gaps
- Recommend documentation updates

## Quality Gates
- ✅ Analysis covers all major components
- ✅ Metrics are accurate and verifiable
- ✅ Recommendations are actionable
- ✅ Priority items identified
- ✅ Report is comprehensive and clear

## Clinical Considerations
- Clinical module complexity assessment
- Patient data handling analysis
- Audit trail completeness verification
- HIPAA compliance pattern analysis

## Example Usage
```bash
# Run repository analysis
python .hermes/scripts/repository_scan.py

# Generate health report
python .hermes/scripts/update_project_memory.py

# Run quality checks
ruff check .
mypy .

# Analyze test coverage
pytest --cov=. --cov-report=html
```
