# Fable Ultracode Phase Workspace

這個資料夾是給 Fable / Fabo 使用的三階段工作資料夾。  
請在同一個 repo，例如 `fable-style-project-harness/` 底下建立一個工作 branch，然後依序執行 Phase 1 → Phase 2 → Phase 3。

建議流程：

```bash
cd fable-style-project-harness
git checkout -b ai-review-adaptive-harness-v2
```

然後依序把以下 prompt 貼給 Fable：

1. `00_MASTER_ORCHESTRATOR.md`  
   先讓 Fable 理解三階段總目標與執行邊界。

2. `01_ai_review_ultracode_optimization.md`  
   Phase 1：AI-review slash command 大優化，包含 CLAUDE.md、Codex delegation、tool/code invocation efficiency。

3. `02_adaptive_harness_skill_ultracode.md`  
   Phase 2：建立 adaptive-harness skill，讓 AI-review 的結果可以進入 rolling improvement loop。

4. `03_full_integration_validation_ultracode.md`  
   Phase 3：真正測試 AI-review + adaptive-harness 是否能完整使用，並設計 Opus / Sonnet / Haiku / Codex 等模型層級驗證。

5. `99_OPEN_OPTIMIZATION_SPACE.md`  
   給 Fable 額外設計空間。當它發現更好的架構、缺失、風險或簡化方式時，必須記錄在這裡，而不是直接無限制擴張系統。

核心原則：

- 三個 Phase 都必須開 `ultracode`。
- 每個 Phase 都要產生可驗證結果，而不是只寫建議。
- Phase 3 是驗收，不是繼續無限加功能。
- scheduled runner 預設 report-only。
- high-risk harness changes 只能產生 patch proposal。
- 不要直接污染 main branch。
- 不要讓系統變成更肥的 prompt collection。
- AI-review 做 local review。
- adaptive-harness 做 rolling system improvement。
- deterministic scripts 做掃描、驗證、report/history。
- LLM 做判斷、取捨、優先級、benchmark 解讀。
- human 保留高風險決策權。


## Optional overlay: codebase memory / knowledge graph

如果目前 repo 已經在使用 codebase memory / codebase-memory MCP / knowledge graph retrieval，請在 Phase 1 或 Phase 2 之後視需要執行：

```text
04_codebase_memory_knowledge_graph_overlay.md
```

這不是第四個主 Phase。  
它的目的不是新增大型記憶系統，而是檢查現有 codebase memory 是否能支援 AI-review、adaptive-harness、rolling improvement、lower-tier model routing，以及 retrieval / stale-reference / benchmark linkage。


## Final first prompt

如果你只想知道第一句要怎麼貼給 Fable / Fabo，請使用：

```text
FINAL_FIRST_PROMPT.md
```

這個檔案會讓 Fable 先讀 `00_MASTER_ORCHESTRATOR.md`，再依序處理 Phase 1、Phase 2、optional codebase memory / KG overlay、Phase 3。


## Updated first-use instruction

Use `FINAL_FIRST_PROMPT.md` as the first message.  
It now tells Fable / Fabo to create or select its own working branch, check git status, avoid main, and preserve long-term maintainability / observability / traceability / rollback safety.

Recommended first action:

```text
Paste the full contents of FINAL_FIRST_PROMPT.md to Fable / Fabo.
```
