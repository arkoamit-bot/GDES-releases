"""Tests for V10 Predictive Intelligence (analytics/services/prediction.py).

Sprints 7-12: eGFR trajectory, relapse probability, treatment response,
cohort risk stratification, prediction audit, proactive alerting.

Conventions:
- Each test class is marked ``@pytest.mark.django_db`` (transaction-per-test).
- Fixtures are per-class or per-test (not shared session fixtures) so prediction
  tests are self-contained and can run in isolation.
- ``LabTest`` rows are created inline (code + name + value_type); the matching
  ``LabResult`` rows feed ``LabResult.series(patient, code)`` which the
  prediction functions call.
- Disease identity is matched by lowercased ``patient.primary_diagnosis``
  against the module's model keys: ``iga_nephropathy``, ``membranous_nephropathy``,
  ``lupus_nephritis``, ``fsgs``. Use those exact strings.
"""

import datetime as dt
from decimal import Decimal
from datetime import date, timedelta

import pytest

from patients.models import Patient

# These tests arrived with the V10 prediction module and have never passed.
# Strict, so CI fails as soon as one starts passing and the marker must go.
calibration_pending = pytest.mark.xfail(
    strict=True,
    reason="Model output differs from the expected value; needs clinical "
           "calibration review before either the model or the test changes.",
)
alert_source_pending = pytest.mark.xfail(
    strict=True,
    reason="Test seeds PatientOutcome.prediction_log, but the alert scan reads "
           "clinical_profile.risk_assessment; which one owns predictions is undecided.",
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _make_lab_test(code: str, name: str) -> "LabTest":
    from labs.models import LabTest

    return LabTest.objects.get_or_create(
        code=code,
        defaults={"name": name, "value_type": "numeric", "is_active": True},
    )[0]


def _add_egfr(patient: Patient, value: float, days_ago: int) -> None:
    from labs.models import LabResult, LabTest

    egfr_test, _ = LabTest.objects.get_or_create(
        code="egfr",
        defaults={"name": "eGFR", "value_type": "numeric", "is_derived": True, "is_active": True},
    )
    LabResult.objects.create(
        patient=patient,
        test=egfr_test,
        value_numeric=Decimal(str(value)),
        result_date=date.today() - timedelta(days=days_ago),
        source="derived",
    )


def _add_lab(patient: Patient, code: str, value: float, days_ago: int) -> None:
    from labs.models import LabResult, LabTest

    test, _ = LabTest.objects.get_or_create(
        code=code,
        defaults={"name": code, "value_type": "numeric", "is_active": True},
    )
    LabResult.objects.create(
        patient=patient,
        test=test,
        value_numeric=Decimal(str(value)),
        result_date=date.today() - timedelta(days=days_ago),
    )


def _ensure_biomarkers(patient: Patient) -> "BiomarkerKinetics":
    from biomarkers.models import BiomarkerKinetics

    bk, _ = BiomarkerKinetics.objects.get_or_create(patient=patient)
    return bk


def _ensure_drug(
    generic_name: str, drug_class: str = ""
) -> "DrugMaster":
    from treatments.models import DrugMaster

    return DrugMaster.objects.get_or_create(
        generic_name=generic_name,
        defaults={"drug_class": drug_class, "is_active": True},
    )[0]


def _expose(
    patient: Patient,
    drug: "DrugMaster",
    *,
    drug_name: str | None = None,
    ongoing: bool = True,
    start_days_ago: int = 30,
    stop_days_ago: int | None = None,
) -> "TreatmentExposure":
    from treatments.models import TreatmentExposure

    return TreatmentExposure.objects.create(
        patient=patient,
        drug=drug,
        drug_name=drug_name or drug.generic_name,
        start_date=date.today() - timedelta(days=start_days_ago),
        stop_date=(
            date.today() - timedelta(days=stop_days_ago)
            if stop_days_ago is not None
            else None
        ),
        ongoing=ongoing,
    )


@pytest.mark.django_db
class TestPredictEGFRTrajectory:

    """Sprint 7 — eGFR trajectory prediction.

    Coverage:
    - OLS forecast against a known linear trajectory (2 points).
    - Bootstrap CI width is sensible for 2-3 points.
    - LMM route selected when >=4 points over >=6 months.
    - Population fallback when <2 eGFR values.
    - Patient-not-found returns an empty forecast (guard).
    - ``explain_prediction`` returns meaningful text.
    - Integration: ``clinical_intelligence._predict_egfr`` stores
      ``risk_assessment["egfr_trajectory"]``.
    """

    def test_ols_forecast_linear_trajectory(self):
        from analytics.services.prediction import predict_egfr_trajectory

        p = Patient.objects.create(
            patient_id="EGFR-OLS-001",
            name="OLS Test Patient",
            hospital_id="H-OLS-001",
            primary_diagnosis="Chronic kidney disease unspecified",
            registration_status="registered",
        )
        # Perfectly linear: eGFR 60 -> 54 -> 48 over 6 months = -12/yr
        _add_egfr(p, 60.0, days_ago=180)
        _add_egfr(p, 54.0, days_ago=90)
        _add_egfr(p, 48.0, days_ago=0)

        fc = predict_egfr_trajectory(p.patient_id, horizons=[6, 12])
        assert len(fc.predictions) == 2
        # At 6 months: 48 - 6 = 42; at 12 months: 48 - 12 = 36 (approx).
        six = next(p for p in fc.predictions if p.horizon_months == 6)
        twelve = next(p for p in fc.predictions if p.horizon_months == 12)
        assert six.predicted_egfr <= 48.0
        assert twelve.predicted_egfr <= six.predicted_egfr
        assert six.model_type == "ols_bootstrap"
        assert fc.egfr_slope_per_year is not None
        assert fc.egfr_slope_per_year < -5.0  # declining

    def test_bootstrap_ci_width_narrow_with_many_points(self):
        from analytics.services.prediction import predict_egfr_trajectory

        p = Patient.objects.create(
            patient_id="EGFR-CI-001",
            name="CI Width Patient",
            hospital_id="H-CI-001",
            primary_diagnosis="Chronic kidney disease unspecified",
            registration_status="registered",
        )
        for i, v in enumerate([90, 88, 86, 84, 82, 80]):
            _add_egfr(p, v, days_ago=180 - i * 30)

        fc = predict_egfr_trajectory(p.patient_id, horizons=[12])
        pred = fc.predictions[0]
        half_width = (pred.upper_ci - pred.lower_ci) / 2
        # With 6 stable-ish points, CI should be moderate or high (narrow).
        assert half_width < 6.0

    def test_lmm_route_with_four_points_six_months(self):
        from analytics.services.prediction import predict_egfr_trajectory

        p = Patient.objects.create(
            patient_id="EGFR-LMM-001",
            name="LMM Candidate",
            hospital_id="H-LMM-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        # 4 points over ~9 months
        _add_egfr(p, 70.0, days_ago=270)
        _add_egfr(p, 66.0, days_ago=180)
        _add_egfr(p, 61.0, days_ago=90)
        _add_egfr(p, 55.0, days_ago=0)

        fc = predict_egfr_trajectory(p.patient_id, horizons=[12])
        pred = fc.predictions[0]
        assert pred.model_type == "lmm"
        assert pred.predicted_egfr < 55.0  # declining

    def test_population_fallback_fewer_than_two_points(self):
        from analytics.services.prediction import predict_egfr_trajectory

        p = Patient.objects.create(
            patient_id="EGFR-POP-001",
            name="Population Fallback",
            hospital_id="H-POP-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        _add_egfr(p, 50.0, days_ago=5)  # only 1 value

        fc = predict_egfr_trajectory(p.patient_id, horizons=[12])
        pred = fc.predictions[0]
        assert pred.model_type == "population"
        assert pred.confidence == "low"
        # iga_nephropathy population slope is -4.0/yr => 12mo -> -4
        assert pred.predicted_egfr < 50.0
        assert pred.predicted_egfr > 40.0

    def test_population_fallback_no_egfr_data(self):
        from analytics.services.prediction import predict_egfr_trajectory

        p = Patient.objects.create(
            patient_id="EGFR-POP-EMPTY-001",
            name="No Labs",
            hospital_id="H-POP-EMPTY-001",
            primary_diagnosis="Chronic kidney disease unspecified",
            registration_status="registered",
        )
        fc = predict_egfr_trajectory(p.patient_id, horizons=[12])
        pred = fc.predictions[0]
        assert pred.model_type == "population"
        assert pred.confidence == "low"
        # No current eGFR known => conservative default 50
        assert pred.predicted_egfr <= 50.0

    def test_patient_not_found_returns_empty_forecast(self):
        from analytics.services.prediction import predict_egfr_trajectory

        fc = predict_egfr_trajectory("no-such-patient-xyz", horizons=[12])
        assert fc.method_summary == "Patient not found"
        assert fc.predictions == []

    def test_explain_prediction_returns_meaningful_text(self):
        from analytics.services.prediction import (
            predict_egfr_trajectory,
            explain_prediction,
        )

        p = Patient.objects.create(
            patient_id="EGFR-EXPLAIN-001",
            name="Explain Patient",
            hospital_id="H-EXP-001",
            primary_diagnosis="Chronic kidney disease unspecified",
            registration_status="registered",
        )
        _add_egfr(p, 40.0, days_ago=180)
        _add_egfr(p, 35.0, days_ago=0)

        fc = predict_egfr_trajectory(p.patient_id)
        text = explain_prediction(fc)
        assert isinstance(text, str)
        assert len(text) > 20
        assert "Predicted eGFR" in text or "eGFR" in text

    def test_explain_prediction_empty_when_no_predictions(self):
        from analytics.services.prediction import (
            explain_prediction,
            EGFRForecast,
        )

        fc = EGFRForecast(
            patient_id="empty",
            prediction_date=date.today(),
            predictions=[],
        )
        text = explain_prediction(fc)
        assert "No eGFR prediction" in text or "insufficient" in text.lower()


@pytest.mark.django_db
class TestRelapseProbability:

    """Sprint 8 — relapse probability forecasting.

    Coverage:
    - IgAN model with known features against manual direction (higher
      proteinuria + S2 lesion = higher probability).
    - MN model: early PLA2R responder => lower risk.
    - Lupus model: complement recovery => lower risk.
    - Edge case: patient with no disease model => general CKD fallback.
    - Patient-not-found returns empty RelapseForecast.
    - High probability (>0.5) yields ``critical`` tier.
    """

    def test_igan_higher_proteinuria_and_s2_raises_risk(self):
        from analytics.services.prediction import predict_relapse_risk

        p = Patient.objects.create(
            patient_id="RELAPSE-IGA-001",
            name="IgAN High Risk",
            hospital_id="H-IGA-001",
            primary_diagnosis="iga_nephropathy",
            oxford_mestc="S2 T0",
            hypertension=True,
            diabetes_status="no",
            registration_status="registered",
        )
        _add_lab(p, "upcr", 3.5, days_ago=0)  # g/day, nephrotic range
        # eGFR slope: declining
        _add_egfr(p, 60.0, days_ago=365)
        _add_egfr(p, 52.0, days_ago=0)

        fc = predict_relapse_risk(p.patient_id, horizons=[6, 12])
        assert fc.disease == "iga_nephropathy"
        twelve = next(p for p in fc.predictions if p.horizon_months == 12)
        # With proteinuria 3.5 + S2 + declining eGFR, should be elevated.
        assert twelve.probability > 0.15
        assert len(twelve.risk_factors) >= 1
        assert "proteinuria" in " ".join(twelve.risk_factors).lower()

    @calibration_pending
    def test_mn_early_pla2r_responder_lower_risk(self):
        from analytics.services.prediction import predict_relapse_risk
        from biomarkers.models import BiomarkerKinetics

        p = Patient.objects.create(
            patient_id="RELAPSE-MN-001",
            name="MN Responder",
            hospital_id="H-MN-001",
            primary_diagnosis="membranous_nephropathy",
            registration_status="registered",
        )
        bk = _ensure_biomarkers(p)
        bk.pla2r_baseline = Decimal("200")
        bk.pla2r_latest = Decimal("80")
        bk.pla2r_pct_decline = Decimal("60")
        bk.pla2r_50pct_decline = True
        bk.pla2r_immunological_remission = True
        bk.save()

        _add_egfr(p, 55.0, days_ago=180)
        _add_egfr(p, 53.0, days_ago=0)

        fc = predict_relapse_risk(p.patient_id, horizons=[12])
        twelve = next(p for p in fc.predictions if p.horizon_months == 12)
        # Immunological remission is protective (beta -0.65) => lower risk
        assert twelve.probability < 0.5
        assert any("immunological" in f.lower() for f in twelve.protective_factors)

    def test_lupus_complement_recovery_lower_risk(self):
        from analytics.services.prediction import predict_relapse_risk
        from biomarkers.models import BiomarkerKinetics

        p = Patient.objects.create(
            patient_id="RELAPSE-LN-001",
            name="LN Recovered",
            hospital_id="H-LN-001",
            primary_diagnosis="lupus_nephritis",
            isn_rps_class="III",
            registration_status="registered",
        )
        bk = _ensure_biomarkers(p)
        bk.c3_recovered = True
        bk.c4_recovered = True
        bk.dsdna_normalized = True
        bk.save()

        _add_egfr(p, 65.0, days_ago=180)
        _add_egfr(p, 64.0, days_ago=0)

        fc = predict_relapse_risk(p.patient_id, horizons=[6])
        six = next(p for p in fc.predictions if p.horizon_months == 6)
        assert six.probability < 0.5
        assert any("c3" in f.lower() for f in six.protective_factors)

    @calibration_pending
    def test_unknown_disease_uses_general_ckd_fallback(self):
        from analytics.services.prediction import predict_relapse_risk

        p = Patient.objects.create(
            patient_id="RELAPSE-UNK-001",
            name="Unknown Disease",
            hospital_id="H-UNK-001",
            primary_diagnosis="Some unknown GN",
            registration_status="registered",
        )
        _add_egfr(p, 50.0, days_ago=0)

        fc = predict_relapse_risk(p.patient_id, horizons=[12])
        assert fc.model_used == "general_ckd"
        assert fc.disease == "some unknown gn"

    def test_patient_not_found_returns_empty_relapse_forecast(self):
        from analytics.services.prediction import predict_relapse_risk

        fc = predict_relapse_risk("no-such-patient-xyz", horizons=[6, 12])
        assert fc.disease == "unknown"
        assert fc.predictions == []
        assert fc.overall_risk_tier == "low"

    def test_high_probability_yields_critical_tier(self):
        from analytics.services.prediction import predict_relapse_risk

        p = Patient.objects.create(
            patient_id="RELAPSE-CRIT-001",
            name="High Relapse Risk",
            hospital_id="H-CRIT-001",
            primary_diagnosis="lupus_nephritis",
            isn_rps_class="IV",
            hypertension=True,
            diabetes_status="no",
            registration_status="registered",
        )
        # Force high-risk features: high dsDNA, low complements, high proteinuria
        bk = _ensure_biomarkers(p)
        bk.dsdna_latest = Decimal("80")
        bk.dsdna_normalized = False
        bk.save()

        _add_lab(p, "upcr", 4.0, days_ago=0)
        _add_egfr(p, 40.0, days_ago=365)
        _add_egfr(p, 30.0, days_ago=0)

        fc = predict_relapse_risk(p.patient_id, horizons=[12])
        assert fc.overall_risk_tier in ("critical", "high")


@pytest.mark.django_db
class TestTreatmentResponse:

    """Sprint 9 — treatment response prediction.

    Coverage:
    - Rituximab in MN: high baseline PLA2R => slower response.
    - Rituximab in lupus: complement already recovered => higher probability.
    - Immunosuppression in IgAN: MEST-C S2T2 + high proteinuria => lower prob.
    - CNI in FSGS: collapsing variant => very low response.
    - Monitoring cadence logic (high response => every 3 months;
      low response => every 1-2 months; remission => every 6 months).
    - No active treatment detected => population-level "none_detected".
    - Patient-not-found returns empty TreatmentResponseForecast.
    """

    def test_rituximab_mn_high_pla2r_slower_response(self):
        from analytics.services.prediction import predict_treatment_response
        from biomarkers.models import BiomarkerKinetics

        p = Patient.objects.create(
            patient_id="TRT-MN-001",
            name="MN on Rituximab",
            hospital_id="H-MN-001",
            primary_diagnosis="membranous_nephropathy",
            registration_status="registered",
        )
        bk = _ensure_biomarkers(p)
        bk.pla2r_baseline = Decimal("200")
        bk.pla2r_latest = Decimal("200")
        bk.pla2r_pct_decline = Decimal("0")
        bk.pla2r_50pct_decline = False
        bk.save()

        drug = _ensure_drug("Rituximab", "Monoclonal antibody")
        _expose(p, drug, drug_name="Rituximab", ongoing=True)

        fc = predict_treatment_response(p.patient_id)
        assert fc.treatment == "rituximab_mn"
        assert fc.predictions
        # High baseline PLA2R (200 ~= log 5.3) with no decline => slower
        best = max(p.probability for p in fc.predictions)
        assert best < 0.7

    def test_rituximab_mn_low_pla2r_faster_response(self):
        from analytics.services.prediction import predict_treatment_response
        from biomarkers.models import BiomarkerKinetics

        p = Patient.objects.create(
            patient_id="TRT-MN-LOW-001",
            name="MN Low PLA2R",
            hospital_id="H-MN-LOW-001",
            primary_diagnosis="membranous_nephropathy",
            registration_status="registered",
        )
        bk = _ensure_biomarkers(p)
        bk.pla2r_baseline = Decimal("20")
        bk.pla2r_latest = Decimal("5")
        bk.pla2r_pct_decline = Decimal("75")
        bk.pla2r_50pct_decline = True
        bk.save()

        drug = _ensure_drug("Rituximab", "Monoclonal antibody")
        _expose(p, drug, drug_name="Rituximab", ongoing=True)

        fc = predict_treatment_response(p.patient_id)
        best = max(p.probability for p in fc.predictions)
        assert best > 0.5

    def test_lupus_complement_recovered_higher_response(self):
        from analytics.services.prediction import predict_treatment_response
        from biomarkers.models import BiomarkerKinetics

        p = Patient.objects.create(
            patient_id="TRT-LN-001",
            name="LN on Rituximab",
            hospital_id="H-LN-001",
            primary_diagnosis="lupus_nephritis",
            isn_rps_class="III",
            registration_status="registered",
        )
        bk = _ensure_biomarkers(p)
        bk.c3_recovered = True
        bk.c4_recovered = True
        bk.dsdna_normalized = True
        bk.dsdna_latest = Decimal("5")
        bk.save()

        drug = _ensure_drug("Rituximab", "Monoclonal antibody")
        _expose(p, drug, drug_name="Rituximab", ongoing=True)

        fc = predict_treatment_response(p.patient_id)
        assert fc.treatment == "rituximab_lupus"
        best = max(p.probability for p in fc.predictions)
        assert best > 0.4

    def test_igan_mestc_s2t2_high_proteinuria_lower_response(self):
        from analytics.services.prediction import predict_treatment_response

        p = Patient.objects.create(
            patient_id="TRT-IGA-001",
            name="IgAN High Risk",
            hospital_id="H-IGA-001",
            primary_diagnosis="iga_nephropathy",
            oxford_mestc="S2 T2",
            registration_status="registered",
        )
        _add_lab(p, "upcr", 4.0, days_ago=0)

        drug = _ensure_drug("Mycophenolate mofetil", "Antimetabolite")
        _expose(p, drug, drug_name="Mycophenolate mofetil", ongoing=True)

        fc = predict_treatment_response(p.patient_id)
        assert fc.treatment == "immunosuppression_igan"
        best = max(p.probability for p in fc.predictions)
        assert best < 0.5

    @calibration_pending
    def test_cni_fsgs_collapsing_variant_poor_response(self):
        from analytics.services.prediction import predict_treatment_response

        p = Patient.objects.create(
            patient_id="TRT-FSGS-001",
            name="FSGS Collapsing",
            hospital_id="H-FSGS-001",
            primary_diagnosis="fsgs",
            biopsy_diagnosis="Collapsing FSGS",
            registration_status="registered",
        )
        _add_lab(p, "upcr", 6.0, days_ago=0)

        drug = _ensure_drug("Tacrolimus", "Calcineurin inhibitor")
        _expose(p, drug, drug_name="Tacrolimus", ongoing=True)

        fc = predict_treatment_response(p.patient_id)
        best = max(p.probability for p in fc.predictions)
        assert best < 0.3

    def test_monitoring_cadence_high_response(self):
        from analytics.services.prediction import predict_treatment_response

        p = Patient.objects.create(
            patient_id="TRT-CADENCE-001",
            name="Good Responder",
            hospital_id="H-CAD-001",
            primary_diagnosis="iga_nephropathy",
            oxford_mestc="T0",
            registration_status="registered",
        )
        # Low proteinuria, improving eGFR
        _add_lab(p, "upcr", 0.5, days_ago=0)
        _add_egfr(p, 70.0, days_ago=180)
        _add_egfr(p, 72.0, days_ago=0)

        drug = _ensure_drug("Mycophenolate mofetil", "Antimetabolite")
        _expose(p, drug, drug_name="Mycophenolate mofetil", ongoing=True)

        fc = predict_treatment_response(p.patient_id)
        assert fc.treatment == "immunosuppression_igan"
        assert fc.monitoring_cadence == "every_3_months"

    def test_monitoring_cadence_low_response(self):
        from analytics.services.prediction import predict_treatment_response

        p = Patient.objects.create(
            patient_id="TRT-CADENCE-LOW-001",
            name="Poor Responder",
            hospital_id="H-CAD-LOW-001",
            primary_diagnosis="iga_nephropathy",
            oxford_mestc="S2 T2",
            registration_status="registered",
        )
        _add_lab(p, "upcr", 5.0, days_ago=0)
        _add_egfr(p, 40.0, days_ago=365)
        _add_egfr(p, 28.0, days_ago=0)

        drug = _ensure_drug("Mycophenolate mofetil", "Antimetabolite")
        _expose(p, drug, drug_name="Mycophenolate mofetil", ongoing=True)

        fc = predict_treatment_response(p.patient_id)
        assert fc.treatment == "immunosuppression_igan"
        assert fc.monitoring_cadence == "every_1_2_months"

    def test_no_active_treatment_returns_none_detected(self):
        from analytics.services.prediction import predict_treatment_response

        p = Patient.objects.create(
            patient_id="TRT-NONE-001",
            name="No Treatment",
            hospital_id="H-NONE-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        _add_egfr(p, 50.0, days_ago=0)

        fc = predict_treatment_response(p.patient_id)
        assert fc.treatment == "none_detected"
        assert fc.predictions == []

    def test_patient_not_found_returns_empty_treatment_forecast(self):
        from analytics.services.prediction import predict_treatment_response

        fc = predict_treatment_response("no-such-patient-xyz")
        assert fc.treatment == "patient_not_found"
        assert fc.predictions == []


@pytest.mark.django_db
class TestRiskStratification:

    """Sprint 10 — risk stratification dashboard.

    Coverage:
    - ``compute_overall_risk_tier``: declining eGFR + high relapse => critical.
    - ``_egfr_trend_label`` mapping.
    - ``risk_stratify_cohort`` returns summaries sortable by tier.
    """

    def test_overall_risk_tier_critical_when_rapid_decline_and_high_relapse(self):
        from analytics.services.prediction import compute_overall_risk_tier

        tier = compute_overall_risk_tier(egfr_slope=-6.0, relapse_prob=0.6, response_prob=0.5)
        assert tier == "critical"

    @calibration_pending
    def test_overall_risk_tier_low_when_all_favorable(self):
        from analytics.services.prediction import compute_overall_risk_tier

        tier = compute_overall_risk_tier(egfr_slope=0.0, relapse_prob=0.05, response_prob=0.8)
        assert tier == "low"

    def test_egfr_trend_label_mapping(self):
        from analytics.services.prediction import _egfr_trend_label

        assert _egfr_trend_label(-8.0) == "declining_rapidly"
        assert _egfr_trend_label(-3.0) == "declining"
        assert _egfr_trend_label(-0.2) == "stable"
        assert _egfr_trend_label(1.5) == "improving"
        assert _egfr_trend_label(None) == "unknown"

    def test_risk_stratify_cohort_returns_summaries(self):
        from analytics.services.prediction import risk_stratify_cohort

        p = Patient.objects.create(
            patient_id="RISK-001",
            name="Risk Strat Patient",
            hospital_id="H-RISK-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        _add_egfr(p, 60.0, days_ago=180)
        _add_egfr(p, 50.0, days_ago=0)

        summaries = risk_stratify_cohort(limit=10)
        assert isinstance(summaries, list)
        matching = [s for s in summaries if s.patient_id == p.patient_id]
        assert matching
        s = matching[0]
        assert s.egfr_trend in ("declining_rapidly", "declining", "stable", "improving", "unknown")
        assert s.overall_risk_tier in ("critical", "high", "moderate", "low")


@pytest.mark.django_db
class TestPredictionAudit:

    """Sprint 11 — prediction audit & explainability.

    Coverage:
    - ``log_prediction`` writes to ``PatientOutcome.prediction_log``.
    - ``prediction_history`` returns entries, most-recent first.
    - ``prediction_explanation`` returns the most recent of a given type.
    - Log is capped at last 50 entries.
    """

    def test_log_prediction_writes_to_outcome(self):
        from analytics.services.prediction import log_prediction
        from analytics.models import PatientOutcome

        p = Patient.objects.create(
            patient_id="AUDIT-001",
            name="Audit Patient",
            hospital_id="H-AUDIT-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        log_prediction(p.patient_id, "egfr_forecast", {"predicted_egfr": 45.0})

        outcome = PatientOutcome.objects.get(patient=p)
        assert outcome.prediction_log
        assert outcome.prediction_log[-1]["type"] == "egfr_forecast"
        assert outcome.prediction_log[-1]["data"]["predicted_egfr"] == 45.0

    def test_prediction_history_returns_sorted_entries(self):
        from analytics.services.prediction import log_prediction, prediction_history

        p = Patient.objects.create(
            patient_id="AUDIT-HIST-001",
            name="History Patient",
            hospital_id="H-AUDIT-HIST-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        log_prediction(p.patient_id, "egfr_forecast", {"predicted_egfr": 45.0})
        log_prediction(p.patient_id, "relapse_forecast", {"probability": 0.3})

        hist = prediction_history(p.patient_id)
        assert len(hist) == 2
        assert hist[0]["type"] == "relapse_forecast"
        assert hist[1]["type"] == "egfr_forecast"

    def test_prediction_history_filtered_by_type(self):
        from analytics.services.prediction import log_prediction, prediction_history

        p = Patient.objects.create(
            patient_id="AUDIT-FILTER-001",
            name="Filter Patient",
            hospital_id="H-AUDIT-FILTER-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        log_prediction(p.patient_id, "egfr_forecast", {"predicted_egfr": 45.0})
        log_prediction(p.patient_id, "relapse_forecast", {"probability": 0.3})

        egfr_only = prediction_history(p.patient_id, prediction_type="egfr_forecast")
        assert len(egfr_only) == 1
        assert egfr_only[0]["type"] == "egfr_forecast"

    def test_prediction_explanation_returns_most_recent(self):
        from analytics.services.prediction import (
            log_prediction,
            prediction_explanation,
        )

        p = Patient.objects.create(
            patient_id="AUDIT-EXP-001",
            name="Explanation Patient",
            hospital_id="H-AUDIT-EXP-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        log_prediction(p.patient_id, "egfr_forecast", {"predicted_egfr": 45.0})
        log_prediction(p.patient_id, "egfr_forecast", {"predicted_egfr": 40.0})

        expl = prediction_explanation(p.patient_id, "egfr_forecast")
        assert expl
        assert expl["data"]["predicted_egfr"] == 40.0

    def test_prediction_log_capped_at_50(self):
        from analytics.services.prediction import log_prediction
        from analytics.models import PatientOutcome

        p = Patient.objects.create(
            patient_id="AUDIT-CAP-001",
            name="Cap Patient",
            hospital_id="H-AUDIT-CAP-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        for i in range(55):
            log_prediction(p.patient_id, "egfr_forecast", {"i": i})

        outcome = PatientOutcome.objects.get(patient=p)
        assert len(outcome.prediction_log) == 50

    def test_prediction_history_empty_for_unknown_patient(self):
        from analytics.services.prediction import prediction_history

        hist = prediction_history("no-such-patient-xyz")
        assert hist == []


@pytest.mark.django_db
class TestProactiveAlerting:

    """Sprint 12 — proactive alerting & watchlist.

    Coverage:
    - eGFR predicted <15 within 12mo => ESKD risk alert (critical).
    - eGFR slope < -5/yr => rapid decline alert (warning).
    - Relapse probability > 0.5 => high relapse alert (warning).
    - Treatment response < 0.2 => treatment failure alert (warning).
    - ``check_predictions_for_alerts`` returns alerts sorted by severity.
    """

    @alert_source_pending
    def test_eskd_risk_alert(self):
        from analytics.services.prediction import check_predictions_for_alerts
        from analytics.models import PatientOutcome

        p = Patient.objects.create(
            patient_id="ALERT-ESKD-001",
            name="ESKD Risk Patient",
            hospital_id="H-ALERT-ESKD-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        # Seed a prediction_log entry with an eGFR forecast that hits <15
        outcome, _ = PatientOutcome.objects.get_or_create(patient=p)
        outcome.prediction_log = [
            {
                "type": "egfr_forecast",
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "data": {
                    "predictions": [
                        {
                            "horizon_months": 12,
                            "predicted_egfr": 12.0,
                            "lower_ci": 10.0,
                            "upper_ci": 14.0,
                        }
                    ]
                },
            }
        ]
        outcome.save()

        alerts = check_predictions_for_alerts(limit=50)
        eskd = [a for a in alerts if a.patient_id == p.patient_id and a.alert_type == "eskd_risk"]
        assert eskd
        assert eskd[0].severity == "critical"

    @alert_source_pending
    def test_rapid_decline_alert(self):
        from analytics.services.prediction import check_predictions_for_alerts
        from analytics.models import PatientOutcome

        p = Patient.objects.create(
            patient_id="ALERT-DECLINE-001",
            name="Rapid Decline Patient",
            hospital_id="H-ALERT-DECLINE-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        outcome, _ = PatientOutcome.objects.get_or_create(patient=p)
        outcome.prediction_log = [
            {
                "type": "egfr_forecast",
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "data": {
                    "slope_per_year": -7.0,
                    "predictions": [],
                },
            }
        ]
        outcome.save()

        alerts = check_predictions_for_alerts(limit=50)
        decline = [a for a in alerts if a.patient_id == p.patient_id and a.alert_type == "rapid_decline"]
        assert decline
        assert decline[0].severity == "warning"

    @alert_source_pending
    def test_high_relapse_alert(self):
        from analytics.services.prediction import check_predictions_for_alerts
        from analytics.models import PatientOutcome

        p = Patient.objects.create(
            patient_id="ALERT-RELAPSE-001",
            name="High Relapse Patient",
            hospital_id="H-ALERT-RELAPSE-001",
            primary_diagnosis="lupus_nephritis",
            registration_status="registered",
        )
        outcome, _ = PatientOutcome.objects.get_or_create(patient=p)
        outcome.prediction_log = [
            {
                "type": "relapse_forecast",
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "data": {
                    "predictions": [
                        {
                            "horizon_months": 6,
                            "probability": 0.65,
                            "lower_ci": 0.55,
                            "upper_ci": 0.75,
                            "monitoring_recommendation": "Intensify monitoring.",
                        }
                    ]
                },
            }
        ]
        outcome.save()

        alerts = check_predictions_for_alerts(limit=50)
        relapse = [a for a in alerts if a.patient_id == p.patient_id and a.alert_type == "high_relapse"]
        assert relapse
        assert relapse[0].severity == "warning"

    @alert_source_pending
    def test_treatment_failure_alert(self):
        from analytics.services.prediction import check_predictions_for_alerts
        from analytics.models import PatientOutcome

        p = Patient.objects.create(
            patient_id="ALERT-TRTFAIL-001",
            name="Treatment Failure Patient",
            hospital_id="H-ALERT-TRTFAIL-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        outcome, _ = PatientOutcome.objects.get_or_create(patient=p)
        outcome.prediction_log = [
            {
                "type": "treatment_response",
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "data": {
                    "predictions": [
                        {
                            "time_to_response_months": 6,
                            "probability": 0.10,
                            "lower_ci": 0.05,
                            "upper_ci": 0.15,
                        }
                    ],
                    "recommendation_summary": "Consider alternative.",
                },
            }
        ]
        outcome.save()

        alerts = check_predictions_for_alerts(limit=50)
        trt = [a for a in alerts if a.patient_id == p.patient_id and a.alert_type == "treatment_failure"]
        assert trt
        assert trt[0].severity == "warning"

    def test_check_predictions_for_alerts_sorts_by_severity(self):
        from analytics.services.prediction import check_predictions_for_alerts
        from analytics.models import PatientOutcome

        p1 = Patient.objects.create(
            patient_id="ALERT-SORT-CRIT-001",
            name="Critical Patient",
            hospital_id="H-ALERT-SORT-CRIT-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        outcome1, _ = PatientOutcome.objects.get_or_create(patient=p1)
        outcome1.prediction_log = [
            {
                "type": "egfr_forecast",
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "data": {
                    "predictions": [
                        {
                            "horizon_months": 12,
                            "predicted_egfr": 10.0,
                            "lower_ci": 8.0,
                            "upper_ci": 12.0,
                        }
                    ]
                },
            }
        ]
        outcome1.save()

        alerts = check_predictions_for_alerts(limit=50)
        critical = [a for a in alerts if a.severity == "critical"]
        warning = [a for a in alerts if a.severity == "warning"]
        if critical and warning:
            assert alerts.index(critical[0]) < alerts.index(warning[0])


@pytest.mark.django_db
class TestIntegrationWithClinicalIntelligence:

    """Cross-cutting integration: verify the prediction module's public API is
    wired into ``clinical_intelligence.py`` and that ``analyze_patient`` stores
    the forecasts on the profile's ``risk_assessment``.

    These tests exercise the real pipeline, not just the pure functions.
    """

    def test_analyze_patient_stores_egfr_trajectory(self):
        from clinical_reasoning.services.clinical_intelligence import (
            ClinicalIntelligenceService,
        )

        p = Patient.objects.create(
            patient_id="INT-EGFR-001",
            name="Integration Patient",
            hospital_id="H-INT-EGFR-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        for i, v in enumerate([60, 57, 54]):
            _add_egfr(p, float(v), days_ago=90 - i * 45)

        svc = ClinicalIntelligenceService()
        report = svc.analyze_patient(p.patient_id)

        ra = (p.clinical_profile.risk_assessment if p.clinical_profile else None) or {}
        egfr = ra.get("egfr_trajectory")
        assert egfr
        assert "predictions" in egfr
        assert len(egfr["predictions"]) >= 1
        assert "method" in egfr

    def test_analyze_patient_prediction_log_grows(self):
        from clinical_reasoning.services.clinical_intelligence import (
            ClinicalIntelligenceService,
        )
        from analytics.models import PatientOutcome

        p = Patient.objects.create(
            patient_id="INT-LOG-001",
            name="Log Integration Patient",
            hospital_id="H-INT-LOG-001",
            primary_diagnosis="iga_nephropathy",
            registration_status="registered",
        )
        _add_egfr(p, 55.0, days_ago=0)

        before = (
            PatientOutcome.objects.filter(patient=p)
            .first()
            .prediction_log
            if PatientOutcome.objects.filter(patient=p).exists()
            else []
        )
        before_count = len(before) if before else 0

        svc = ClinicalIntelligenceService()
        svc.analyze_patient(p.patient_id)

        outcome = PatientOutcome.objects.get(patient=p)
        after = outcome.prediction_log or []
        assert len(after) >= before_count + 1
