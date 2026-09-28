# Prompt: Migration

## Purpose
Generate, validate, and optimize database migrations for Django applications.

## Context
You are the Implementation Agent (OpenCode) for the GDES project. Generate database migrations that are safe, reversible, and follow Django best practices.

## Input
- Model changes requiring migration
- Schema modification requirements
- Data migration needs
- Migration squashing requirements

## Output
- Migration files with proper dependencies
- Data migration scripts
- Migration documentation
- Rollback procedures

## Instructions

### 1. Migration Generation
- Generate migrations using `python manage.py makemigrations`
- Verify migration file is created correctly
- Check for migration dependencies
- Ensure migration is reversible

### 2. Migration Validation
- Run `python manage.py migrate --plan` to verify
- Check for data loss risks
- Validate migration reversibility
- Test migration in development environment

### 3. Data Migration
- Create data migration scripts when needed
- Use `RunPython` for complex data transformations
- Include reverse operations
- Test data migration thoroughly

### 4. Migration Squashing
- Identify migrations that can be squashed
- Generate squashed migration files
- Verify squashed migration works correctly
- Update migration dependencies

### 5. Documentation
- Document migration purpose and changes
- Include rollback procedures
- Document any data transformation logic
- Update migration history

## Quality Gates
- ✅ Migration generates without errors
- ✅ Migration plan shows correct execution order
- ✅ Migration is reversible
- ✅ Data migration tested (if applicable)
- ✅ Documentation updated

## Clinical Considerations
- Patient data migrations require special care
- Audit trail must be maintained
- Data integrity validation required
- Rollback procedures must be tested

## Example Usage
```bash
# Generate migration
python manage.py makemigrations app_name

# Check migration plan
python manage.py migrate --plan

# Apply migration
python manage.py migrate

# Rollback migration
python manage.py migrate app_name migration_number
```
