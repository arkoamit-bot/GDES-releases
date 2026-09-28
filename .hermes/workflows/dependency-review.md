# Workflow: Dependency Review

## Purpose
Analyze, validate, and manage project dependencies for security, compatibility, and maintainability.

## Input
- Requirements files (requirements.txt, setup.py, etc.)
- Dependency versions and constraints
- Security vulnerability databases
- License information
- Compatibility matrices

## Output
- Dependency analysis report
- Security vulnerability assessment
- License compliance report
- Upgrade recommendations
- Dependency management plan

## Execution Steps

### 1. Dependency Inventory
- Parse requirements files
- Identify all direct dependencies
- Map transitive dependencies
- Document version constraints
- Check for dependency conflicts

### 2. Security Analysis
- Scan for known vulnerabilities
- Check CVE databases
- Validate dependency integrity
- Review security advisories
- Assess risk levels

### 3. Compatibility Check
- Test Python version compatibility
- Check Django version compatibility
- Verify OS compatibility
- Validate dependency interactions
- Test integration points

### 4. License Compliance
- Identify license types
- Check license compatibility
- Validate compliance requirements
- Document license obligations
- Review usage restrictions

### 5. Version Analysis
- Check for outdated dependencies
- Identify upgrade opportunities
-评估 breaking changes
- Plan upgrade strategy
- Test upgrade compatibility

### 6. Recommendations
- Prioritize security fixes
- Plan dependency upgrades
- Recommend version constraints
- Document migration steps
- Update requirements files

## Agent Responsibilities

### Hermes (Orchestrator)
- Coordinate dependency review
- Prioritize security fixes
- Plan upgrade strategies
- Report to Project Owner

### Repository Intelligence Agent
- Analyze dependency graph
- Detect vulnerabilities
- Check license compliance
- Generate dependency reports

### Implementation Agent (OpenCode)
- Update requirements files
- Test dependency upgrades
- Fix compatibility issues
- Document changes

### Architecture Agent (Claude Code)
- Review dependency architecture
- Validate upgrade strategies
- Assess impact on design
- Provide guidance

## Quality Gates
- ✅ No critical security vulnerabilities
- ✅ All dependencies have compatible licenses
- ✅ Version constraints are appropriate
- ✅ Upgrade path is documented
- ✅ Testing covers dependency changes

## Failure Handling
- Document dependency issues
- Prioritize critical vulnerabilities
- Plan remediation steps
- Schedule follow-up review
- Update dependency management plan

## Dependency Types

### Direct Dependencies
- Django framework
- Django REST Framework
- Clinical libraries
- Data processing libraries
- PDF generation tools

### Development Dependencies
- Testing frameworks
- Linting tools
- Type checking tools
- Documentation generators
- Build tools

### Transitive Dependencies
- Dependencies of dependencies
- Version compatibility chains
- Conflict resolution
- Update coordination

## Security Considerations
- Vulnerability scanning
- Integrity verification
- Version pinning
- Update frequency
- Risk assessment

## Frequency
- **Weekly:** Security vulnerability check
- **Monthly:** Full dependency review
- **Quarterly:** Dependency upgrade planning
- **After security advisories:** Immediate review
- **Before releases:** Comprehensive check
