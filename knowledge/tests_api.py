"""
Tests for the clinical and knowledge REST API endpoints.
"""
import datetime as dt

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from patients.models import Patient
from patients.workflow import DiseasePhase, RegistrationStatus
from encounters.models import ClinicalEncounter
from encounters.services.workflow import register_patient
from clinical.models import ClinicalAssessment, VitalSign
from knowledge.models import GuidelineSource, KnowledgeBaseEntry


class RBACTestBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_roles")

    def _user(self, username, role=None):
        u = User.objects.create_user(username, password="x")
        if role:
            u.groups.add(Group.objects.get(name=role))
        return u

    def _auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")


# ---------------------------------------------------------------------------
# Clinical API Tests
# ---------------------------------------------------------------------------
class ClinicalAssessmentAPITests(RBACTestBase):

    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="BGD-TEST", name="Test", sex="M"
        )
        self.encounter = ClinicalEncounter.objects.create(
            patient=self.patient, encounter_date=dt.date.today()
        )

    def test_list_assessments(self):
        self._auth(self._user("ro", "readonly"))
        ClinicalAssessment.objects.create(
            encounter=self.encounter, chief_complaint="Frothy urine"
        )
        resp = self.client.get("/api/v1/clinical-assessments/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_create_assessment(self):
        self._auth(self._user("dm", "data_manager"))
        data = {
            "encounter": self.encounter.id,
            "chief_complaint": "Frothy urine for 2 weeks",
            "time_course": "subacute",
            "features": ["edema", "hypertension"],
        }
        resp = self.client.post("/api/v1/clinical-assessments/", data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["chief_complaint"], "Frothy urine for 2 weeks")

    def test_update_assessment(self):
        self._auth(self._user("dm", "data_manager"))
        a = ClinicalAssessment.objects.create(
            encounter=self.encounter, chief_complaint="Initial"
        )
        resp = self.client.patch(
            f"/api/v1/clinical-assessments/{a.id}/",
            {"chief_complaint": "Updated"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        a.refresh_from_db()
        self.assertEqual(a.chief_complaint, "Updated")

    def test_delete_assessment(self):
        self._auth(self._user("dm", "data_manager"))
        a = ClinicalAssessment.objects.create(encounter=self.encounter)
        resp = self.client.delete(f"/api/v1/clinical-assessments/{a.id}/")
        self.assertEqual(resp.status_code, 204)

    def test_readonly_cannot_write(self):
        self._auth(self._user("ro2", "readonly"))
        data = {"encounter": self.encounter.id}
        resp = self.client.post("/api/v1/clinical-assessments/", data, format="json")
        self.assertEqual(resp.status_code, 403)


class VitalSignAPITests(RBACTestBase):

    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="BGD-VS", name="Vital Test", sex="M"
        )
        self.encounter = ClinicalEncounter.objects.create(
            patient=self.patient, encounter_date=dt.date.today()
        )

    def test_list_vital_signs(self):
        self._auth(self._user("ro", "readonly"))
        VitalSign.objects.create(
            encounter=self.encounter, bp_systolic=120, bp_diastolic=80
        )
        resp = self.client.get("/api/v1/vital-signs/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_create_vital_sign(self):
        self._auth(self._user("dm", "data_manager"))
        data = {
            "encounter": self.encounter.id,
            "bp_systolic": 130,
            "bp_diastolic": 85,
            "heart_rate": 72,
            "weight_kg": 65.5,
        }
        resp = self.client.post("/api/v1/vital-signs/", data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["bp_systolic"], 130)

    def test_multiple_vitals_per_encounter(self):
        self._auth(self._user("dm", "data_manager"))
        data1 = {"encounter": self.encounter.id, "bp_systolic": 120, "bp_diastolic": 80}
        data2 = {"encounter": self.encounter.id, "bp_systolic": 130, "bp_diastolic": 85}
        self.client.post("/api/v1/vital-signs/", data1, format="json")
        self.client.post("/api/v1/vital-signs/", data2, format="json")
        resp = self.client.get("/api/v1/vital-signs/")
        self.assertEqual(resp.data["count"], 2)


# ---------------------------------------------------------------------------
# Knowledge API Tests
# ---------------------------------------------------------------------------
class GuidelineSourceAPITests(RBACTestBase):

    def test_list_sources(self):
        self._auth(self._user("ro", "readonly"))
        GuidelineSource.objects.create(
            title="KDIGO 2025", abbreviation="KDIGO",
            version_year=2025, effective_date=dt.date(2025, 1, 1),
        )
        resp = self.client.get("/api/v1/guideline-sources/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_create_source(self):
        self._auth(self._user("dm", "data_manager"))
        data = {
            "title": "KDIGO 2025",
            "abbreviation": "KDIGO",
            "version_year": 2025,
            "effective_date": "2025-01-01",
        }
        resp = self.client.post("/api/v1/guideline-sources/", data, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_readonly_cannot_write(self):
        self._auth(self._user("ro2", "readonly"))
        data = {"title": "Test", "abbreviation": "T", "version_year": 2024,
                "effective_date": "2024-01-01"}
        resp = self.client.post("/api/v1/guideline-sources/", data, format="json")
        self.assertEqual(resp.status_code, 403)


class KnowledgeBaseEntryAPITests(RBACTestBase):

    def setUp(self):
        self.source = GuidelineSource.objects.create(
            title="KDIGO 2025", abbreviation="KDIGO",
            version_year=2025, effective_date=dt.date(2025, 1, 1),
        )

    def test_list_entries(self):
        self._auth(self._user("ro", "readonly"))
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-IGA-001", disease_id="iga",
            rule_data={"conditions": [], "weight": 1, "explanation": "Test"},
            source=self.source, effective_date=dt.date(2025, 1, 1),
        )
        resp = self.client.get("/api/v1/knowledge-base/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_filter_by_disease(self):
        self._auth(self._user("ro", "readonly"))
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-IGA-001", disease_id="iga",
            rule_data={"conditions": [], "weight": 1, "explanation": "Test"},
            source=self.source, effective_date=dt.date(2025, 1, 1),
        )
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-MEM-001", disease_id="membranous",
            rule_data={"conditions": [], "weight": 1, "explanation": "Test"},
            source=self.source, effective_date=dt.date(2025, 1, 1),
        )
        resp = self.client.get("/api/v1/knowledge-base/by_disease/?disease_id=iga")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["disease_id"], "iga")

    def test_filter_by_disease_missing_param(self):
        self._auth(self._user("ro", "readonly"))
        resp = self.client.get("/api/v1/knowledge-base/by_disease/")
        self.assertEqual(resp.status_code, 400)

    def test_list_active_entries(self):
        self._auth(self._user("ro", "readonly"))
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-ACTIVE", disease_id="iga",
            rule_data={"conditions": [], "weight": 1, "explanation": "Active"},
            source=self.source, effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-DRAFT", disease_id="iga",
            rule_data={"conditions": [], "weight": 1, "explanation": "Draft"},
            source=self.source, effective_date=dt.date(2025, 1, 1),
            status="draft",
        )
        resp = self.client.get("/api/v1/knowledge-base/active/")
        self.assertEqual(resp.status_code, 200)
        # active action returns a list, not paginated
        self.assertEqual(len(resp.data), 1)

    def test_evaluate_rules_endpoint(self):
        self._auth(self._user("ro", "readonly"))
        # Create active rules
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-EVAL-001", disease_id="iga",
            rule_data={
                "conditions": [
                    {"field": "disease_phase", "operator": "eq", "value": "active"}
                ],
                "weight": 3,
                "explanation": "Active disease phase",
                "base_score": 1,
            },
            source=self.source, effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        # Create patient with active phase
        p = Patient.objects.create(
            patient_id="BGD-EVAL", name="Eval Patient", sex="M",
            current_phase=DiseasePhase.ACTIVE,
        )
        resp = self.client.post(
            "/api/v1/knowledge-base/evaluate/",
            {"patient_id": p.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("results", resp.data)
        self.assertIn("features", resp.data)
        self.assertEqual(resp.data["patient_id"], "BGD-EVAL")

    def test_evaluate_rules_nonexistent_patient(self):
        self._auth(self._user("ro", "readonly"))
        resp = self.client.post(
            "/api/v1/knowledge-base/evaluate/",
            {"patient_id": 99999},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_evaluate_rules_with_disease_filter(self):
        self._auth(self._user("ro", "readonly"))
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-FIL-IGA", disease_id="iga",
            rule_data={"conditions": [], "weight": 1, "explanation": "IGA", "base_score": 5},
            source=self.source, effective_date=dt.date(2025, 1, 1), status="active",
        )
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-FIL-MEM", disease_id="membranous",
            rule_data={"conditions": [], "weight": 1, "explanation": "MEM", "base_score": 5},
            source=self.source, effective_date=dt.date(2025, 1, 1), status="active",
        )
        p = Patient.objects.create(
            patient_id="BGD-FIL", name="Filter Test", sex="M",
        )
        resp = self.client.post(
            "/api/v1/knowledge-base/evaluate/",
            {"patient_id": p.id, "disease_id": "iga"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        disease_ids = [r["disease_id"] for r in resp.data["results"]]
        self.assertIn("iga", disease_ids)
        self.assertNotIn("membranous", disease_ids)

    def test_create_entry(self):
        self._auth(self._user("dm", "data_manager"))
        data = {
            "entry_id": "KB-NEW-001",
            "disease_id": "iga",
            "rule_data": {"conditions": [], "weight": 1, "explanation": "New"},
            "source": self.source.id,
            "effective_date": "2025-01-01",
        }
        resp = self.client.post("/api/v1/knowledge-base/", data, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_readonly_cannot_write(self):
        self._auth(self._user("ro2", "readonly"))
        data = {"entry_id": "KB-X", "disease_id": "iga",
                "rule_data": {}, "source": self.source.id,
                "effective_date": "2025-01-01"}
        resp = self.client.post("/api/v1/knowledge-base/", data, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_version_history_create_and_list(self):
        self._auth(self._user("dm3", "data_manager"))
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-VER-001", disease_id="iga",
            rule_data={"conditions": [{"field": "proteinuria", "operator": "gte", "value": 3.5}], "weight": 3},
            source=self.source, effective_date=dt.date(2025, 1, 1),
            guideline_chapter="KDIGO 2021 IgAN Chapter 3",
            guideline_paragraph="Section 3.1.2",
            guideline_quote="Proteinuria >1 g/day warrants treatment",
        )

        # Create version snapshot
        resp = self.client.post(
            f"/api/v1/knowledge-base/{entry.id}/versions/",
            {"change_summary": "Initial rule definition"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["version_number"], 1)
        self.assertEqual(resp.data["change_summary"], "Initial rule definition")
        self.assertEqual(resp.data["guideline_chapter"], "KDIGO 2021 IgAN Chapter 3")

        # List versions
        resp = self.client.get(f"/api/v1/knowledge-base/{entry.id}/versions/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_version_restore(self):
        self._auth(self._user("dm4", "data_manager"))
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-VER-002", disease_id="iga",
            rule_data={"conditions": [], "weight": 2},
            source=self.source, effective_date=dt.date(2025, 1, 1),
        )

        # Create v1
        self.client.post(
            f"/api/v1/knowledge-base/{entry.id}/versions/",
            {"change_summary": "v1"},
            format="json",
        )

        # Modify entry
        entry.rule_data = {"conditions": [], "weight": 5}
        entry.save()

        # Create v2
        resp = self.client.post(
            f"/api/v1/knowledge-base/{entry.id}/versions/",
            {"change_summary": "v2"},
            format="json",
        )
        v2_id = resp.data["id"]

        # Restore to v1 (should create auto-snapshot first)
        resp = self.client.post(
            f"/api/v1/knowledge-base/{entry.id}/restore_version/",
            {"version_id": resp.data["id"]},  # restoring to v2 (same as current)
            format="json",
        )
        self.assertEqual(resp.status_code, 200)

        # Should now have 3 versions (v1, v2, auto-snapshot)
        resp = self.client.get(f"/api/v1/knowledge-base/{entry.id}/versions/")
        self.assertEqual(len(resp.data), 3)

    def test_guideline_linkage_fields(self):
        self._auth(self._user("dm5", "data_manager"))
        data = {
            "entry_id": "KB-GL-001",
            "disease_id": "iga",
            "rule_data": {"conditions": [], "weight": 1},
            "source": self.source.id,
            "effective_date": "2025-01-01",
            "guideline_chapter": "KDIGO 2021 IgAN Chapter 3",
            "guideline_paragraph": "Section 3.1.2",
            "guideline_quote": "Treat proteinuria >1 g/day with supportive care",
            "evidence_url": "https://kdigo.org/guidelines/igA-nephropathy/",
        }
        resp = self.client.post("/api/v1/knowledge-base/", data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["guideline_chapter"], "KDIGO 2021 IgAN Chapter 3")
        self.assertEqual(resp.data["guideline_paragraph"], "Section 3.1.2")
        self.assertIn("Treat proteinuria", resp.data["guideline_quote"])


# ─── V4.2 Graph Reasoning API Tests ─────────────────────────────────────


class GraphReasoningAPITests(RBACTestBase):
    """Test the graph-enhanced reasoning API endpoints."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from knowledge.models import (
            Disease, Syndrome, PathologyEntity, LabEntity,
            DrugIntelligence, MonitoringProtocol, Complication,
        )
        cls.disease = Disease.objects.create(id="iga", name="IgA Nephropathy")
        cls.disease2 = Disease.objects.create(id="mcd", name="Minimal Change Disease")
        cls.syndrome = Syndrome.objects.create(id="nephrotic", name="Nephrotic Syndrome")
        cls.syndrome.associated_diseases.add(cls.disease, cls.disease2)
        cls.pathology = PathologyEntity.objects.create(id="mesangial", name="Mesangial IgA")
        cls.pathology.associated_diseases.add(cls.disease)
        cls.lab = LabEntity.objects.create(id="hematuria", name="Hematuria")
        cls.lab.associated_diseases.add(cls.disease)
        cls.drug = DrugIntelligence.objects.create(id="pred", name="Prednisolone")
        cls.drug.indications.add(cls.disease)
        cls.mon = MonitoringProtocol.objects.create(
            id="mon_pred", name="Prednisone Monitoring", drug=cls.drug)
        cls.mon.associated_diseases.add(cls.disease)
        cls.comp = Complication.objects.create(id="inf", name="Infection")
        cls.comp.associated_diseases.add(cls.disease)
        from knowledge.graph_service import populate_from_models
        populate_from_models()

    def setUp(self):
        self._auth(self._user("ro", "readonly"))

    def test_treatments_endpoint(self):
        resp = self.client.get("/api/v1/graph-reasoning/treatments/?disease_id=iga")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("treatments", resp.data)
        names = [t["drug_name"] for t in resp.data["treatments"]]
        self.assertIn("Prednisolone", names)

    def test_treatments_endpoint_missing_param(self):
        resp = self.client.get("/api/v1/graph-reasoning/treatments/")
        self.assertEqual(resp.status_code, 400)

    def test_monitoring_endpoint(self):
        resp = self.client.get("/api/v1/graph-reasoning/monitoring/?disease_id=iga")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("protocols", resp.data)
        labels = [p["label"] for p in resp.data["protocols"]]
        self.assertIn("Prednisone Monitoring", labels)

    def test_complications_endpoint(self):
        resp = self.client.get("/api/v1/graph-reasoning/complications/?disease_id=iga")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("complications", resp.data)
        names = [c["complication_name"] for c in resp.data["complications"]]
        self.assertIn("Infection", names)

    def test_syndrome_match_endpoint(self):
        features = {"features": ["hypertension"], "labs": [], "biopsy": [],
                     "proteinuria": "nephrotic", "egfrTrend": "normal"}
        resp = self.client.post(
            "/api/v1/graph-reasoning/syndrome_match/",
            {"features": features},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("matches", resp.data)
        self.assertGreater(len(resp.data["matches"]), 0)
        self.assertIn("Nephrotic", resp.data["matches"][0]["syndrome_name"])

    def test_syndrome_match_endpoint_missing(self):
        resp = self.client.post("/api/v1/graph-reasoning/syndrome_match/", {}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_graph_differential_endpoint(self):
        features = {"features": [], "labs": [], "biopsy": [],
                     "proteinuria": "nephrotic", "egfrTrend": "normal"}
        resp = self.client.post(
            "/api/v1/graph-reasoning/graph_differential/",
            {"features": features},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("differential", resp.data)
        self.assertGreater(len(resp.data["differential"]), 0)

    def test_enhanced_plan_endpoint(self):
        resp = self.client.get("/api/v1/graph-reasoning/enhanced_plan/?disease_id=iga")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("treatments", resp.data)
        self.assertIn("monitoring", resp.data)
        self.assertIn("complication_risks", resp.data)
