# GDES_NEXT_DEVELOPMENT_PLAN_V9.md

**Project:** Glomerular Disease Expert System (GDES)

**Version:** V9 Development Roadmap

**Status:** Master Implementation Plan

**Target:** OpenCode Autonomous Development

**Priority:** Highest

---

# Executive Summary

After reviewing the current architecture, recent implementation, and code review findings, the development strategy for GDES is being revised.

The previous approach focused on adding new modules and infrastructure.

The new direction focuses on **Clinical Intelligence**, **Code Quality**, **Clinical Reasoning**, and **Maintainability**.

The objective is not to increase the size of GDES.

The objective is to significantly increase the quality of every clinical recommendation.

---

# Core Philosophy

## Intelligence > Features

Every future change must satisfy at least one of the following:

- Improves clinical reasoning
- Improves evidence quality
- Improves explainability
- Improves clinician workflow
- Improves patient safety
- Improves maintainability

If a proposed feature only adds code without improving intelligence, it should not be implemented.

---

# Development Rules

OpenCode SHALL NOT

- Create unnecessary Django apps
- Create duplicate models
- Create duplicate services
- Create overlapping workflows
- Increase architectural complexity without measurable benefit

Instead

Reuse

Refactor

Simplify

Improve

---

# Current Priority Order

## Phase 1

System Stabilization

## Phase 2

Clinical Intelligence

## Phase 3

Evidence Quality

## Phase 4

AI Optimization

## Phase 5

Workflow Optimization

## Phase 6

Knowledge Evolution

---

# PHASE 1 — SYSTEM STABILIZATION

Goal

Create a stable production foundation before adding intelligence.

---

## Task 1

Resolve every CRITICAL issue

Including

✓ Add vera_web ProviderType

✓ Fix ranking type mismatch

✓ Prevent ProviderRateLimit IntegrityError

---

## Task 2

Resolve HIGH priority issues

Including

Authentication

Prompt optimization

Dead fields

Migration cleanup

Evidence cache

---

## Task 3

Refactor

Remove

Duplicate code

Unused models

Unused services

Unused utilities

Technical debt

---

## Task 4

Increase unit test coverage

Target

95%

Every service

Every provider

Every validator

Every orchestrator

Every cache

Every prompt generator

Must have tests.

---

# PHASE 2 — BUILD CLINICAL INTELLIGENCE

Do NOT build another Django module.

Create ONE orchestration service.

ClinicalIntelligenceService

Responsibilities

Analyze patient

Generate recommendation

Retrieve evidence

Review evidence

Calculate confidence

Generate explanation

Generate final recommendation

This becomes the heart of GDES.

---

# PHASE 3 — EVIDENCE PIPELINE

Use only reliable public APIs.

Priority

PubMed

Europe PMC

Semantic Scholar

OpenAlex

CrossRef

These become the evidence backbone.

No unnecessary providers.

---

# AI REVIEWER

Primary AI

GPT-5 API

Purpose

Independent reviewer

NOT

Primary decision maker

Prompt

Does the evidence support the recommendation?

What evidence conflicts?

What confidence?

Explain your reasoning.

Return structured JSON.

---

# Recommendation Pipeline

Patient

↓

Knowledge Engine

↓

Recommendation

↓

Evidence Retrieval

↓

Evidence Ranking

↓

GPT Review

↓

Confidence

↓

Explanation

↓

Display

---

# PHASE 4 — SMART PROMPTS

Current implementation sends too much information.

This must change.

Instead of

Entire patient snapshot

Use

Diagnosis

Disease stage

Proteinuria

eGFR

Relevant biopsy

Key medications

Important contraindications

Clinical question

Nothing else.

Goal

Reduce

Tokens

Latency

Cost

PHI exposure

Hallucinations

---

# PHASE 5 — CASE COMPLEXITY

Not every patient requires AI.

Implement

Case Complexity Score

Simple CKD

↓

Knowledge Engine only

Moderate complexity

↓

Evidence APIs

Complex GN

↓

Evidence APIs

+

GPT Review

Rare disease

↓

Evidence APIs

+

GPT Review

+

Optional Vera consultation

This dramatically reduces cost.

---

# PHASE 6 — BETTER EVIDENCE

Improve ranking.

Current ranking is insufficient.

New ranking factors

Guideline citation

Meta-analysis

RCT

Systematic review

Journal quality

Citation count

Kidney relevance

Publication recency

Disease specificity

Evidence level

The goal is

Clinical relevance

not

Search relevance.

---

# PHASE 7 — EXPLAINABILITY

Every recommendation must explain itself.

Example

Recommendation

Start MMF

Why?

KDIGO 2024 Recommendation 3.8

Evidence

12 PubMed papers

3 Meta-analyses

GPT Review

Supports recommendation

Agreement

98%

Confidence

97%

Never display a recommendation without an explanation.

---

# PHASE 8 — CLINICIAN TRUST

Build trust.

Every recommendation shall include

Supporting guideline

Supporting evidence

Confidence

Alternative options

Known controversies

Latest publications

This is more valuable than simply producing an answer.

---

# PHASE 9 — OPTIONAL VERA CONSULTATION

Vera shall NOT become a dependency.

Workflow

Recommendation

↓

Evidence APIs

↓

GPT Review

↓

Display

↓

Optional

Consult Vera

↓

Compare opinions

↓

Save

Vera becomes

Expert Second Opinion

NOT

Primary reasoning engine.

---

# SMART VERA PROMPT

Automatically generate

Diagnosis

Current disease stage

Biopsy

Laboratory summary

Current treatment

GDES recommendation

Evidence summary

Specific clinical question

The clinician only needs

Copy

Paste

Review

---

# PHASE 10 — CONTINUOUS LEARNING

Implement

Knowledge Feedback Loop

Recommendation

↓

Clinician Override

↓

Reason

↓

Review Queue

↓

Knowledge Committee

↓

Knowledge Base Update

The system should continuously improve.

---

# PHASE 11 — PERFORMANCE

Target

Recommendation

<2 seconds

Evidence retrieval

<5 seconds

GPT review

<10 seconds

Complete workflow

<15 seconds

Cache hit

>80%

---

# PHASE 12 — CODE QUALITY

OpenCode shall

Prefer refactoring

Prefer composition

Prefer reuse

Avoid

Duplicate services

Duplicate models

Duplicate APIs

Duplicate workflows

Technical debt must decrease every sprint.

---

# PHASE 13 — TESTING

Every new feature requires

Unit tests

Integration tests

Failure tests

Mock provider tests

Performance tests

Security tests

Regression tests

Target

95%+

Coverage

---

# SUCCESS METRICS

Measure

Recommendation quality

Guideline compliance

Clinician trust

Explanation quality

Evidence quality

Latency

API cost

Maintainability

Do NOT measure

Number of modules

Number of models

Lines of code

---

# IMPLEMENTATION ORDER

Sprint 1

Stabilize codebase

Fix all CRITICAL and HIGH issues

Refactor duplicated code

Increase test coverage

---

Sprint 2

Refactor ClinicalIntelligenceService

Implement intelligent orchestration

Simplify workflow

---

Sprint 3

Improve evidence retrieval

Improve ranking

Improve caching

---

Sprint 4

Optimize GPT prompts

Implement case complexity scoring

Reduce token usage

---

Sprint 5

Improve explanations

Confidence engine

Clinical reasoning

---

Sprint 6

Clinician feedback loop

Knowledge evolution

Continuous improvement

---

# NON-GOALS

Do NOT

Create more Django apps

Create more models unless unavoidable

Create more settings pages

Create duplicate evidence modules

Integrate unsupported providers

Increase architectural complexity

---

# FINAL PRINCIPLE

The next version of GDES must become

Smarter

Not Bigger.

Every commit should make the system

- More clinically accurate
- More evidence-based
- More explainable
- Faster
- Easier to maintain
- Easier for nephrologists to trust

The measure of success is not how much code exists.

The measure of success is whether a nephrologist can make safer, faster, and more evidence-based decisions with confidence.

---

# OpenCode Implementation Instructions

1. Stop creating new architectural layers unless absolutely necessary.
2. Refactor and simplify existing code before adding features.
3. Resolve all critical and high-priority review findings before implementing new functionality.
4. Consolidate intelligence into a single `ClinicalIntelligenceService` that orchestrates existing components.
5. Build around free, reliable evidence sources (PubMed, Europe PMC, Semantic Scholar, OpenAlex, CrossRef).
6. Use GPT-5 strictly as an evidence reviewer and explanation engine, never as the primary decision-maker.
7. Treat Vera as an optional expert consultation workflow with structured prompt generation.
8. Prioritize explainability, clinician trust, performance, and maintainability over feature expansion.
9. Preserve backward compatibility and maintain comprehensive automated tests throughout development.

**Guiding Principle:**

> **Build Better Intelligence, Not Bigger Software.**