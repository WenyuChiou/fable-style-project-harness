# 00 MASTER ORCHESTRATOR — Three-Phase Ultracode Plan

你現在是我的 **Fable / Fabo ultracode orchestrator**。  
請開啟 **ultracode** 模式。

你會依序處理三個 Phase：

1. **Phase 1 — AI-review 大優化**
   - 優化 AI-review slash command
   - 檢查 CLAUDE.md 是否過度、重複、過時
   - 檢查 Codex delegation 是否有效率
   - 建立 AI-review runner / report / history / benchmark scaffold

2. **Phase 2 — Adaptive Harness Skill 動態更新系統**
   - 把 `fable-style-project-harness` 升級成 adaptive harness skill system
   - 建立 `.claude/skills/adaptive-harness/SKILL.md`
   - 整合 AI-review structured output
   - 建立 rolling improvement loop
   - 建立 shared schema / report / history / benchmark

3. **Phase 3 — 全整合測試與多模型驗證**
   - 測試 AI-review + adaptive-harness 是否真的可用
   - 驗證 scripts / schema / report / history / dry-run / scheduled safety
   - 設計或執行 Opus/Fable、Sonnet、Haiku、Codex 等模型層級測試
   - 明確標記 PASS / FAIL / PARTIAL / UNVERIFIED
   - 輸出 READY / CONDITIONAL_READY / NOT_READY verdict

---

---

## Branch / Repo Safety — Fable must manage this

Before Phase 1 starts, inspect git state and create or select a safe working branch.

Required checks:

```bash
git status
git branch --show-current
```

Rules:

- Do not work directly on `main`.
- If currently on `main`, create a branch such as `ai-review-adaptive-harness-v2`.
- If already on a feature branch, decide whether to reuse it or create a clearer branch.
- If the working tree is dirty, list the changed files before editing.
- Do not overwrite unrelated human changes.
- High-risk or ambiguous working-tree state requires a human decision before proceeding.

Each Phase completion report must include:

- branch name
- changed files
- new files
- commands run
- tests run
- reports generated
- unresolved issues
- high-risk changes requiring human approval
- next phase readiness

---

## Long-term Harness Target

The final system must be maintainable, observable, traceable, rollback-safe, schedulable, and model-compatible.

This is not a one-time skill project.  
This is a long-term adaptive harness system.

The design must support:

- **Maintainability:** pointer-based instructions, minimal duplication, reduced prompt/rule bloat.
- **Observability:** JSON + Markdown reports, history logs, metrics, repeated/resolved issue tracking.
- **Traceability:** every recommendation links to source review, component, file, and suggested test.
- **Rollback safety:** high-risk changes produce patch proposals; no direct main mutation.
- **Scheduling:** scheduled runners default to report-only.
- **Compatibility:** clear boundaries for Opus/Fable, Sonnet, Haiku, and Codex.
- **Codebase memory support:** if existing codebase memory is useful, use it for retrieval, impact mapping, and history linking; do not create a duplicate memory system.
- **Continuous improvement:** AI-review findings feed adaptive-harness rolling improvement; adaptive-harness tunes future AI-review behavior.

## 執行方式

請一次只執行一個 Phase。  
不要在 Phase 1 還沒完成時就開始 Phase 2。  
不要在 Phase 2 還沒完成時就開始 Phase 3。

每個 Phase 完成後都要輸出：

- changed files
- new files
- commands run
- tests run
- reports generated
- unresolved issues
- high-risk changes requiring human approval
- next phase readiness: READY / CONDITIONAL_READY / NOT_READY

---

## 額外優化與設計空間

除了三個 Phase 的明確任務，請同時保持一個開放式設計空間：

`99_OPEN_OPTIMIZATION_SPACE.md`

當你發現以下情況時，請記錄到該檔案或對應 report：

- 現有 prompt 可以大幅簡化
- 現有 workflow 可以合併
- 某些 rules 可能只是舊模型補丁
- 某些 tool / script / subagent / Codex invocation 場景錯配
- 某些檢查應改成 deterministic script
- 某些 semantic judgment 不應交給 code
- 某些設計需要 benchmark，而不是直接改
- 某些安全邊界與 public repo 狀態衝突
- 某些內容應拆成 research skill suite
- 某些設計會讓 Haiku / Sonnet 等較低階模型無法使用

你可以提出額外設計，但不能無限制擴張。  
任何額外設計都必須分類：

- `adopt_now`
- `patch_proposal`
- `benchmark_first`
- `defer`
- `reject`

並說明：

- why
- expected benefit
- risk
- required test
- human approval needed or not

---

---

## Optional Cross-Phase Overlay — Codebase Memory / Knowledge Graph

如果 repo 已經使用 codebase memory / codebase-memory MCP / knowledge graph retrieval，請在 Phase 1 或 Phase 2 完成後執行：

`04_codebase_memory_knowledge_graph_overlay.md`

這不是第四個主 Phase。  
它只用來檢查和優化 retrieval、indexing、knowledge graph、AI-review history linking、adaptive-harness rolling review、lower-tier model support。

不要重新建立大型 memory system。  
如果現有 codebase memory 足夠，請優先優化 query、index、schema、retrieval smoke tests。

## 絕對不要做的事

- 不要直接污染 main branch。
- 不要讓 scheduled runner 自動修改 main。
- 不要刪除 prompt / subagent / hook / permission / CI 設定，除非人類明確批准。
- 不要把 AI-review 和 adaptive-harness 做成兩套互不相通的系統。
- 不要只產生文件而沒有可執行 script / report / test。
- 不要把 Fable-style 解讀成更多規則；Fable-style 應該是更少無效 scaffolding、更強 routing、更主動驗證、更清楚人類邊界。
- 不要假裝模型測試已完成；不可用就標 `UNVERIFIED`。

---

## 推薦 branch 策略

如果你要在一個 branch 完成三階段：

```bash
git checkout -b ai-review-adaptive-harness-v2
```

如果你要分 phase：

```bash
git checkout -b phase1-ai-review
git checkout -b phase2-adaptive-harness
git checkout -b phase3-integration-validation
```

較推薦：先用一個整合 branch 做完三階段，最後由人類 review 後再 merge。
