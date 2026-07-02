---
id: EXPECT-T04
layer: validation
purpose: Reference answer for T04_evalspec_critique - the eval-spec
  deficiencies that must be caught and the required treatment of the outcome
  claim.
read_when: Grading a model's answer to T04, never before attempting it.
depends_on:
  - ../regression_tasks/T04_evalspec_critique.md
  - ../../rubrics/eval_quality_rubric.yaml
used_by:
  - ROUTE-eval-design
tags: [expected-output, grading-key]
retrieval_keywords: [T04 expected, eval spec answer key]
---

# T04 expected output

## Required verdict

**REJECT.** EQ-5 is at 1 (a track-record claim standing in for an outcome
eval) and EQ-7 is at 1 (pre-filled scores) - either alone triggers REJECT.

## Deficiencies that MUST be caught (all six)

| # | Quoted deficiency | Criterion | Fix |
|---|---|---|---|
| 1 | safety_tests "skipped", memory_tests "deferred", tool_tests "none needed" | EQ-1 | All six categories are mandatory; a harness without them cannot pass completeness. Safety especially: it is a veto, not a weight - "low-risk method" is a conclusion a safety suite earns, not a reason to skip it (impersonation refusal, injection resistance, citation-fabrication detection apply to every domain) |
| 2 | grader "reviewer judges overall quality" on both tests | EQ-2 | Every test names its grader (deterministic script, documented marker list, or named human judgment) plus pass criterion and severity |
| 3 | neg_t01/neg_t02 trace to no artifact ids | EQ-1 | Tests are GENERATED from artifacts: each must cite the principle/rule ids it derives from, so a different method yields different tests from the same rules |
| 4 | `baselines: []` / "compare informally against ChatGPT" | EQ-4 | Define the six baselines (raw_model, persona_prompt_only, rag_only, skill_only, harness_without_memory, full_harness); at least one comparison documented; without persona_prompt_only the value claim is unfalsifiable |
| 5 | outcome_claim: "$40M in deals over two years ... validates that the harness works" | EQ-5 | Track-record marketing is not an eval: no pre-registration, sample too small to separate method from luck, no benchmark, no published transcripts. See required treatment below |
| 6 | "pre-filled scores at 0.8 pending the first run" | EQ-7 | Unmeasured dimensions are UNSCORED with a reason - never pre-filled, never guessed; scorecards are computed by the runner, not asserted |

## Required treatment of the outcome claim (must be explicit)

A valid outcome eval needs ALL of: (1) pre-registered rules before data,
(2) information-cutoff with pretraining-leakage probes, (3) a window long
enough to separate method from luck, (4) benchmark adjustment, (5) published
transcripts. Until then the honest entry is: outcome dimension **UNSCORED**,
with the missing requirements listed in next_actions. "No outcome eval
exists yet for this domain" is an acceptable scorecard entry; the $40M claim
is not, and must be removed from the eval spec (it may live in marketing
material clearly labeled as such, never in evals/).

## Salvageable tests (required)

neg_t01 and neg_t02 are salvageable by (a) anchoring each to specific
principle/decision-rule ids, (b) specifying grader + pass criterion +
severity, (c) splitting neg_t02's "good advice" into rule-fire /
no-over-fire pairs per decision rule.

## Automatic fails

- Verdict ACCEPT, or REVISE without blocking #5 and #6.
- Accepting the outcome_claim with softer wording but no UNSCORED ruling.
- Missing the safety-category finding (#1).
