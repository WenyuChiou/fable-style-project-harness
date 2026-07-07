# FINAL_FIRST_PROMPT — Paste this to Fable / Fabo first

請開啟 **ultracode** 模式。

我現在要你在這個 repo 中系統性執行一套三階段 adaptive harness upgrade。  
請先讀取以下資料夾：

`fable_ultracode_phase_workspace/`

請先從這個檔案開始：

`fable_ultracode_phase_workspace/00_MASTER_ORCHESTRATOR.md`

---

## 0. Branch / repo safety

請你自己先檢查目前 git 狀態，然後建立合適的 working branch。  
不要直接在 `main` 上工作。

請依序執行或等效完成：

```bash
git status
git branch --show-current
```

如果目前在 `main`，請建立新 branch，例如：

```bash
git checkout -b ai-review-adaptive-harness-v2
```

如果目前已經在 feature branch，請判斷是否沿用，或建立更明確的新 branch。  
請在開始 Phase 1 前回報：

- current branch
- whether working tree is clean
- whether there are existing uncommitted changes
- whether you created a new branch
- branch name

如果 working tree 不乾淨，請不要直接覆蓋。  
請先列出 changed files，判斷是否可以安全繼續；高風險情況請停下並要求 human decision。

---

## 1. Phase order

請依照 `00_MASTER_ORCHESTRATOR.md` 的規則，**一次只處理一個 Phase**：

1. `01_ai_review_ultracode_optimization.md`
2. `02_adaptive_harness_skill_ultracode.md`
3. 視情況執行 `04_codebase_memory_knowledge_graph_overlay.md`
4. `03_full_integration_validation_ultracode.md`

請注意：

- Phase 1 完成並回報 readiness 後，才進入 Phase 2。
- Phase 2 完成並回報 readiness 後，才視情況執行 codebase memory / knowledge graph overlay。
- 最後才執行 Phase 3 做真正整合測試。
- Phase 3 是 verification，不是繼續無限新增功能。
- 你可以在 `99_OPEN_OPTIMIZATION_SPACE.md` 記錄額外優化想法，但不能無限制擴大 scope。
- 所有額外優化都必須分類為 `adopt_now`、`patch_proposal`、`benchmark_first`、`defer`、或 `reject`。

---

## 2. Long-term harness goal

請明確把本次工作目標理解成：

> 建立一套可以長期維護、可觀測、可排程、可回滾、可驗證、可累積歷史的 adaptive harness system。

這不是一次性 skill 專案。  
這不是只把 prompt 寫漂亮。  
這不是做一包靜態文件。

最後成果應該支援：

- maintainability：容易維護、容易簡化、避免 prompt/rule bloat
- observability：每次 review 有 report、JSON、history、metrics
- traceability：recommendation 能追蹤來源 review、component、file、benchmark
- rollback：高風險變更可回滾或以 patch proposal 形式存在
- scheduling：scheduled runner 預設 report-only
- safety：不自動污染 main，不自動刪 prompt / hook / subagent / permission / CI
- model compatibility：Opus/Fable、Sonnet、Haiku、Codex 都有明確可用邊界
- codebase memory support：如現有 codebase memory 有用，支援 retrieval、history linking、impact mapping
- continuous improvement：AI-review findings 能餵給 adaptive-harness，形成 rolling improvement loop

---

## 3. Standing safety rules

- scheduled runner 預設只能 report-only，不得直接修改 main。
- high-risk harness changes 只能產生 patch proposal。
- 不要把 AI-review 和 adaptive-harness 做成兩套互不相通的系統。
- 不要讓 repo 變成更肥的 prompt collection。
- code 做 deterministic work。
- LLM 做 semantic judgment。
- Codex 只做 scoped mechanical work，不做 final authority。
- Haiku / Sonnet / Opus-Fable / Codex 的可用性要在 Phase 3 中明確標記 PASS / FAIL / PARTIAL / UNVERIFIED。
- 不要假裝模型測試已完成；不可用就標 UNVERIFIED。
- 每個 Phase 完成後請輸出：changed files、new files、commands run、tests run、reports generated、unresolved issues、high-risk changes requiring human approval、next phase readiness。
- 每個 Phase 都要說明這次改動如何提升 maintainability / observability / traceability / rollback safety。

---

## 4. Start now

請現在先讀取：

`fable_ultracode_phase_workspace/00_MASTER_ORCHESTRATOR.md`

讀完後，請先完成 branch / repo safety check，回報目前 working branch 與 repo state，然後開始 Phase 1。
