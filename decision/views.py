from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.base import AuditedModelViewSet

from .models import DecisionRequest, DecisionResult
from .serializers import (
    DecisionRequestSerializer, DecisionResultSerializer,
    OverrideDecisionSerializer, EGFRCalculatorSerializer,
    BSACalculatorSerializer, ProteinuriaConverterSerializer,
    RenalDoseSerializer, KDIGOHeatmapSerializer,
)
from .services import (
    evaluate_case, egfr_ckd_epi_2021, bsa_mosteller,
    upcr_to_24h_utp, utp_to_upcr, proteinuria_category,
    renal_dose_adjustment, kdigo_heatmap_point,
)
from .explainability import build_explainability, build_traceability_entry


class DecisionViewSet(AuditedModelViewSet):
    """DEPRECATED: Legacy differential diagnosis engine (9 diseases).

    Use ClinicalProfileViewSet.reason() (clinical_reasoning app) instead
    which uses the KnowledgeBase-driven engine (18 diseases).
    Kept for backward compatibility during pilot transition.
    """
    queryset = DecisionRequest.objects.all()
    serializer_class = DecisionRequestSerializer

    def create(self, request):
        serializer = DecisionRequestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        decision_request = serializer.save()

        patient_data = decision_request.input_snapshot
        result_data = evaluate_case(patient_data)

        # Build rich explainability trace
        traceability = build_traceability_entry(patient_data)
        explanation_data = build_explainability(patient_data)

        result = DecisionResult.objects.create(
            request=decision_request,
            phenotype=result_data["phenotype"],
            urgency_level=result_data["urgency"]["level"],
            urgency_tone=result_data["urgency"]["tone"],
            urgency_reasons=result_data["urgency"]["reasons"],
            ranked_differential=result_data["ranked"],
            next_steps=result_data["steps"],
            traceability=traceability,
            explanation=explanation_data["reasoning_summary"],
        )

        return Response(DecisionResultSerializer(result).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def evaluate(self, request):
        data = request.data
        result_data = evaluate_case(data)

        encounter_id = data.get("encounter_id")
        if encounter_id:
            from encounters.models import ClinicalEncounter
            try:
                enc = ClinicalEncounter.objects.get(id=encounter_id)
                req = DecisionRequest.objects.create(
                    patient=enc.patient, encounter=enc,
                    input_snapshot=data,
                )
                traceability = build_traceability_entry(data)
                explanation_data = build_explainability(data)
                DecisionResult.objects.create(
                    request=req,
                    phenotype=result_data["phenotype"],
                    urgency_level=result_data["urgency"]["level"],
                    urgency_tone=result_data["urgency"]["tone"],
                    urgency_reasons=result_data["urgency"]["reasons"],
                    ranked_differential=result_data["ranked"],
                    next_steps=result_data["steps"],
                    traceability=traceability,
                    explanation=explanation_data["reasoning_summary"],
                )
            except Exception:
                pass

        # Attach explainability data to response
        result_data["explainability"] = build_explainability(data)

        resp = Response(result_data)
        resp["HX-Refresh"] = "true"
        return resp

    @action(detail=False, methods=["get", "post"], url_path="calculators")
    def calculators(self, request):
        """Clinical calculators endpoint.

        GET: returns available calculator types.
        POST: performs a calculation.
        """
        if request.method == "GET":
            return Response({
                "calculators": {
                    "egfr": "CKD-EPI 2021 eGFR calculator",
                    "bsa": "Mosteller body surface area",
                    "upcr_to_utp": "UPCR to estimated 24h urine protein",
                    "utp_to_upcr": "24h urine protein to estimated UPCR",
                    "proteinuria_category": "Classify proteinuria by UPCR",
                    "renal_dose": "Renal dose adjustment lookup",
                    "kdigo_heatmap": "KDIGO heat-map risk classification",
                }
            })

        calc = request.data.get("calculator")

        if calc == "egfr":
            s = EGFRCalculatorSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            d = s.validated_data
            egfr = egfr_ckd_epi_2021(d["creatinine_mg_dl"], d["age"], d["sex"], d.get("race", "other"))
            return Response({"egfr": egfr, "unit": "mL/min/1.73m²", "formula": "CKD-EPI 2021"})

        if calc == "bsa":
            s = BSACalculatorSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            d = s.validated_data
            bsa = bsa_mosteller(d["height_cm"], d["weight_kg"])
            return Response({"bsa": bsa, "unit": "m²", "formula": "Mosteller"})

        if calc in ("upcr_to_utp", "utp_to_upcr"):
            s = ProteinuriaConverterSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            d = s.validated_data
            if d["direction"] == "upcr_to_utp":
                result = upcr_to_24h_utp(d["value"], d["weight_kg"])
                return Response({"result": result, "unit": "g/day", "input": f"{d['value']} g/g UPCR"})
            else:
                result = utp_to_upcr(d["value"], d["weight_kg"])
                return Response({"result": result, "unit": "g/g", "input": f"{d['value']} g/day UTP"})

        if calc == "proteinuria_category":
            val = float(request.data.get("value", 0))
            cat = proteinuria_category(val)
            return Response({"upcr": val, "category": cat})

        if calc == "renal_dose":
            s = RenalDoseSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            d = s.validated_data
            result = renal_dose_adjustment(d["drug"], d["egfr"])
            return Response(result)

        if calc == "kdigo_heatmap":
            s = KDIGOHeatmapSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            d = s.validated_data
            result = kdigo_heatmap_point(d["egfr"], d["upcr"])
            return Response(result)

        return Response({"error": f"Unknown calculator: {calc}"}, status=status.HTTP_400_BAD_REQUEST)


class DecisionResultViewSet(AuditedModelViewSet):
    queryset = DecisionResult.objects.all()
    serializer_class = DecisionResultSerializer

    @action(detail=True, methods=["post"])
    def override(self, request, pk=None):
        """Override an AI decision with clinician reasoning."""
        result = self.get_object()
        serializer = OverrideDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        result.override_reason = d["override_reason"]
        result.alternative_diagnosis = d.get("alternative_diagnosis", "")
        result.clinician_notes = d.get("clinician_notes", "")
        result.overridden_by = request.user if request.user.is_authenticated else None
        result.override_at = timezone.now()
        result.save()

        return Response(DecisionResultSerializer(result).data)
