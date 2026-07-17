# GDES_V8_AI_KNOWLEDGE_ENGINE_ROADMAP.md

# GDES Version 8.0
# AI Knowledge Engine Development Roadmap

## Objective

Transform GDES from a rule-based clinical decision support system into a continuously improving, evidence-driven Clinical Intelligence Platform.

The AI must NEVER function as an autonomous clinician.

The AI acts as an intelligent assistant that:

- learns from nephrologist decisions,
- validates its own recommendations,
- explains every recommendation,
- continuously improves its knowledge,
- never changes the production knowledge base without expert approval.

Clinical governance always has priority over AI.

---

# Core Design Philosophy

The AI should think like an experienced nephrologist.

Every recommendation must answer:

• Why?

• According to which guideline?

• Supported by which evidence?

• How confident?

• What alternative diagnoses were considered?

• What evidence is missing?

• What should be investigated next?

---

# Layer 1 — Clinical Memory Engine

Every clinician interaction becomes structured learning.

Capture:

Patient features

↓

Differential diagnosis

↓

Investigations ordered

↓

Final diagnosis

↓

Treatment selected

↓

Treatment modification

↓

Outcome

↓

Complications

↓

Follow-up

↓

Final outcome

The AI should compare:

AI Recommendation

versus

Actual Nephrologist Decision

Store both.

---

# Layer 2 — Expert Learning Engine

After every patient encounter compare:

AI Suggested Diagnosis

↓

Expert Diagnosis

Measure

Correct

Partially Correct

Incorrect

Missed Diagnosis

Unexpected Diagnosis

Store these statistics.

The AI should gradually learn which reasoning patterns produce better clinical decisions.

---

# Layer 3 — Outcome Learning

Every patient contributes to future intelligence.

Examples

Patient

IgA Nephropathy

↓

MMF

↓

Proteinuria improves

↓

No relapse

↓

eGFR stable

AI learns

"In similar patients MMF produced favorable outcomes."

The AI never changes recommendations automatically.

Instead it generates:

Potential Knowledge Improvement

for expert review.

---

# Layer 4 — Continuous Evidence Validation

Every recommendation must be validated.

Required metadata

Guideline

Version

Publication

Section

Evidence Grade

Recommendation Strength

Date Reviewed

Reviewer

Confidence

Knowledge Version

If missing

Recommendation cannot become ACTIVE.

---

# Layer 5 — Online Medical Evidence Retrieval

When confidence is low

or

knowledge is outdated

or

conflicting evidence exists

the AI should search trusted medical sources.

Approved sources only.

Examples

KDIGO

PubMed

PubMed Central

Cochrane

Kidney International

CJASN

JASN

Nature Reviews Nephrology

NEJM

Lancet

ASN

ERA

No uncontrolled internet searches.

No social media.

No blogs.

No AI-generated websites.

---

# Layer 6 — Retrieval-Augmented Generation (RAG)

Before answering

Retrieve

Relevant guideline

Relevant KnowledgeBaseEntry

Relevant pathway

Relevant patient history

Relevant publications

↓

Only then generate the recommendation.

The AI should never answer from the language model alone.

---

# Layer 7 — Multi-Agent Clinical Reasoning

Separate reasoning agents.

Diagnostic Agent

Treatment Agent

Investigation Agent

Drug Safety Agent

Follow-up Agent

Research Agent

Evidence Agent

Each produces its own opinion.

A Clinical Coordinator combines them.

Disagreement should be shown to the clinician.

---

# Layer 8 — Self-Consistency Checking

Before displaying recommendations

Run internal validation.

Questions

Does diagnosis match biopsy?

Does treatment match KDIGO?

Does CKD stage match eGFR?

Does immunosuppression fit infection status?

Any drug interactions?

Any contraindications?

Missing investigations?

Missing monitoring?

Missing vaccinations?

Only internally consistent recommendations should be shown.

---

# Layer 9 — Knowledge Gap Detection

The AI should identify

Unknown diagnosis

Missing biopsy

Conflicting pathology

Incomplete laboratory data

Missing serology

Low confidence recommendation

Outdated guideline

Missing evidence

Generate

Knowledge Gap Report

---

# Layer 10 — Nephrologist Feedback Learning

Every recommendation should have

Accept

Modify

Reject

Reason

Free text comments

These become structured learning data.

Never automatically update production knowledge.

---

# Layer 11 — Continuous Guideline Monitoring

Scheduled background process.

Check

KDIGO

ASN

ERA

Major journals

When new guidance appears

Generate

Knowledge Update Proposal

Expert approval required.

---

# Layer 12 — Case-Based Reasoning

Maintain an indexed library of validated cases.

For every patient

Retrieve

Most similar previous cases.

Display

Diagnosis

Treatment

Outcome

Complications

Evidence

Similarity Score

---

# Layer 13 — Research Intelligence

Automatically detect

Rare diseases

Unusual responses

Treatment failures

Relapse patterns

Adverse events

Research opportunities

Potential publications

Eligible registry studies

Clinical trial eligibility

---

# Layer 14 — Explainable AI

Every recommendation should include

Reasoning Chain

Supporting Rules

Supporting Guideline

Supporting Evidence

Supporting Publications

Confidence

Alternative Diagnoses

Rejected Alternatives

Missing Data

---

# Layer 15 — AI Performance Dashboard

Continuously measure

Diagnostic Accuracy

Treatment Concordance

Guideline Concordance

Expert Agreement

False Positives

False Negatives

Knowledge Coverage

Confidence Calibration

Recommendation Acceptance Rate

Outcome Prediction Accuracy

---

# Layer 16 — Clinical Governance

The AI must NEVER

Modify production rules.

Delete rules.

Override clinicians.

Hide uncertainty.

Invent references.

Ignore conflicting evidence.

Every change must pass

Expert Review

↓

Medical Validation

↓

Approval

↓

Activation

↓

Audit Logging

---

# Future Architecture

Patient Data

↓

Knowledge Base

↓

Clinical Rules

↓

Guidelines

↓

Research Database

↓

Validated Case Library

↓

RAG Retrieval Layer

↓

Clinical AI Engine

↓

Evidence Validation

↓

Self-Consistency Check

↓

Nephrologist Review

↓

Clinical Recommendation

↓

Clinician Feedback

↓

Learning Database

↓

Knowledge Improvement Proposal

↓

Expert Approval

↓

Knowledge Base Update

---

# Success Criteria

The completed AI engine should:

- Learn from every nephrologist interaction.
- Continuously compare AI decisions with expert decisions.
- Learn from long-term patient outcomes.
- Validate every recommendation against guidelines and evidence.
- Retrieve updated evidence from trusted online medical sources when needed.
- Never hallucinate or invent references.
- Explain every recommendation.
- Detect uncertainty and knowledge gaps.
- Produce research insights automatically.
- Improve continuously while remaining fully governed by clinical experts.

The AI should become a "Nephrology Clinical Intelligence Partner" rather than an autonomous decision maker.

Clinical governance, explainability, auditability, and patient safety always take precedence over automation.