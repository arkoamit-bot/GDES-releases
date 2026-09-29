# Changelog

## Latest Changes (2026-09-29)

cc2787a Keep the pathology projection hook connected in production
36869d8 Link biopsy facts to one owner; carry the diagnosis into the next Rx
ffd744b Let the second clinic LAN (192.168.10.0/24) reach GDES
d661281 Fit the printed Rx to A4; admin-managed steroid taper templates
085f760 Make pathology finding-code choices deterministic
4fb0c11 Make the Tests workflow pass on Linux CI
9a02f0f Fix the two lint failures on the pull request
fe6971d Add a clinic-LAN server profile for Windows, beside the DKD registry
54fec85 Enlarge the printed prescription and print it in English
d463eb1 Link repeated clinical facts to one owner; structured renal histopathology
56f8071 Restore the CKD-EPI 2021 contract in the local eGFR implementation
b820265 Track the exports app and add the 2026-09-27 entry-linkage review
e004959 test: add V10 predictive intelligence tests (Sprints 7-12)
0ffdd60 fix: make V10 prediction functions return empty forecasts instead of raising on unknown patient
98b86ee feat: desktop pilot hardening — searchable drug picker, build self-check, health endpoint guard
779f57b Close registry security holes, fix clinical logic, widen strength fields
0908342 Refresh the drug database from MedEx, and keep it refreshed weekly
20b56d1 Fix app startup crash: gdes_core missing — add local CKD-EPI 2021 fallback
77dffa1 Add BDDrugBank importer for DrugMaster formulary enrichment
a09d3ba Make the reasoning and traceability panels useful
d3de657 Bundle gdes-core in the desktop build
afe5840 Record medication once; stop sending a drug history to Vera as allergies
aba6e08 Expose exposure -> outcome output; stop the same exposure counting twice
5be4978 Fix PowerShell scripts that could not parse on PS 5.1
69a7556 Remove OneDrive conflict copies; guard against both device suffixes
c07149c Fix the update package: 7.3.11 shipped 101 MB of junk and a missing app
91f9b7d chore: bump version to 7.3.11
ae980dd feat: V8 Clinical Intelligence Platform — CEI module, Vera Health, bug fixes
2ebfb1f State the ISN/RPS class once; reject contradictions
6edf3ef Fix template comments rendering as visible text

---

# Changelog

## Latest Changes (2026-07-23)

4af5fd2 docs: update changelog [skip ci]
fe46c9d fix: grant contents:write permission to changelog workflow
03279f8 feat: end-to-end clinical scenarios, KDIGO compliance, AI Factory regression tests
1245365 fix: resolve SQLite init_command + analytics test date cutoff issues
59102ba feat: clinical analytics dashboard, kidney survival prediction, patient trajectory
70f0979 feat: strengthen clinical reasoning with disease-specific care gaps, pathway stages, and enhanced explainability
e0b5d44 Phase 4 Sprint 1: Treatment Failure Detection
3fe7029 fix: Windows cloud-sync path detection on Linux CI runners
a555715 feat: implement egfr_decline treatment failure pattern (Sprint 1)
6422c8c test: add smoke tests for clinic, decision, users, treatments apps
b18450e fix: resolve all clinical_reasoning test failures (240/240 passing)
5dab71c fix: resolve view test failures — URL names, mock serialization, user permissions
fcf8e89 fix: add ruff configuration to resolve CI lint failures
1892c23 docs: consolidate documentation and create index
ab20da8 deps: update ruff requirement from ~=0.7.4 to ~=0.15.22
ff23094 fix: resolve CI test failures
579e3cd feat: enable CSP headers and rate limiting for security hardening
8c54030 feat: complete HERMES_MASTER_BOOTSTRAP.md implementation
677e0f6 feat: implement HERMES_SYSTEM.md and update agent definitions
569793a feat: bootstrap AI Factory v1.0 infrastructure and documentation
3bb8229 feat: AI Factory v1.0 — complete engineering platform
35ca62e refactor: complete clinic/views.py → clinic/views/ package split
48c9735 chore: remove __pycache__ from tracking
5d18312 refactor: address critical and high-priority issues

---

# Changelog

## Latest Changes (2026-07-23)

fe46c9d fix: grant contents:write permission to changelog workflow
03279f8 feat: end-to-end clinical scenarios, KDIGO compliance, AI Factory regression tests
1245365 fix: resolve SQLite init_command + analytics test date cutoff issues
59102ba feat: clinical analytics dashboard, kidney survival prediction, patient trajectory
70f0979 feat: strengthen clinical reasoning with disease-specific care gaps, pathway stages, and enhanced explainability
e0b5d44 Phase 4 Sprint 1: Treatment Failure Detection
6422c8c test: add smoke tests for clinic, decision, users, treatments apps
b18450e fix: resolve all clinical_reasoning test failures (240/240 passing)
5dab71c fix: resolve view test failures — URL names, mock serialization, user permissions
fcf8e89 fix: add ruff configuration to resolve CI lint failures
1892c23 docs: consolidate documentation and create index
ab20da8 deps: update ruff requirement from ~=0.7.4 to ~=0.15.22
ff23094 fix: resolve CI test failures
579e3cd feat: enable CSP headers and rate limiting for security hardening
8c54030 feat: complete HERMES_MASTER_BOOTSTRAP.md implementation
677e0f6 feat: implement HERMES_SYSTEM.md and update agent definitions
569793a feat: bootstrap AI Factory v1.0 infrastructure and documentation
3bb8229 feat: AI Factory v1.0 — complete engineering platform
35ca62e refactor: complete clinic/views.py → clinic/views/ package split
48c9735 chore: remove __pycache__ from tracking
5d18312 refactor: address critical and high-priority issues

---

