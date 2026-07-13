"""Domain event type constants for the event orchestration system."""

# Patient lifecycle
PATIENT_REGISTERED = "patient.registered"
PATIENT_UPDATED = "patient.updated"

# Encounters
ENCOUNTER_CREATED = "encounter.created"
ENCOUNTER_UPDATED = "encounter.updated"
ENCOUNTER_COMPLETED = "encounter.completed"

# Labs
LAB_RESULT_CREATED = "lab_result.created"
LAB_RESULT_UPDATED = "lab_result.updated"

# Biopsy
BIOPSY_CREATED = "biopsy.created"
BIOPSY_FINALIZED = "biopsy.finalized"

# Clinical events
CLINICAL_EVENT_CREATED = "clinical_event.created"
CLINICAL_ASSESSMENT_CREATED = "clinical_assessment.created"
CLINICAL_ASSESSMENT_UPDATED = "clinical_assessment.updated"
HARD_KIDNEY_ENDPOINT = "hard_kidney_endpoint.reached"
DEATH_RECORDED = "death.recorded"

# Prescriptions / medications
PRESCRIPTION_CREATED = "prescription.created"
PRESCRIPTION_FINALIZED = "prescription.finalized"
MEDICATION_STARTED = "medication.started"

# Treatment
TREATMENT_EXPOSURE_CREATED = "treatment_exposure.created"
TREATMENT_EXPOSURE_UPDATED = "treatment_exposure.updated"

# Knowledge / decision support
DECISION_REQUESTED = "decision.requested"
RECOMMENDATION_GENERATED = "recommendation.generated"
SAFETY_ALERT_RAISED = "safety_alert.raised"

# Reminders / scheduling
REMINDER_SENT = "reminder.sent"
FOLLOW_UP_SCHEDULED = "follow_up.scheduled"
VISIT_OVERDUE = "visit.overdue"

# Outcomes
OUTCOME_RECORDED = "outcome.recorded"
OUTCOME_RECOMPUTED = "outcome.recomputed"
DISEASE_TRAJECTORY_UPDATED = "disease_trajectory.updated"

# Follow-up engine
FOLLOW_UP_PLAN_UPDATED = "follow_up_plan.updated"
FOLLOW_UP_TASK_CREATED = "follow_up_task.created"
FOLLOW_UP_TASK_COMPLETED = "follow_up_task.completed"
FOLLOW_UP_TASK_OVERDUE = "follow_up_task.overdue"
FOLLOW_UP_ESCALATED = "follow_up.escalated"

# Clinical reasoning
CLINICAL_PROFILE_UPDATED = "clinical_profile.updated"
CARE_PATHWAY_UPDATED = "care_pathway.updated"
REASONING_COMPLETED = "reasoning.completed"

# All known events for subscription validation
ALL_EVENTS = frozenset({
    PATIENT_REGISTERED, PATIENT_UPDATED,
    ENCOUNTER_CREATED, ENCOUNTER_UPDATED, ENCOUNTER_COMPLETED,
    LAB_RESULT_CREATED, LAB_RESULT_UPDATED,
    BIOPSY_CREATED, BIOPSY_FINALIZED,
    CLINICAL_EVENT_CREATED, CLINICAL_ASSESSMENT_CREATED, CLINICAL_ASSESSMENT_UPDATED, HARD_KIDNEY_ENDPOINT, DEATH_RECORDED,
    PRESCRIPTION_CREATED, PRESCRIPTION_FINALIZED, MEDICATION_STARTED,
    TREATMENT_EXPOSURE_CREATED, TREATMENT_EXPOSURE_UPDATED,
    DECISION_REQUESTED, RECOMMENDATION_GENERATED, SAFETY_ALERT_RAISED,
    REMINDER_SENT, FOLLOW_UP_SCHEDULED, VISIT_OVERDUE,
    OUTCOME_RECORDED, OUTCOME_RECOMPUTED, DISEASE_TRAJECTORY_UPDATED,
    CLINICAL_PROFILE_UPDATED, CARE_PATHWAY_UPDATED, REASONING_COMPLETED,
    FOLLOW_UP_PLAN_UPDATED, FOLLOW_UP_TASK_CREATED, FOLLOW_UP_TASK_COMPLETED,
    FOLLOW_UP_TASK_OVERDUE, FOLLOW_UP_ESCALATED,
})
