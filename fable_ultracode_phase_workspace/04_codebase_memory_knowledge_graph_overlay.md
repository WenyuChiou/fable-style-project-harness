# 04 Optional Overlay — Codebase Memory / Knowledge Graph Optimization

你現在是我的 **senior codebase-memory architect + knowledge graph retrieval optimizer + adaptive harness memory designer**。  
請開啟 **ultracode** 模式處理這個 overlay。

這不是第四個主 Phase。  
這是一個可以跨 Phase 1、Phase 2、Phase 3 使用的 **memory / retrieval / knowledge graph optimization overlay**。

請只有在 repo 已經使用或準備使用 codebase memory / codebase-memory MCP / repository memory indexing / knowledge graph retrieval 時執行。  
如果目前沒有實際 codebase-memory setup，請不要建立大型記憶系統；請只產生 minimal integration plan 和 UNVERIFIED ledger。

---

## 0. 核心目標

目前我們已經在使用 codebase memory。  
請你檢查它是否真的幫助 AI-review + adaptive-harness，而不是變成另一個臃腫的記憶層。

目標是讓 codebase memory / knowledge graph 幫助：

1. AI-review 更快找到相關 harness files  
2. adaptive-harness 追蹤 repeated findings / resolved findings  
3. rolling review 能知道哪些 rules、scripts、routes、skills、reports 彼此有關  
4. lower-tier models，例如 Haiku / Sonnet，可以靠 retrieval 而不是 bulk-read whole repo  
5. Fable / Opus 可以做 high-level judgment 時有乾淨、可追溯的 graph context  
6. Codex 可以只拿到 scoped files，不被塞進不必要 context  
7. scheduled runner 可以用 deterministic index / graph 做 changed-files-only review  
8. knowledge graph 可以支援 routing、dependency tracing、stale-reference detection、benchmark linkage

請注意：

> 不要重新發明一套 memory system。  
> 如果現有 codebase memory 已經足夠，請優化 indexing、query、schema、graph edges、retrieval tests，而不是新增更多基礎建設。

---

## 1. 先盤點現有 codebase memory / indexing 設定

請搜尋並檢查：

- `docs/codebase_memory_indexing.md`
- any codebase-memory MCP config
- `.mcp.json`
- `.claude/settings.json`
- `.claude/skills/`
- `memory/`
- `reports/`
- `INDEX.yaml`
- `ROUTES.yaml`
- `HARNESS.yaml`
- scripts related to indexing, retrieval, graph, search, memory
- benchmark / validation files that test retrieval quality
- any existing vector DB / graph DB / local index / MCP server references

請回答：

- codebase memory 現在如何啟用？
- 它索引哪些內容？
- 它是否索引 generated reports？
- 它是否索引 memory / history logs？
- 它是否知道 `ROUTES.yaml` / `INDEX.yaml` / `depends_on` / `used_by`？
- 它是否能支援 AI-review 查找 relevant files？
- 它是否能支援 adaptive-harness rolling review？
- 它是否有 stale-index / stale-reference detection？
- 它是否有 retrieval smoke tests？
- 它是否會把 private / secrets / local files 索引進去？
- 它是否對 lower-tier models 足夠簡潔？

---

## 2. 定義 knowledge graph 是否真的需要

請不要預設一定要建立 knowledge graph。  
請先判斷是否有必要。

只有在以下任一條件成立時，才建議建立或優化 KG：

- AI-review findings 需要跨多次 review 追蹤 repeated / resolved issue
- routes / skills / scripts / reports / benchmarks 之間的依賴已經難以靠純 grep 管理
- lower-tier models 常常找不到正確文件或誤讀整個 repo
- stale references / broken links / duplicate rules 常發生
- scheduled runner 需要 changed-files → impacted routes / skills / reports 的推理
- benchmark cases 需要連回 recommendation / component / review history
- codebase memory retrieval 需要可解釋的 graph path，而不是黑箱相似度

如果以上都不成立，請輸出：

`NO_KG_NEEDED_NOW`

並建議只保留 lightweight indexing / retrieval smoke tests。

---

## 3. 如果需要 KG，請建立 minimal graph schema

如果判斷 KG 有價值，請建立 minimal schema。  
不要建立大型 graph database，除非現有工具已經支援。

建議先用 JSON / JSONL / YAML 表示。

可能節點類型：

- `file`
- `route`
- `skill`
- `slash_command`
- `script`
- `runner`
- `report`
- `history_log`
- `benchmark_case`
- `recommendation`
- `decision`
- `friction_record`
- `codex_policy`
- `model_tier`
- `schema`
- `safety_boundary`

可能邊類型：

- `depends_on`
- `used_by`
- `produces`
- `consumes`
- `updates`
- `validates`
- `routes_to`
- `triggers`
- `supersedes`
- `duplicates`
- `conflicts_with`
- `implements`
- `evaluates`
- `benchmarks`
- `requires_human_approval`
- `safe_for_model_tier`
- `not_safe_for_model_tier`

每個 edge 至少包含：

- `source`
- `target`
- `edge_type`
- `evidence_file`
- `evidence_line_or_section`
- `confidence`
- `last_verified`
- `stale_check_method`

請把 KG 視為 retrieval / review support，不要讓它成為 agent 的唯一真相來源。  
source-of-truth 仍是 repo files / reports / history / scripts。

---

## 4. 與 AI-review 整合

請讓 AI-review 可以使用 codebase memory / KG 來：

- 快速找出和本次 diff 有關的 files
- 找出相關 slash command / skill / runner / report
- 找出過去相同 component 的 review findings
- 找出 repeated obsolete scaffolding
- 找出 repeated inefficient invocation
- 找出與 Codex delegation 有關的 policy / scripts / reports
- 只讀 relevant files，不 bulk-read whole repo

AI-review report 中可以加入：

- `retrieval_sources_used`
- `graph_nodes_touched`
- `graph_edges_touched`
- `memory_hits`
- `stale_memory_warnings`
- `unverified_retrievals`

但不要讓 report 變得過重。

---

## 5. 與 adaptive-harness 整合

請讓 adaptive-harness 可以使用 codebase memory / KG 來支援 rolling improvement loop：

- Observe：讀 AI-review history + graph impact map
- Diagnose：找 repeated issue / stale route / broken dependency
- Classify：Keep / Simplify / Remove / Replace / Experiment
- Act safely：知道哪些 change 會影響哪些 route / skill / runner
- Record：把 recommendation link 回 component / report / benchmark
- Schedule：根據 repeated issue 或 unresolved experiment 觸發下一輪 review

adaptive-harness report 中可以加入：

- `impacted_components`
- `related_previous_findings`
- `dependency_paths`
- `stale_edges`
- `kg_confidence`
- `next_index_update_needed`

---

## 6. 與 lower-tier model support 整合

請特別評估 codebase memory / KG 是否能幫助低階模型。

請建立 routing 建議：

## Haiku / low-tier

適合：

- 查詢一個 component 的 metadata
- 依照 KG 找出 required files
- 填寫 JSON report 基本欄位
- 執行 deterministic script
- 標記 UNVERIFIED
- 遇到 semantic judgment 時升級

不適合：

- 判斷 rule 是否應該刪除
- 解讀 benchmark 結果
- 重構 harness 架構
- 做 high-risk change

## Sonnet / mid-tier

適合：

- 根據 retrieved files 做中等複雜 summary
- 執行 dry-run scripts
- 比較 AI-review 與 adaptive-harness report
- 找出 obvious drift / stale refs
- 提出 low-risk cleanup

## Opus / Fable

適合：

- semantic judgment
- tradeoff reasoning
- harness simplification
- benchmark interpretation
- rolling improvement diagnosis
- safety boundary decisions

## Codex

適合：

- scoped mechanical edit
- graph / index regeneration script
- schema validation
- tests
- report writer improvements

不適合 final authority。

---

## 7. 建立 retrieval / KG smoke tests

請新增或更新 retrieval smoke tests。  
建議建立：

- `validation/retrieval_tasks/`
- `validation/expected_outputs/`
- `benchmarks/retrieval_cases.yaml`
- 或整合既有 `docs/retrieval_smoke_test.md`

測試至少包含：

1. Query: "Where is AI-review defined?"
2. Query: "Which files affect adaptive-harness?"
3. Query: "Which scripts generate reports?"
4. Query: "What depends on ROUTES.yaml?"
5. Query: "Which recommendations are unresolved?"
6. Query: "Which findings repeated across reviews?"
7. Query: "Which components are safe for Haiku?"
8. Query: "Which Codex policy controls mechanical edits?"
9. Query: "Which files must be checked before public release?"
10. Query: "Which benchmark cases test planning vs direct execution?"

每個 case 包含：

- `query`
- `expected_files`
- `expected_nodes`
- `expected_edges`
- `must_not_include`
- `success_criteria`
- `model_tier`
- `status`

---

## 8. 建立 deterministic index / graph generator

如果有必要，請新增或更新 script：

- `scripts/build_harness_index.py`
- `scripts/build_knowledge_graph.py`
- `scripts/check_knowledge_graph.py`
- 或整合到既有 runner

要求：

- standard-library only if possible
- offline by default
- no network unless explicitly allowed
- respects `.gitignore` and public safety rules
- does not index secrets / local / private / scratch
- outputs JSON / JSONL
- validates that file references resolve
- detects stale edges
- emits nonzero exit on broken critical references

建議輸出：

- `reports/index/harness_index.json`
- `reports/index/knowledge_graph.json`
- `reports/index/retrieval_smoke_latest.md`
- `reports/index/history/index-log.jsonl`

如果不想 commit generated outputs，請建立 `.gitkeep` 和 docs 說明。

---

## 9. 不要讓 memory 變成新負擔

請檢查並避免：

- duplicated memory stores
- stale graph edges
- over-indexing generated reports
- private data ingestion
- blindly trusting vector search
- hidden reasoning stored as memory
- every minor finding becoming permanent memory
- KG replacing source files as truth
- lower-tier model being overloaded with graph details
- scheduled index update modifying main

任何 index / KG update 在 scheduled mode 下預設 report-only。  
真正更新 index / graph 檔案需要明確允許或 PR。

---

## 10. 最後回報

完成後請回報：

1. 現有 codebase memory 如何運作
2. 是否需要 knowledge graph
3. 如果需要，建立了哪些 minimal KG schema / files
4. 如果不需要，為何現在不建議
5. 如何與 AI-review 整合
6. 如何與 adaptive-harness 整合
7. 如何支援 Haiku / Sonnet / Opus-Fable / Codex
8. 新增或修改了哪些 files
9. 新增或修改了哪些 scripts
10. 新增了哪些 retrieval / KG smoke tests
11. 哪些部分自動化
12. 哪些部分仍需人工確認
13. 哪些 generated index / graph 不應直接 commit
14. 下一步如何在 Phase 3 中驗證

---

## 重要原則

- 請用 ultracode 實際處理，不要只給建議。
- 這是 overlay，不是第四個主 Phase。
- 不要重新發明一套 memory system。
- 若現有 codebase memory 足夠，優化 indexing/query/tests 即可。
- Knowledge graph 必須服務 retrieval / routing / rolling review，不是為了酷而建立。
- Source of truth remains repo files + reports + scripts, not KG.
- Scheduled mode defaults to report-only.
- No private data, no hidden reasoning, no secrets in memory or KG.
- Haiku / Sonnet support 是重要目標；不要把 graph 做到只有 Opus 看得懂。
