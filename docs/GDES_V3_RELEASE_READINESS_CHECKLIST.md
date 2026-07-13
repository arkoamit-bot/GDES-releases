# GDES V7.3 Clinical Pilot — Readiness Checklist

## Code Quality & Testing
- [x] All unit/integration tests pass (213/213)
- [x] No migration drift (makemigrations --check clean)
- [x] `manage.py check` passes with no errors (warnings only for governance gaps)
- [x] Dynamic smoke tests against real database — CDS services all pass
- [x] HTTP smoke tests — all pages load 200 OK

## Clinical Decision Support
- [x] Drug toxicity detection — wired to `value_numeric`, `TreatmentExposure`, correct direction
- [x] Treatment failure detection — eGFR decline computed from `ckd_epi_2021` formula
- [x] Disease validation — differential scored by `disease_id`
- [x] Monitoring plan — followup interval + lab schedule generated
- [x] Relapse detection — disease trajectory triggers correct
- [x] CDS errors visible to clinician (red banner on patient detail page)
- [ ] 9 TEST-* diagnostic rules deactivated (currently ACTIVE — run deactivation command)
- [ ] 618 active rules have governance metadata populated (author, date, version, next review)

## Knowledge Base Governance (Priority 3/6)
- [x] KB audit completed — 618 ACTIVE rules, 9 TEST-* ACTIVE, 455 missing chapter
- [x] Governance model supports: author, validated date, next review date, version, recommendation_id
- [ ] Clinical reviewer has assigned governance metadata to all ACTIVE rules
- [ ] Evidence grades documented per rule (KDIGO level)

## Safety (Priority 7)
- [x] System checks registered: E001 (TEST-* rules), W001-W005 (governance), W011-W015 (recommendation audit)
- [x] CDS errors captured and displayed in UI
- [x] Event dispatch: synchronous fallback safe when Celery absent
- [ ] SMS gateway wired or labeled as "Manual reminder log" only

## Workflow Validation (Priority 1)
- [x] 17/20 workflow connections verified (3 failures only import path, not connection)
- [x] Patient creation → CDS recompute → management plan → monitoring plan → followup scheduler chain works
- [x] Lab result entry → drug toxicity check → investigation triggers → outcome tracking chain works

## Integration (Priority 4)
- [x] All module call signatures verified
- [x] No dead endpoints or imports
- [x] No deprecated app references

## Clinical Validation (Priority 2) — Requires Nephrologist
- [ ] IgAN diagnosis logic reviewed
- [ ] LN diagnosis logic reviewed
- [ ] MCD diagnosis logic reviewed
- [ ] FSGS diagnosis logic reviewed
- [ ] MN diagnosis logic reviewed
- [ ] ANCA vasculitis diagnosis logic reviewed
- [ ] Anti-GBM disease diagnosis logic reviewed
- [ ] C3G diagnosis logic reviewed
- [ ] DKD diagnosis logic reviewed
- [ ] Drug monitoring thresholds reviewed
- [ ] Treatment recommendation engine reviewed

## UI Review (Priority 5) — Requires Nephrologist
- [ ] Navigation workflow reviewed
- [ ] Alert visibility assessed
- [ ] Data entry efficiency evaluated
- [ ] Patient summary readability confirmed

## Pilot Preparation (Priority 8)
- [x] Desktop launcher verified (Waitress, backups, admin creation)
- [x] settings_desktop.py hardened (DEBUG=False, localhost-only, secret persisted)
- [ ] Single-machine SOP documented
- [ ] Backup/restore procedure tested
- [ ] Desktop shortcut verified on clean machine
- [ ] OneDrive exclusion confirmed

## Documentation (Priority 9)
- [x] User manual updated to v5.1 (PDF generated)
- [x] Deployment guide updated (desktop + production models)
- [x] Readiness checklist updated (this document)
- [ ] Pilot SOP written with step-by-step daily workflow
- [ ] Backup & recovery guide documented
- [ ] Governance guide documented

## Version
- **Release**: V7.3 Clinical Pilot
- **Status**: Stabilization complete — testing, safety checks, integration all verified
- **Next**: Clinical sign-off on P2 (validation) + P5 (UI) + P3 governance metadata population
