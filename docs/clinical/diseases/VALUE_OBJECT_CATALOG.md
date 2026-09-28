# Value Object Catalog

**Version:** 2.5  
**Pattern:** Immutable, comparable by value, no identity

---

## Clinical Value Objects

| Value Object | Attributes | Used By | Source |
|---|---|---|---|
| `PatientId` | prefix="BGD-", sequence number | Patient | `patients/models.py:59` |
| `Sex` | M, F, O | Patient | `patients/models.py:47` |
| `DiabetesStatus` | none, t1, t2, other | Patient | `patients/models.py:52` |
| `DiseasePhase` | suspected, active, relapse, remission, ckd, eskd, post_transplant, conservative | Patient, ClinicalProfile | `patients/workflow.py` |
| `RegistrationStatus` | suspected, confirmed, inactive | Patient | `patients/workflow.py` |
| `SiteCode` | short alphanumeric | Site | `patients/models.py:24` |
| `EncounterType` | (choices) | ClinicalEncounter | `encounters/` |
| `VitalSign` | bp_systolic, bp_diastolic, heart_rate, weight, height | ClinicalEncounter | `encounters/` |
| `LabValue` | value_numeric, value_text, unit | LabResult | `labs/models.py` |
| `ReferenceRange` | low, high, unit | LabResult | `labs/models.py` |
| `LabFlag` | normal, high, low, critical_high, critical_low | LabResult | `labs/models.py` |
| `HistologicalDiagnosis` | diagnosis text, classification | Biopsy | `pathology/models.py` |
| `GNPattern` | light_microscopy, immunofluorescence, electron_microscopy | Biopsy | `pathology/models.py` |
| `DrugDose` | amount, unit, frequency, route | TreatmentExposure | `treatments/models.py` |
| `TreatmentRegimen` | regimen_name, drugs, duration | TreatmentExposure | `treatments/models.py` |
| `DrugClass` | class name | DrugMaster | `treatments/models.py` |
| `RemissionStatus` | complete, partial, none | PatientOutcome | `analytics/services/outcomes.py` |
| `OutcomeEvent` | event_type, event_date, details | PatientOutcome | `analytics/services/outcomes.py` |
| `VisitStatus` | scheduled, completed, missed, cancelled | ScheduledVisit | `scheduling/models.py` |

---

## Knowledge & Reasoning Value Objects

| Value Object | Attributes | Used By | Source |
|---|---|---|---|
| `RuleData` | conditions: [], weight, explanation, recommendations | KnowledgeBaseEntry | `knowledge/models.py:43` |
| `Condition` | field, operator, value | KnowledgeBaseEntry.rule_data | `knowledge/services.py` |
| `EvidenceGrade` | 1, 2, NG, OP | KnowledgeBaseEntry | `knowledge/models.py:36` |
| `RuleType` | diagnostic, treatment, monitoring, referral, prognostic, exclusion | KnowledgeBaseEntry | `knowledge/models.py:21` |
| `DifferentialItem` | disease_id, disease_name, score, matched_rules_count, source, evidence_grade | ClinicalProfile.differential | `engine.py:84` |
| `DiseaseTrajectory` | trend, detail, confidence, kidney_survival_estimate | ClinicalProfile.disease_trajectory | `disease_trajectory.py` |
| `RiskAssessment` | overall, factors: [] | ClinicalProfile.risk_assessment | `engine.py:171` |
| `CareStage` | name, label, description, typical_duration_days, required_actions, next_stages | CarePathwayEngine | `care_pathway_engine.py:15` |
| `CareGap` | field, importance, message | ClinicalProfile.care_pathway | `care_pathway.py` |
| `PathwayDeviation` | stage, issue, severity, message | ClinicalProfile.care_pathway | `care_pathway_engine.py:155` |
| `ReasoningStep` | step, finding, detail, confidence | ClinicalProfile.reasoning_chain | `engine.py:143` |
| `InformationGap` | field, importance, message | ClinicalProfile.information_gaps | `engine.py:111` |
| `DiseaseMilestone` | milestone_type, label, date_identified, details, confidence | ClinicalProfile.milestones | `disease_milestones.py:14` |
| `UrgencyLevel` | level, tone, reasons | DecisionResult | `decision/models.py` |
| `RankedDifferential` | diagnoses: [], scores: [] | DecisionResult | `decision/models.py` |
| `QualityScore` | completeness, clarity, evidence, testability, overall, grade | KnowledgeQuality | `knowledge_quality.py:27` |
| `RuleConflict` | entry_id_1, entry_id_2, disease_id, field, severity, message | KnowledgeQuality | `knowledge_quality.py:138` |
| `CoverageReport` | total_rules, unique_diseases, unique_sources, rules per dimension | KnowledgeQuality | `knowledge_quality.py:163` |
| `CohortDefinition` | name, description, criteria | ResearchIntelligence | `research_intelligence.py:62` |
| `ProtocolMatch` | study_id, study_name, match_score, status | ResearchIntelligence | `research_intelligence.py:82` |
| `ComplianceScore` | patient_id, compliance_score, deductions, grade | OperationalIntelligence | `operational_intelligence.py:89` |
| `ExplainabilityReport` | summary, triggering_findings, matched_rules, guideline_support, evidence_quality, rejected_alternatives, information_gaps, reasoning_chain, recommendations, audit_trail | Explainability | `explainability.py:19` |

---

## Support Value Objects

| Value Object | Attributes | Used By | Source |
|---|---|---|---|
| `EventPayload` | arbitrary JSON | Event | `events/models.py:11` |
| `ConsentScope` | consent_type, form_version, scope text | Consent | `audit/models.py` |
| `ReviewStatus` | pending, approved, changes_requested, rejected | RuleReview | `knowledge/models.py` |
| `AuditAction` | CREATE, UPDATE, DELETE | AuditLog | `audit/models.py` |
| `CalendarWindow` | scheduled_date, reminder_offset | ScheduledVisit, Reminder | `scheduling/models.py` |
| `ExportFormat` | CSV, Excel, JSON | Export | `exports/` |
