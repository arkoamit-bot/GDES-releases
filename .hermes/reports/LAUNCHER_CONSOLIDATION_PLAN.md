# Launcher Consolidation Plan

## Current State

| File | LOC | Branding | Features |
|------|-----|----------|----------|
| `launcher.py` | 1,108 | GDES | Full: single-instance, hardening, OneDrive, auto-update |
| `launcher-Dr-Wasim.py` | 772 | GDES | Simplified: no single-instance, no hardening |
| `launcher-Dr-Wasim-2.py` | 910 | BGDDR | Middle: some features, BGDDR branding |

## Key Differences

### launcher.py (Production)
- Single-instance guard socket
- Hardening helpers import
- OneDrive folder suggestions (GDES-Backups/Media/Update)
- In-app update from GitHub Releases
- GDES branding throughout

### launcher-Dr-Wasim.py (Dr. Wasim's Version)
- No single-instance guard
- No hardening helpers
- Simpler folder handling
- No auto-update
- GDES branding

### launcher-Dr-Wasim-2.py (Dr. Wasim's Version 2)
- BGDDR branding (older)
- Some features from both
- Different folder naming (BGDDR-Backups/Media/Update)
- Has auto-update but simpler

## Recommendation

**Consolidate into a single launcher with configuration:**

1. Keep `launcher.py` as the canonical version
2. Add configuration options for:
   - Branding (GDES vs BGDDR)
   - Feature toggles (single-instance, hardening, auto-update)
   - Folder naming conventions
3. Create `launcher.config.json` for per-deployment customization
4. Archive `launcher-Dr-Wasim.py` and `launcher-Dr-Wasim-2.py`

## Risk Assessment
- **Risk Level:** MEDIUM
- **Impact:** Desktop deployment for clinic PCs
- **Mitigation:** Test on one PC before rolling out
- **Rollback:** Keep archived versions available

## Implementation Steps
1. Create configuration system
2. Refactor launcher.py to read config
3. Test on development machine
4. Deploy to one clinic PC
5. Roll out to all PCs
6. Archive old launchers
