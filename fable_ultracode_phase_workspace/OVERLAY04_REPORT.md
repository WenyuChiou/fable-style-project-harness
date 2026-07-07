# Overlay 04 Completion Report — Codebase Memory / Knowledge Graph

Date: 2026-07-06 · Branch: `ai-review-adaptive-harness-v2` · Commit: `411dcbe` (6 files, +802/−2)

## §10 回報項目

1. **現有 codebase memory 如何運作**: 兩層並存 — (a) codebase-memory MCP(`.codebase-memory/`,gitignored;CLAUDE.md 定位為 ADVISORY、stale-by-default、需驗證 load-bearing claims;`docs/codebase_memory_indexing.md` 記錄索引方式);(b) repo 自身的顯式圖譜:每檔 frontmatter `depends_on`/`used_by` + INDEX.yaml(134 entries)+ ROUTES.yaml route 成員 + 穩定 ID 系統。generated reports 不被索引(gitignored);memory/ 是 mhc 專案記錄。
2. **是否需要 KG**: **KG_NEEDED — 最小導出式**。不建新記憶系統:顯式圖譜已存在,缺的是全量機械驗證 + reverse-edge impact 查詢 + 低階模型可查的單一 JSON。
3. **建立了什麼**: `scripts/build_harness_graph.py`(147 nodes / 726 edges 導出至 gitignored `reports/index/knowledge_graph.json` + history JSONL;edge 帶 evidence/last_verified/stale_check_method/resolution)+ `graph_impact` collector(diff_only_review、rolling_improvement_review)+ `benchmarks/retrieval_cases.yaml`(10 個 pre-registered 查詢)。
4. **為何不建大系統**: repeated/resolved 追蹤已由 Phase 2 `rolling_state.json` 決定性解決;~160 檔的 repo 用 grep+顯式邊即可;vector DB / graph DB 會違反「不重新發明 memory system」原則。
5. **與 AI-review 整合**: diff → impacted files/routes 讓 review 只讀相關檔案;broken frontmatter deps 成為 P1 deterministic issues(全量覆蓋 — 先前只有 8 個 overlay 檔案被機器驗證,現在 4 種 frontmatter 慣例全解析,含先前隱形的 12 檔/19 條宣告)。
6. **與 adaptive-harness 整合**: `metrics.graph.impacted_components` 進報告;stale routes_to → P2;graph unavailable → P2(不靜默)。
7. **模型層級支援**: 整合文件新增 tier routing 表 — Haiku:跑 deterministic scripts、查 graph/rolling-state JSON、填 schema 欄位、標 UNVERIFIED 後升級;Sonnet:retrieved-files 摘要、drift triage、低風險 cleanup;Opus/Fable:語意判斷、benchmark 解讀、安全邊界;Codex:scoped mechanical(graph regeneration 類),永不做 final authority。
8. **新增/修改 files**: 上列 6 檔(commit 411dcbe)。
9. **新增/修改 scripts**: builder + tests + runner collector 接線。
10. **retrieval / KG smoke tests**: `benchmarks/retrieval_cases.yaml` 10 cases(含 must_not_include、model_tier);`validation/retrieval_probe.py`(Phase 2 已入 repo)11 probes;builder 測試 9/9。
11. **自動化**: 圖導出、全量依賴驗證(exit 1 on broken)、impact 閉包(fixpoint)、混用路徑慣例計量(root-relative=17,OPT-013 記錄)、gitignore 尊重(git ls-files --cached --others --exclude-standard)。
12. **仍需人工**: retrieval_cases 的執行與解讀;OPT-013(慣例統一)決策;MCP 索引更新時機。
13. **不應 commit 的 generated 內容**: `reports/index/*` 全部(已在 `reports/` gitignore 之下)。
14. **Phase 3 驗證方式**: 跑 builder(期望 0 broken)、跑 diff_only_review 檢查 graph collector ok、抽 3 條 edges 對照原始檔、retrieval_cases 抽測、模型層級標記。

## Review gate record

Pair (wf_eb130a7f-1d0): correctness REQUEST_CHANGES(2 blocking + 1 should-fix + 4 nit)、honesty REQUEST_CHANGES(1 blocking + 2 nit;安全主張 a–e 全數機械確認)。Blocking:depth-4 截斷(實際鏈深 7+,8 個 seed 的 impact 集不完整)→ fixpoint;frontmatter 只認 2/4 慣例(12 檔隱形,"full-coverage" 主張為假)→ 4 慣例全解析 + BOM + 多行 inline list。9 項全修 + regression-pinned(builder 測試 6→9),零 skip。
