from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    DrugInteractionCheckSerializer,
    DrugContraindicationCheckSerializer,
    MultiDrugContraindicationCheckSerializer,
)
from .interactions import (
    check_interactions,
    get_interaction_summary,
    INTERACTION_DB,
)
from .contraindications import (
    check_contraindications,
    get_contraindication_summary,
    check_all_contraindications,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def drug_interactions_check(request):
    """Check for drug-drug interactions.

    GET: Returns the interaction database summary (for reference).
    POST: Check a list of drugs for interactions.
    """
    if request.method == "GET":
        drug_set = sorted(set(
            i["drug_a"] for i in INTERACTION_DB
        ))
        return Response({
            "available_drugs": drug_set,
            "total_interactions": len(INTERACTION_DB),
            "endpoint": "POST /api/v1/drug-interactions/check/",
            "payload_example": {
                "drugs": ["tacrolimus", "fluconazole"],
                "patient_context": {"egfr": 45},
            },
        })

    serializer = DrugInteractionCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data

    results = check_interactions(d["drugs"], d.get("patient_context", {}))
    summary = get_interaction_summary(results)

    return Response(summary)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def drug_contraindications_check(request):
    """Check for drug-disease contraindications.

    GET: Returns reference info about the contraindication database.
    POST: Check a drug against patient's disease profile.
    """
    if request.method == "GET":
        drugs = sorted(set(
            i["drug"] for i in __import__(
                "treatments.contraindications", fromlist=["CONTRANDICATION_DB"]
            ).CONTRANDICATION_DB
        ))
        return Response({
            "available_drugs": drugs,
            "total_contraindications": len(__import__(
                "treatments.contraindications", fromlist=["CONTRANDICATION_DB"]
            ).CONTRANDICATION_DB),
            "endpoint": "POST /api/v1/drug-contraindications/check/",
            "payload_example": {
                "drug": "cyclophosphamide",
                "patient_diseases": ["pregnancy"],
            },
        })

    single = request.data.get("drug") and not request.data.get("drugs")
    if single:
        serializer = DrugContraindicationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        results = check_contraindications(
            d["drug"],
            d["patient_diseases"],
            d.get("patient_context", {}),
        )
        summary = get_contraindication_summary(results)
        return Response(summary)

    serializer = MultiDrugContraindicationCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data
    result = check_all_contraindications(
        d["drugs"],
        d["patient_diseases"],
        d.get("patient_context", {}),
    )
    return Response(result)
