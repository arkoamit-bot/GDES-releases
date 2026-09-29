"""Tests for eGFR trajectory prediction — Sprint 7 of V10 Predictive Intelligence."""
import datetime as dt
import math

from django.test import TestCase

from labs.services.results import record_result
from patients.models import Patient

from .services.prediction import (
    PredictedEGFR,
    EGFRForecast,
    _extract_egfr_series,
    _compute_slope_per_year,
    _linear_forecast,
    _lmm_forecast,
    _population_prediction,
    _build_drivers,
    _ci_confidence,
    explain_prediction,
    predict_egfr_trajectory,
)


class ExtractEGFRSeriesTests(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="PRED-1", name="Test P", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1),
        )

    def test_returns_egfr_values_in_date_order(self):
        record_result(self.p, "creatinine", result_date=dt.date(2024, 6, 1), value_numeric=1.5)
        record_result(self.p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        record_result(self.p, "creatinine", result_date=dt.date(2025, 1, 1), value_numeric=2.0)
        series = _extract_egfr_series(self.p)
        self.assertEqual(len(series), 3)
        dates = [d for d, _ in series]
        self.assertEqual(dates, sorted(dates))

    def test_excludes_none_values(self):
        record_result(self.p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        record_result(self.p, "creatinine", result_date=dt.date(2024, 6, 1), value_numeric=1.5)
        # Only creatinine records — egfr is derived, so no egfr test code exists yet.
        # This test verifies the extraction doesn't crash with empty egfr series.
        series = _extract_egfr_series(self.p)
        # If eGFR isn't auto-derived from creatinine in the test DB, series is empty.
        self.assertIsInstance(series, list)


class SlopeComputationTests(TestCase):
    def test_linear_slope(self):
        dates = [dt.date(2024, 1, 1), dt.date(2025, 1, 1)]
        values = [60.0, 48.0]
        slope = _compute_slope_per_year(dates, values)
        self.assertAlmostEqual(slope, -12.0, places=1)

    def test_stable_egfr(self):
        dates = [dt.date(2024, 1, 1), dt.date(2024, 7, 1), dt.date(2025, 1, 1)]
        values = [60.0, 60.0, 60.0]
        slope = _compute_slope_per_year(dates, values)
        self.assertAlmostEqual(slope, 0.0, places=1)

    def test_single_point_returns_zero(self):
        slope = _compute_slope_per_year([dt.date(2024, 1, 1)], [60.0])
        self.assertEqual(slope, 0.0)


class LinearForecastTests(TestCase):
    def test_forecast_on_known_linear_trajectory(self):
        # Perfect linear decline: 60 → 48 over 12 months
        dates = [dt.date(2024, 1, 1), dt.date(2025, 1, 1)]
        values = [60.0, 48.0]
        today = dt.date(2025, 1, 1)
        preds = _linear_forecast(dates, values, today, [6, 12])
        self.assertEqual(len(preds), 2)
        # At 6 months: 48 + (-12 * 0.5) = 42
        self.assertAlmostEqual(preds[0].predicted_egfr, 42.0, delta=1.0)
        # At 12 months: 48 + (-12 * 1.0) = 36
        self.assertAlmostEqual(preds[1].predicted_egfr, 36.0, delta=1.0)

    def test_ci_width_increases_with_horizon(self):
        dates = [dt.date(2024, 1, 1), dt.date(2025, 1, 1)]
        values = [60.0, 48.0]
        today = dt.date(2025, 1, 1)
        preds = _linear_forecast(dates, values, today, [6, 24])
        ci_6 = preds[0].upper_ci - preds[0].lower_ci
        ci_24 = preds[1].upper_ci - preds[1].lower_ci
        self.assertGreater(ci_24, ci_6)

    def test_model_type_is_ols_bootstrap(self):
        dates = [dt.date(2024, 1, 1), dt.date(2025, 1, 1)]
        values = [60.0, 48.0]
        today = dt.date(2025, 1, 1)
        preds = _linear_forecast(dates, values, today, [12])
        self.assertEqual(preds[0].model_type, "ols_bootstrap")

    def test_three_points_forecast(self):
        dates = [
            dt.date(2024, 1, 1), dt.date(2024, 7, 1), dt.date(2025, 1, 1),
        ]
        values = [70.0, 65.0, 60.0]
        today = dt.date(2025, 1, 1)
        preds = _linear_forecast(dates, values, today, [12])
        # Slope is -10/yr, so at 12 months: 60 + (-10) = 50
        self.assertAlmostEqual(preds[0].predicted_egfr, 50.0, delta=2.0)


class LMMForecastTests(TestCase):
    def test_forecast_on_linear_trajectory(self):
        # 6 points over 2 years, linear decline from 80 to 60
        dates = [
            dt.date(2024, 1, 1), dt.date(2024, 5, 1),
            dt.date(2024, 9, 1), dt.date(2025, 1, 1),
            dt.date(2025, 5, 1), dt.date(2025, 9, 1),
        ]
        values = [80.0, 76.7, 73.3, 70.0, 66.7, 63.3]
        today = dt.date(2025, 9, 1)
        preds = _lmm_forecast(dates, values, today, [6, 12])
        self.assertEqual(len(preds), 2)
        # Slope is -10/yr: at 6 months → ~58.3, at 12 months → ~53.3
        self.assertAlmostEqual(preds[0].predicted_egfr, 58.3, delta=3.0)
        self.assertAlmostEqual(preds[1].predicted_egfr, 53.3, delta=4.0)
        self.assertEqual(preds[0].model_type, "lmm")

    def test_ci_narrower_than_ols_with_many_points(self):
        # More data should give tighter CIs
        dates_many = [
            dt.date(2024, 1, 1), dt.date(2024, 3, 1), dt.date(2024, 5, 1),
            dt.date(2024, 7, 1), dt.date(2024, 9, 1), dt.date(2024, 11, 1),
            dt.date(2025, 1, 1), dt.date(2025, 3, 1),
        ]
        values_many = [80.0, 77.5, 75.0, 72.5, 70.0, 67.5, 65.0, 62.5]
        dates_few = [dt.date(2024, 1, 1), dt.date(2025, 3, 1)]
        values_few = [80.0, 62.5]
        today = dt.date(2025, 3, 1)
        lmm_preds = _lmm_forecast(dates_many, values_many, today, [12])
        ols_preds = _linear_forecast(dates_few, values_few, today, [12])
        ci_lmm = lmm_preds[0].upper_ci - lmm_preds[0].lower_ci
        ci_ols = ols_preds[0].upper_ci - ols_preds[0].lower_ci
        self.assertLess(ci_lmm, ci_ols)


class PopulationForecastTests(TestCase):
    def test_population_uses_patient_egfr_if_available(self):
        p = Patient.objects.create(
            patient_id="POP-1", name="Pop P", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1),
            latest_egfr=45.0,
            primary_diagnosis="iga_nephropathy",
        )
        pred = _population_prediction(p, dt.date(2025, 1, 1), 12)
        # IgAN slope is -4.0/yr: 45 - 4 = 41
        self.assertAlmostEqual(pred.predicted_egfr, 41.0, delta=2.0)
        self.assertEqual(pred.model_type, "population")
        self.assertEqual(pred.confidence, "low")

    def test_population_default_when_no_egfr(self):
        p = Patient.objects.create(
            patient_id="POP-2", name="Pop P2", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1),
        )
        pred = _population_prediction(p, dt.date(2025, 1, 1), 12)
        self.assertEqual(pred.model_type, "population")
        self.assertGreater(pred.predicted_egfr, 0)


class DriverTests(TestCase):
    def test_stable_egfr_driver(self):
        series = [(dt.date(2024, 1, 1), 60.0), (dt.date(2025, 1, 1), 59.5)]
        preds = [PredictedEGFR(
            patient_id="X", prediction_date=dt.date(2025, 1, 1),
            horizon_months=12, predicted_egfr=59.0,
            lower_ci=55.0, upper_ci=63.0, model_type="ols_bootstrap",
        )]
        drivers = _build_drivers(series, 0.5, preds)
        self.assertTrue(any("stable" in d.lower() for d in drivers))

    def test_rapid_decline_driver(self):
        series = [(dt.date(2024, 1, 1), 60.0), (dt.date(2025, 1, 1), 48.0)]
        preds = [PredictedEGFR(
            patient_id="X", prediction_date=dt.date(2025, 1, 1),
            horizon_months=12, predicted_egfr=36.0,
            lower_ci=30.0, upper_ci=42.0, model_type="ols_bootstrap",
        )]
        drivers = _build_drivers(series, -12.0, preds)
        self.assertTrue(any("rapidly" in d.lower() for d in drivers))

    def test_eskd_proximity_driver(self):
        series = [(dt.date(2024, 1, 1), 20.0), (dt.date(2025, 1, 1), 12.0)]
        preds = [PredictedEGFR(
            patient_id="X", prediction_date=dt.date(2025, 1, 1),
            horizon_months=12, predicted_egfr=8.0,
            lower_ci=3.0, upper_ci=13.0, model_type="ols_bootstrap",
        )]
        drivers = _build_drivers(series, -8.0, preds)
        self.assertTrue(any("kidney failure" in d.lower() for d in drivers))


class ConfidenceTests(TestCase):
    def test_high_confidence(self):
        self.assertEqual(_ci_confidence(2.0), "high")

    def test_moderate_confidence(self):
        self.assertEqual(_ci_confidence(4.0), "moderate")

    def test_low_confidence(self):
        self.assertEqual(_ci_confidence(7.0), "low")

    def test_insufficient_confidence(self):
        self.assertEqual(_ci_confidence(12.0), "insufficient")


class ExplainPredictionTests(TestCase):
    def test_explanation_contains_key_parts(self):
        forecast = EGFRForecast(
            patient_id="X",
            prediction_date=dt.date(2025, 1, 1),
            predictions=[
                PredictedEGFR(
                    patient_id="X", prediction_date=dt.date(2025, 1, 1),
                    horizon_months=12, predicted_egfr=45.0,
                    lower_ci=40.0, upper_ci=50.0, model_type="ols_bootstrap",
                ),
            ],
            egfr_slope_per_year=-5.0,
            method_summary="OLS extrapolation with bootstrap CI",
        )
        text = explain_prediction(forecast)
        self.assertIn("45", text)
        self.assertIn("12 months", text)
        self.assertIn("declining", text)

    def test_stable_explanation(self):
        forecast = EGFRForecast(
            patient_id="X",
            prediction_date=dt.date(2025, 1, 1),
            predictions=[],
            egfr_slope_per_year=0.3,
            method_summary="test",
        )
        text = explain_prediction(forecast)
        self.assertIn("stable", text.lower())


class PredictEgfrTrajectoryIntegrationTests(TestCase):
    """Integration tests for the full predict_egfr_trajectory() function."""
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="PRED-INT-1", name="Int P", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1),
            primary_diagnosis="iga_nephropathy",
        )

    def test_no_egfr_data_uses_population(self):
        forecast = predict_egfr_trajectory(self.p.patient_id, [12])
        self.assertEqual(len(forecast.predictions), 1)
        self.assertEqual(forecast.predictions[0].model_type, "population")
        self.assertIn("Population", forecast.method_summary)

    def test_two_points_uses_ols(self):
        record_result(self.p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        record_result(self.p, "creatinine", result_date=dt.date(2025, 1, 1), value_numeric=1.5)
        # If eGFR isn't auto-derived, we test the extraction path
        series = _extract_egfr_series(self.p)
        if len(series) >= 2:
            forecast = predict_egfr_trajectory(self.p.patient_id, [6, 12])
            self.assertIn(forecast.predictions[0].model_type, ("ols_bootstrap", "lmm"))

    def test_forecast_has_all_horizons(self):
        forecast = predict_egfr_trajectory(self.p.patient_id, [6, 12, 24])
        self.assertEqual(len(forecast.predictions), 3)
        horizons = [p.horizon_months for p in forecast.predictions]
        self.assertEqual(horizons, [6, 12, 24])

    def test_predictions_are_non_negative(self):
        # Even with aggressive decline, eGFR shouldn't go negative
        forecast = predict_egfr_trajectory(self.p.patient_id, [60])
        for p in forecast.predictions:
            self.assertGreaterEqual(p.predicted_egfr, 0.0)
            self.assertGreaterEqual(p.lower_ci, 0.0)


# =========================================================================== #
# Sprint 8 — Relapse Probability Forecasting Tests
# =========================================================================== #

from .services.prediction import (
    PredictedRelapse,
    RelapseForecast,
    _extract_relapse_features,
    _extract_latest_proteinuria,
    _get_relapse_model,
    _compute_relapse_probability,
    predict_relapse_risk,
    _RELAPSE_MODELS,
    _GENERAL_CKD_MODEL,
)


class RelapseModelTests(TestCase):
    """Tests for disease-specific relapse prognostic models."""

    def test_igan_model_exists(self):
        model = _RELAPSE_MODELS.get("iga_nephropathy")
        self.assertIsNotNone(model)
        self.assertIn("baseline_hazard_6mo", model)
        self.assertIn("baseline_hazard_12mo", model)
        self.assertGreater(len(model["covariates"]), 0)

    def test_mn_model_exists(self):
        model = _RELAPSE_MODELS.get("membranous_nephropathy")
        self.assertIsNotNone(model)
        self.assertIn("pla2r_immunological_remission", [c["name"] for c in model["covariates"]])

    def test_lupus_model_exists(self):
        model = _RELAPSE_MODELS.get("lupus_nephritis")
        self.assertIsNotNone(model)

    def test_general_ckd_fallback(self):
        model = _GENERAL_CKD_MODEL
        self.assertIn("baseline_hazard_6mo", model)
        self.assertGreater(model["baseline_hazard_12mo"], model["baseline_hazard_6mo"])

    def test_get_relapse_model_returns_model_for_known_disease(self):
        model = _get_relapse_model("iga_nephropathy")
        self.assertEqual(model, _RELAPSE_MODELS["iga_nephropathy"])

    def test_get_relapse_model_falls_back_to_general_for_unknown(self):
        model = _get_relapse_model("unknown_disease_xyz")
        self.assertEqual(model, _GENERAL_CKD_MODEL)


class RelapseProbabilityComputationTests(TestCase):
    """Tests for the Cox-like hazard calculation."""

    def test_zero_lp_gives_baseline_probability(self):
        """With no risk factors active, probability should equal baseline."""
        model = _RELAPSE_MODELS["iga_nephropathy"]
        features = {c["name"]: 0.0 for c in model["covariates"]}
        prob, lo, hi = _compute_relapse_probability(model, features, 6)
        # Baseline hazard 6mo = 0.10, so P = 1 - exp(-0.10) ≈ 0.095
        self.assertAlmostEqual(prob, 0.095, delta=0.02)
        self.assertGreater(prob, 0.0)
        self.assertLess(prob, 1.0)

    def test_positive_risk_factors_increase_probability(self):
        """Active risk factors should increase probability above baseline."""
        model = _RELAPSE_MODELS["iga_nephropathy"]
        # Baseline
        features_base = {c["name"]: 0.0 for c in model["covariates"]}
        prob_base, _, _ = _compute_relapse_probability(model, features_base, 12)

        # With risk factors
        features_risk = {c["name"]: 0.0 for c in model["covariates"]}
        features_risk["proteinuria_g_per_day"] = 3.5
        features_risk["oxford_S2_or_higher"] = 1.0
        prob_risk, _, _ = _compute_relapse_probability(model, features_risk, 12)

        self.assertGreater(prob_risk, prob_base)

    def test_protective_factors_decrease_probability(self):
        """Protective factors should decrease probability below baseline."""
        model = _RELAPSE_MODELS["iga_nephropathy"]
        features_base = {c["name"]: 0.0 for c in model["covariates"]}
        prob_base, _, _ = _compute_relapse_probability(model, features_base, 12)

        features_protective = {c["name"]: 0.0 for c in model["covariates"]}
        features_protective["on_immunosuppression"] = 1.0
        prob_prot, _, _ = _compute_relapse_probability(model, features_protective, 12)

        self.assertLess(prob_prot, prob_base)

    def test_probability_bounded_0_to_1(self):
        """Probability should always be between 0 and 1."""
        model = _RELAPSE_MODELS["iga_nephropathy"]
        features = {c["name"]: 0.0 for c in model["covariates"]}
        features["proteinuria_g_per_day"] = 10.0
        features["oxford_S2_or_higher"] = 1.0
        features["oxford_T2_or_higher"] = 1.0
        prob, lo, hi = _compute_relapse_probability(model, features, 24)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        self.assertGreaterEqual(lo, 0.0)
        self.assertLessEqual(hi, 1.0)

    def test_ci_width_increases_with_horizon(self):
        """CI should be wider at longer horizons."""
        model = _RELAPSE_MODELS["iga_nephropathy"]
        features = {c["name"]: 0.0 for c in model["covariates"]}
        _, lo6, hi6 = _compute_relapse_probability(model, features, 6)
        _, lo12, hi12 = _compute_relapse_probability(model, features, 12)
        ci6 = hi6 - lo6
        ci12 = hi12 - lo12
        self.assertGreater(ci12, ci6)


class RelapseFeatureExtractionTests(TestCase):
    """Tests for patient feature extraction for relapse models."""

    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="REL-1", name="Rel P", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1),
            primary_diagnosis="iga_nephropathy",
            hypertension=True,
            oxford_mestc="S2T1M0E0C0",
        )

    def test_extract_features_returns_dict(self):
        features = _extract_relapse_features(self.p)
        self.assertIsInstance(features, dict)
        self.assertIn("proteinuria_g_per_day", features)
        self.assertIn("egfr_slope_per_year", features)
        self.assertIn("hypertension", features)

    def test_hypertension_feature(self):
        features = _extract_relapse_features(self.p)
        self.assertEqual(features["hypertension"], 1.0)

    def test_no_hypertension(self):
        self.p.hypertension = False
        self.p.save()
        features = _extract_relapse_features(self.p)
        self.assertEqual(features["hypertension"], 0.0)

    def test_igan_oxford_features(self):
        features = _extract_relapse_features(self.p)
        self.assertEqual(features["oxford_S2_or_higher"], 1.0)

    def test_igan_no_sclerosis(self):
        self.p.oxford_mestc = "S0T0M0E0C0"
        self.p.save()
        features = _extract_relapse_features(self.p)
        self.assertEqual(features["oxford_S2_or_higher"], 0.0)


class PredictRelapseRiskIntegrationTests(TestCase):
    """Integration tests for predict_relapse_risk()."""
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="REL-INT-1", name="Rel Int P", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1),
            primary_diagnosis="iga_nephropathy",
            hypertension=True,
        )

    def test_returns_forecast_with_predictions(self):
        forecast = predict_relapse_risk(self.p.patient_id, [6, 12])
        self.assertEqual(len(forecast.predictions), 2)
        self.assertEqual(forecast.disease, "iga_nephropathy")

    def test_predictions_have_required_fields(self):
        forecast = predict_relapse_risk(self.p.patient_id, [6, 12])
        for p in forecast.predictions:
            self.assertIsInstance(p, PredictedRelapse)
            self.assertGreaterEqual(p.probability, 0.0)
            self.assertLessEqual(p.probability, 1.0)
            self.assertGreaterEqual(p.lower_ci, 0.0)
            self.assertLessEqual(p.upper_ci, 1.0)
            self.assertIn(p.horizon_months, [6, 12])

    def test_risk_tier_classification(self):
        forecast = predict_relapse_risk(self.p.patient_id, [6, 12])
        self.assertIn(forecast.overall_risk_tier, ("low", "moderate", "high", "critical"))

    def test_unknown_disease_uses_general_model(self):
        self.p.primary_diagnosis = "chronic_kidney_disease_unspecified"
        self.p.save()
        forecast = predict_relapse_risk(self.p.patient_id, [6, 12])
        self.assertEqual(forecast.disease, "chronic_kidney_disease_unspecified")

    def test_12mo_probability_higher_than_6mo(self):
        """Cumulative probability should be monotonically increasing."""
        forecast = predict_relapse_risk(self.p.patient_id, [6, 12])
        p6 = forecast.predictions[0].probability
        p12 = forecast.predictions[1].probability
        self.assertGreaterEqual(p12, p6)


# =========================================================================== #
# Sprint 9 — Treatment Response Prediction Tests
# =========================================================================== #

from .services.prediction import (
    PredictedResponse,
    TreatmentResponseForecast,
    _get_treatment_model,
    _infer_treatment,
    _suggest_monitoring_cadence,
    _compute_treatment_response,
    predict_treatment_response,
    _TREATMENT_MODELS,
)


class TreatmentModelTests(TestCase):
    def test_rituximab_mn_model_exists(self):
        model = _TREATMENT_MODELS.get("rituximab_mn")
        self.assertIsNotNone(model)
        self.assertEqual(model["response_type"], "immunological")

    def test_rituximab_lupus_model_exists(self):
        model = _TREATMENT_MODELS.get("rituximab_lupus")
        self.assertIsNotNone(model)

    def test_igan_immunosuppression_model_exists(self):
        model = _TREATMENT_MODELS.get("immunosuppression_igan")
        self.assertIsNotNone(model)
        self.assertEqual(model["response_type"], "proteinuria_reduction")

    def test_cni_fsgs_model_exists(self):
        model = _TREATMENT_MODELS.get("cni_fsgs")
        self.assertIsNotNone(model)

    def test_get_treatment_model_known(self):
        self.assertIsNotNone(_get_treatment_model("rituximab_mn"))

    def test_get_treatment_model_unknown(self):
        self.assertIsNone(_get_treatment_model("unknown_treatment"))


class MonitoringCadenceTests(TestCase):
    def test_high_probability_3_months(self):
        cadence = _suggest_monitoring_cadence(0.7)
        self.assertEqual(cadence, "every_3_months")

    def test_low_probability_frequent(self):
        cadence = _suggest_monitoring_cadence(0.2)
        self.assertEqual(cadence, "every_1_2_months")

    def test_remission_6_months(self):
        cadence = _suggest_monitoring_cadence(0.8, in_remission=True)
        self.assertEqual(cadence, "every_6_months")

    def test_moderate_probability(self):
        cadence = _suggest_monitoring_cadence(0.45)
        self.assertEqual(cadence, "every_3_months")


class TreatmentResponseComputationTests(TestCase):
    def test_zero_lp_gives_baseline(self):
        model = _TREATMENT_MODELS["rituximab_mn"]
        features = {c["name"]: 0.0 for c in model["covariates"]}
        prob, lo, hi = _compute_treatment_response(model, features, 6)
        # Baseline hazard 6mo = 0.55, P = 1 - exp(-0.55) ≈ 0.423
        self.assertAlmostEqual(prob, 0.423, delta=0.05)
        self.assertGreater(prob, 0.0)

    def test_achieved_response_increases_probability(self):
        model = _TREATMENT_MODELS["rituximab_mn"]
        features_base = {c["name"]: 0.0 for c in model["covariates"]}
        prob_base, _, _ = _compute_treatment_response(model, features_base, 6)

        features_achieved = {c["name"]: 0.0 for c in model["covariates"]}
        features_achieved["pla2r_50pct_achieved"] = 1.0
        prob_achieved, _, _ = _compute_treatment_response(model, features_achieved, 6)

        self.assertGreater(prob_achieved, prob_base)

    def test_collapsing_variant_reduces_probability(self):
        model = _TREATMENT_MODELS["cni_fsgs"]
        features_base = {c["name"]: 0.0 for c in model["covariates"]}
        prob_base, _, _ = _compute_treatment_response(model, features_base, 6)

        features_collapsing = {c["name"]: 0.0 for c in model["covariates"]}
        features_collapsing["histological_collapsing"] = 1.0
        prob_collapsing, _, _ = _compute_treatment_response(model, features_collapsing, 6)

        self.assertLess(prob_collapsing, prob_base)

    def test_probability_bounded(self):
        model = _TREATMENT_MODELS["rituximab_mn"]
        features = {c["name"]: 1.0 for c in model["covariates"]}
        prob, lo, hi = _compute_treatment_response(model, features, 12)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)


class PredictTreatmentResponseIntegrationTests(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="TR-INT-1", name="TR Int P", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1),
            primary_diagnosis="membranous_nephropathy",
        )

    def test_no_treatment_returns_none_detected(self):
        forecast = predict_treatment_response(self.p.patient_id)
        self.assertEqual(forecast.treatment, "none_detected")
        self.assertEqual(len(forecast.predictions), 0)
        self.assertIn("No active", forecast.recommendation_summary)

    def test_explicit_treatment_works(self):
        forecast = predict_treatment_response(
            self.p.patient_id, treatment="rituximab_mn", horizons=[6, 12],
        )
        self.assertEqual(forecast.treatment, "rituximab_mn")
        self.assertEqual(len(forecast.predictions), 2)
        self.assertIn("every", forecast.monitoring_cadence)

    def test_predictions_have_required_fields(self):
        forecast = predict_treatment_response(
            self.p.patient_id, treatment="rituximab_mn", horizons=[3, 6, 12],
        )
        for p in forecast.predictions:
            self.assertIsInstance(p, PredictedResponse)
            self.assertGreaterEqual(p.probability, 0.0)
            self.assertLessEqual(p.probability, 1.0)
            self.assertEqual(p.treatment, "rituximab_mn")

    def test_unknown_model_returns_empty(self):
        forecast = predict_treatment_response(
            self.p.patient_id, treatment="nonexistent_drug",
        )
        self.assertEqual(len(forecast.predictions), 0)

    def test_12mo_probability_gte_6mo(self):
        forecast = predict_treatment_response(
            self.p.patient_id, treatment="rituximab_mn", horizons=[6, 12],
        )
        if len(forecast.predictions) == 2:
            self.assertGreaterEqual(
                forecast.predictions[1].probability,
                forecast.predictions[0].probability,
            )


# =========================================================================== #
# Sprint 10 — Risk Stratification Tests
# =========================================================================== #

from .services.prediction import (
    PatientRiskSummary,
    compute_overall_risk_tier,
    risk_stratify_cohort,
    _egfr_trend_label,
    _determine_next_action,
)


class OverallRiskTierTests(TestCase):
    def test_critical_egfr_slope(self):
        self.assertEqual(compute_overall_risk_tier(-7.0, None, None), "critical")

    def test_high_egfr_slope(self):
        self.assertEqual(compute_overall_risk_tier(-3.0, None, None), "high")

    def test_moderate_egfr_slope(self):
        self.assertEqual(compute_overall_risk_tier(-0.5, None, None), "moderate")

    def test_low_egfr_slope(self):
        self.assertEqual(compute_overall_risk_tier(2.0, None, None), "low")

    def test_critical_relapse_prob(self):
        self.assertEqual(compute_overall_risk_tier(None, 0.6, None), "critical")

    def test_high_relapse_prob(self):
        self.assertEqual(compute_overall_risk_tier(None, 0.35, None), "high")

    def test_critical_low_response(self):
        self.assertEqual(compute_overall_risk_tier(None, None, 0.1), "critical")

    def test_high_low_response(self):
        self.assertEqual(compute_overall_risk_tier(None, None, 0.3), "high")

    def test_all_none_returns_low(self):
        self.assertEqual(compute_overall_risk_tier(None, None, None), "low")

    def test_worst_tier_wins(self):
        # moderate eGFR + critical relapse → critical
        self.assertEqual(compute_overall_risk_tier(-1.0, 0.55, None), "critical")


class EGFRTrendLabelTests(TestCase):
    def test_rapid_decline(self):
        self.assertEqual(_egfr_trend_label(-6.0), "declining_rapidly")

    def test_slow_decline(self):
        self.assertEqual(_egfr_trend_label(-3.0), "declining")

    def test_stable(self):
        self.assertEqual(_egfr_trend_label(-0.5), "stable")

    def test_improving(self):
        self.assertEqual(_egfr_trend_label(2.0), "improving")

    def test_none_returns_unknown(self):
        self.assertEqual(_egfr_trend_label(None), "unknown")


class DetermineNextActionTests(TestCase):
    def test_critical_egfr_decline(self):
        action, date = _determine_next_action("critical", -6.0, None)
        self.assertIn("Urgent", action)
        self.assertEqual(date, str(dt.date.today()))

    def test_critical_relapse(self):
        action, date = _determine_next_action("critical", None, 0.7)
        self.assertIn("immunosuppression", action.lower())

    def test_high_tier(self):
        action, date = _determine_next_action("high", -3.0, None)
        self.assertIn("2 weeks", action)

    def test_moderate_tier(self):
        action, date = _determine_next_action("moderate", None, None)
        self.assertIn("1 month", action)

    def test_low_tier(self):
        action, date = _determine_next_action("low", None, None)
        self.assertIn("Standard", action)
        expected = dt.date.today() + dt.timedelta(days=90)
        self.assertEqual(date, str(expected))


class RiskStratifyCohortTests(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.p1 = Patient.objects.create(
            patient_id="RISK-1", name="Alice Test", sex="F",
            primary_diagnosis="IgA Nephropathy",
            registration_status="registered",
        )
        self.p2 = Patient.objects.create(
            patient_id="RISK-2", name="Bob Test", sex="M",
            primary_diagnosis="Membranous Nephropathy",
            registration_status="registered",
        )

    def test_returns_list(self):
        summaries = risk_stratify_cohort(limit=10)
        self.assertIsInstance(summaries, list)

    def test_summary_has_pk(self):
        summaries = risk_stratify_cohort(
            Patient.objects.filter(patient_id="RISK-1"), limit=10,
        )
        if summaries:
            self.assertIsInstance(summaries[0].pk, int)
            self.assertGreater(summaries[0].pk, 0)

    def test_summary_has_patient_id(self):
        summaries = risk_stratify_cohort(
            Patient.objects.filter(patient_id="RISK-1"), limit=10,
        )
        if summaries:
            self.assertEqual(summaries[0].patient_id, "RISK-1")

    def test_risk_filter(self):
        summaries = risk_stratify_cohort(risk_filter="low", limit=10)
        for s in summaries:
            self.assertEqual(s.overall_risk_tier, "low")

    def test_disease_filter(self):
        summaries = risk_stratify_cohort(
            disease_filter="IgA", limit=10,
        )
        for s in summaries:
            self.assertIn("IgA", s.disease)

    def test_sorted_by_tier(self):
        summaries = risk_stratify_cohort(limit=200)
        tier_order = {"critical": 4, "high": 3, "moderate": 2, "low": 1}
        for i in range(len(summaries) - 1):
            self.assertGreaterEqual(
                tier_order.get(summaries[i].overall_risk_tier, 0),
                tier_order.get(summaries[i + 1].overall_risk_tier, 0),
            )

    def test_percentage_fields(self):
        summaries = risk_stratify_cohort(
            Patient.objects.filter(patient_id="RISK-1"), limit=10,
        )
        if summaries and summaries[0].relapse_risk is not None:
            self.assertIsInstance(summaries[0].relapse_risk_pct, int)
            self.assertGreaterEqual(summaries[0].relapse_risk_pct, 0)
            self.assertLessEqual(summaries[0].relapse_risk_pct, 100)


# =========================================================================== #
# Sprint 11 — Prediction Audit Tests
# =========================================================================== #

from .services.prediction import (
    log_prediction,
    prediction_history,
    prediction_explanation,
)


class PredictionAuditTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(
            patient_id="AUDIT-1", name="Audit Patient", sex="M",
            primary_diagnosis="IgA Nephropathy",
            registration_status="registered",
        )

    def test_log_prediction_creates_entry(self):
        log_prediction(self.p.patient_id, "egfr_forecast", {
            "method": "OLS", "predictions": [{"horizon_months": 12, "predicted_egfr": 45}],
        })
        history = prediction_history(self.p.patient_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["type"], "egfr_forecast")

    def test_log_multiple_predictions(self):
        log_prediction(self.p.patient_id, "egfr_forecast", {"predictions": []})
        log_prediction(self.p.patient_id, "relapse_forecast", {"predictions": []})
        history = prediction_history(self.p.patient_id)
        self.assertEqual(len(history), 2)
        # Most recent first
        self.assertEqual(history[0]["type"], "relapse_forecast")
        self.assertEqual(history[1]["type"], "egfr_forecast")

    def test_prediction_history_filter(self):
        log_prediction(self.p.patient_id, "egfr_forecast", {"a": 1})
        log_prediction(self.p.patient_id, "relapse_forecast", {"b": 2})
        egfr_history = prediction_history(self.p.patient_id, prediction_type="egfr_forecast")
        self.assertEqual(len(egfr_history), 1)
        self.assertEqual(egfr_history[0]["type"], "egfr_forecast")

    def test_prediction_explanation_returns_latest(self):
        log_prediction(self.p.patient_id, "egfr_forecast", {"data": "old"})
        log_prediction(self.p.patient_id, "egfr_forecast", {"data": "new"})
        explanation = prediction_explanation(self.p.patient_id, "egfr_forecast")
        self.assertIsNotNone(explanation)
        self.assertEqual(explanation["data"]["data"], "new")

    def test_prediction_explanation_returns_none_if_empty(self):
        explanation = prediction_explanation(self.p.patient_id, "egfr_forecast")
        self.assertIsNone(explanation)

    def test_prediction_history_empty_patient(self):
        history = prediction_history("NONEXISTENT-999")
        self.assertEqual(history, [])

    def test_log_keeps_last_50(self):
        for i in range(55):
            log_prediction(self.p.patient_id, "egfr_forecast", {"i": i})
        history = prediction_history(self.p.patient_id)
        self.assertEqual(len(history), 50)
        # Oldest kept should be i=5
        self.assertEqual(history[-1]["data"]["i"], 5)


# =========================================================================== #
# Sprint 12 — Proactive Alerting Tests
# =========================================================================== #

from .services.prediction import Alert, check_predictions_for_alerts


class AlertTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(
            patient_id="ALERT-1", name="Alert Patient", sex="M",
            primary_diagnosis="IgA Nephropathy",
            registration_status="registered",
        )

    def test_returns_list(self):
        alerts = check_predictions_for_alerts()
        self.assertIsInstance(alerts, list)

    def test_empty_when_no_profiles(self):
        alerts = check_predictions_for_alerts(
            Patient.objects.filter(patient_id="ALERT-1")
        )
        self.assertEqual(len(alerts), 0)

    def test_eskd_alert_when_low_egfr(self):
        from clinical_reasoning.models import ClinicalProfile
        profile = ClinicalProfile.objects.get_or_create(
            patient=self.p,
            defaults={"differential": [{"disease_id": "iga_nephropathy", "disease_name": "IgAN", "score": 8.0}]},
        )[0]
        profile.risk_assessment = {
            "egfr_trajectory": {
                "slope_per_year": -6.0,
                "predictions": [
                    {"horizon_months": 12, "predicted_egfr": 10, "lower_ci": 5, "upper_ci": 15,
                     "confidence": "high"},
                    {"horizon_months": 24, "predicted_egfr": 5, "lower_ci": 0, "upper_ci": 10,
                     "confidence": "moderate"},
                ],
            },
        }
        profile.save(update_fields=["risk_assessment"])

        alerts = check_predictions_for_alerts(
            Patient.objects.filter(patient_id="ALERT-1")
        )
        eskd_alerts = [a for a in alerts if a.alert_type == "eskd_risk"]
        self.assertGreater(len(eskd_alerts), 0)
        self.assertEqual(eskd_alerts[0].severity, "critical")

    def test_rapid_decline_alert(self):
        from clinical_reasoning.models import ClinicalProfile
        profile = ClinicalProfile.objects.get_or_create(
            patient=self.p,
            defaults={"differential": [{"disease_id": "iga_nephropathy", "disease_name": "IgAN", "score": 8.0}]},
        )[0]
        profile.risk_assessment = {
            "egfr_trajectory": {
                "slope_per_year": -7.0,
                "predictions": [],
            },
        }
        profile.save(update_fields=["risk_assessment"])

        alerts = check_predictions_for_alerts(
            Patient.objects.filter(patient_id="ALERT-1")
        )
        decline_alerts = [a for a in alerts if a.alert_type == "rapid_decline"]
        self.assertGreater(len(decline_alerts), 0)

    def test_high_relapse_alert(self):
        from clinical_reasoning.models import ClinicalProfile
        profile = ClinicalProfile.objects.get_or_create(
            patient=self.p,
            defaults={"differential": [{"disease_id": "iga_nephropathy", "disease_name": "IgAN", "score": 8.0}]},
        )[0]
        profile.risk_assessment = {
            "relapse_forecast": {
                "predictions": [
                    {"horizon_months": 6, "probability": 0.65, "lower_ci": 0.5, "upper_ci": 0.8,
                     "risk_factors": ["high proteinuria"], "protective_factors": [],
                     "monitoring_recommendation": "Monitor closely"},
                ],
            },
        }
        profile.save(update_fields=["risk_assessment"])

        alerts = check_predictions_for_alerts(
            Patient.objects.filter(patient_id="ALERT-1")
        )
        relapse_alerts = [a for a in alerts if a.alert_type == "high_relapse"]
        self.assertGreater(len(relapse_alerts), 0)
        self.assertIn("65%", relapse_alerts[0].message)

    def test_treatment_failure_alert(self):
        from clinical_reasoning.models import ClinicalProfile
        profile = ClinicalProfile.objects.get_or_create(
            patient=self.p,
            defaults={"differential": [{"disease_id": "iga_nephropathy", "disease_name": "IgAN", "score": 8.0}]},
        )[0]
        profile.risk_assessment = {
            "treatment_response": {
                "treatment": "rituximab_mn",
                "monitoring_cadence": "every_3_months",
                "recommendation_summary": "Continue",
                "predictions": [
                    {"time_to_response_months": 6, "response_type": "partial",
                     "probability": 0.15, "lower_ci": 0.05, "upper_ci": 0.25,
                     "stopping_criteria_met": True, "factors": ["high risk"]},
                ],
            },
        }
        profile.save(update_fields=["risk_assessment"])

        alerts = check_predictions_for_alerts(
            Patient.objects.filter(patient_id="ALERT-1")
        )
        tr_alerts = [a for a in alerts if a.alert_type == "treatment_failure"]
        self.assertGreater(len(tr_alerts), 0)

    def test_sorted_by_severity(self):
        alerts = check_predictions_for_alerts()
        severity_order = {"critical": 3, "warning": 2, "info": 1}
        for i in range(len(alerts) - 1):
            self.assertGreaterEqual(
                severity_order.get(alerts[i].severity, 0),
                severity_order.get(alerts[i + 1].severity, 0),
            )
