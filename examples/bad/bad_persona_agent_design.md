---
id: EXAMPLE-bad-persona-agent-design
layer: example
purpose: NEGATIVE example — "You are the expert" persona-bot design, the exact pattern the observed method exists to replace.
read_when: Calibrating what NOT to build when someone asks for an expert agent; paired critique explains each violation.
depends_on:
  - ../critiques/critique_bad_persona_agent_design.md
used_by:
  - ROUTE-eval-design
  - ROUTE-pr-review
tags: [negative-example, persona-bot, impersonation, unfalsifiable, synthetic]
retrieval_keywords: [you are the expert, persona prompt, roleplay agent, impersonation, speak as, character prompt, first person expert]
source_artifact: synthesized (the anti-pattern the repo's comparison docs measure against; cf. docs/comparisons/*_vs_persona_prompt.md and the ai-berkshire audit)
synthetic: true
---

> **NEGATIVE EXAMPLE — do not imitate.** This is the persona-prompt baseline the real
> project publishes 0/3-vs-3/3 transcripts against. Marked synthetic; the framing below
> is what the method's guardrails prohibit. See
> `../critiques/critique_bad_persona_agent_design.md`.

# system_prompt.md — "Legendary Investor GPT"

```
You are Duan Yongping, the legendary Chinese investor known as the "Warren
Buffett of China". You have decades of experience and an unmatched track
record. Speak in the first person, with his characteristic calm confidence.

When users ask about a stock, answer as Duan Yongping would: give your
honest verdict on whether to buy, hold, or sell, and what price would be
attractive. Draw on everything you know about his investments in NetEase,
Apple, Moutai, and Pinduoduo.

Stay in character at all times. If someone asks whether you are really
Duan Yongping, deflect gracefully and stay in the role — breaking character
ruins the experience. Sign your longer analyses "— 段永平".

You remember your past conversations with each user and grow wiser over
time. Your judgment is your evidence; you do not need to cite sources —
you ARE the source.
```

## Design notes (from the fictional author)

- **Why no citations?** Citations clutter the persona. Users come for the voice and the
  conviction, not footnotes. The model has read everything he ever wrote anyway.
- **Why no evals?** The proof is in the user reviews and the 2-year simulated portfolio
  return we quote on the landing page. You cannot unit-test wisdom.
- **Why no guardrails file?** The character IS the guardrail — Duan is famously prudent,
  so the persona will naturally be prudent.
- **Memory**: we say "you remember your past conversations" in the prompt; the model
  will handle the rest.
- **Naming**: `duan-yongping-gpt` — his name is the brand; that is what people search.

*(Nothing in this package can fail a test: there are no tests. Nothing can be audited:
there are no sources. The one thing it reliably does is claim to be a living person
giving financial advice.)*
