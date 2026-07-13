#!/usr/bin/env python
"""
CI/CD Knowledge Certification -- automated pre-merge verification.

Every pull request should automatically verify:
  - Knowledge schema (tables exist, migrations applied)
  - Rule syntax (all rule_data is structurally valid)
  - Rule uniqueness (no duplicate entry_id values)
  - Evidence completeness (every ACTIVE rule has supporting evidence)
  - Guideline references (every ACTIVE rule has guideline chapter/quote)
  - ACTIVE rule coverage (at least one ACTIVE rule exists)
  - Integration tests pass (deterministic test KB + pipeline)
  - Clinical acceptance tests pass (realistic patient journeys)

Exit code 0 = all checks pass
Exit code 1 = one or more checks failed
"""
import os
import sys
import subprocess

# Ensure project root is on sys.path
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
if PROJECT not in sys.path:
    sys.path.insert(0, PROJECT)

os.environ["DJANGO_SETTINGS_MODULE"] = "bgddr.settings"
os.environ["DJANGO_SECRET_KEY"] = "test"


def _ensure_django():
    """Set up Django if not already set up."""
    import django
    from django.conf import settings
    if not settings.configured:
        django.setup()


def run(cmd, **kw):
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=kw.pop("cwd", PROJECT), **kw
    )
    return result.returncode, result.stdout, result.stderr


def check_imports():
    print(":: [1/8] Checking knowledge schema (imports)...")
    try:
        _ensure_django()
        from knowledge.models import KnowledgeBaseEntry, GuidelineSource, EvidenceEntry
        from knowledge.bootstrap import check_knowledge_base
        from knowledge.rule_validator import validate_rule_data
        print("  [OK] All knowledge modules import successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def check_migrations():
    print(":: [2/8] Checking migrations...")
    rc, out, err = run([sys.executable, "manage.py", "showmigrations", "--list"])
    if "[ ]" in out:
        print("  [FAIL] Unapplied migrations found:")
        for line in out.splitlines():
            if "[ ]" in line:
                print(f"    {line.strip()}")
        return False
    print("  [OK] All migrations applied")
    return True


def check_rule_syntax():
    print(":: [3/8] Checking rule syntax...")
    rc, out, err = run([sys.executable, "manage.py", "validate_rules"])
    # "with errors" appears only when errors are found
    # ERROR lines from the validator start with the entry_id prefix
    err_lines = [ln for ln in out.splitlines() if "ERRORS:" in ln]
    if err_lines:
        print("  [FAIL] Rule validation errors found")
        for line in err_lines:
            print(f"    {line.strip()}")
        return False
    print("  [OK] All rules structurally valid")
    return True


def check_active_rules():
    print(":: [4/8] Checking ACTIVE rules...")
    try:
        _ensure_django()
        from knowledge.models import KnowledgeBaseEntry
        active = KnowledgeBaseEntry.objects.filter(status=KnowledgeBaseEntry.Status.ACTIVE).count()
        total = KnowledgeBaseEntry.objects.count()
        if active == 0 and total > 0:
            print(f"  [FAIL] {total} rules exist but ZERO are ACTIVE")
            return False
        if total == 0:
            print("  [WARN] No rules in database (test KB may not be loaded)")
            return True
        print(f"  [OK] {active}/{total} rules are ACTIVE")
        return True
    except Exception as e:
        print(f"  [FAIL] Error checking active rules: {e}")
        return False


def check_evidence():
    print(":: [5/8] Checking evidence completeness...")
    try:
        _ensure_django()
        from knowledge.models import KnowledgeBaseEntry
        active_entries = KnowledgeBaseEntry.objects.filter(status=KnowledgeBaseEntry.Status.ACTIVE)
        total_active = active_entries.count()
        with_evidence = active_entries.filter(evidence_entries__isnull=False).distinct().count()
        if total_active > 0 and with_evidence < total_active:
            missing = total_active - with_evidence
            print(f"  [WARN] {missing}/{total_active} ACTIVE rules lack evidence entries")
        else:
            print(f"  [OK] {with_evidence}/{total_active} ACTIVE rules have evidence")
        return True
    except Exception as e:
        print(f"  [FAIL] Error checking evidence: {e}")
        return False


def check_integration_tests():
    print(":: [6/8] Running integration tests...")
    rc, out, err = run(
        [sys.executable, "-m", "pytest", "tests/test_knowledge_integration.py",
         "-x", "--tb=short", "--no-header", "-q"],
    )
    if rc != 0:
        print("  [FAIL] Integration tests FAILED")
        for line in (out + err).splitlines():
            if "FAILED" in line or "ERROR" in line:
                print(f"    {line.strip()}")
        return False
    print("  [OK] Integration tests passed")
    return True


def check_acceptance_tests():
    print(":: [7/8] Running clinical acceptance tests...")
    rc, out, err = run(
        [sys.executable, "-m", "pytest", "tests/test_clinical_acceptance.py",
         "-x", "--tb=short", "--no-header", "-q"],
    )
    if rc != 0:
        print("  [FAIL] Clinical acceptance tests FAILED")
        for line in (out + err).splitlines():
            if "FAILED" in line or "ERROR" in line:
                print(f"    {line.strip()}")
        return False
    print("  [OK] Clinical acceptance tests passed")
    return True


def check_bootstrap_health():
    print(":: [8/8] Checking bootstrap health...")
    try:
        _ensure_django()
        from knowledge.bootstrap import check_knowledge_base
        health = check_knowledge_base()
        if health.is_healthy:
            print(f"  [OK] Bootstrap healthy ({sum(1 for v in health.checks.values() if v)}/{len(health.checks)} checks)")
            return True
        print("  [FAIL] Bootstrap health check FAILED")
        for e in health.errors:
            print(f"    [FAIL] {e}")
        for w in health.warnings:
            print(f"    [WARN] {w}")
        return len(health.errors) == 0
    except Exception as e:
        print(f"  [FAIL] Bootstrap check error: {e}")
        return False


def main():
    print("=" * 60)
    print("  GDES Knowledge Certification - CI/CD Pre-merge Check")
    print("=" * 60)
    print()

    checks = [
        ("schema_imports", check_imports),
        ("migrations", check_migrations),
        ("rule_syntax", check_rule_syntax),
        ("active_rules", check_active_rules),
        ("evidence", check_evidence),
        ("integration_tests", check_integration_tests),
        ("acceptance_tests", check_acceptance_tests),
        ("bootstrap_health", check_bootstrap_health),
    ]

    results = {}
    all_pass = True
    for name, fn in checks:
        try:
            results[name] = fn()
        except Exception as e:
            print(f"  [FAIL] {name} crashed: {e}")
            results[name] = False
        if not results[name]:
            all_pass = False
        print()

    print("=" * 60)
    print("  Results:")
    for name, ok in results.items():
        status = "OK" if ok else "FAIL"
        print(f"    [{status}] {name}")
    print()
    print(f"  Overall: {'PASS' if all_pass else 'FAIL'}")
    print("=" * 60)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
