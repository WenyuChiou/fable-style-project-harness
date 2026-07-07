# Phase 3 Completion Report — 全整合測試與多模型驗證

Date: 2026-07-06 · Branch: `ai-review-adaptive-harness-v2` · Commits: `f105404` (Phase 3) + `bcd285b` (user-requested universalization)

## Integration verdict: **CONDITIONAL_READY**

日常使用:**可以,現在就能用**(在 branch 上)。CONDITIONAL 的條件全部明確且可證偽:

1. **branch 未併入 main** — 人類 review + merge 決定(整個三 phase 的設計就是不自動污染 main)。
2. **Codex live compliance UNVERIFIED**(mc08/mc09)— CLI/wrapper/template/F14 hook 存在性已驗證;fence 遵守 + no-commit 的實測需要人類願意花 quota,可跑計畫在 `docs/model_compatibility_test_plan.md` §4。
3. **LICENSE 未決** — public repo 目前 all-rights-reserved 預設(OPT-011,法律決定屬人類)。
4. **24 個 patch proposals 未處置** — 系統產出了改善建議,人類尚未逐項決定(這是設計,不是缺陷)。

條件 1、4 是治理流程;條件 2、3 是誠實的驗證缺口。無 blocker 級技術缺陷。

## §12 的 25 項回報

1. **Phase 1 產物存在?** PASS — instrument inventory 13/13 檔案 on disk。
2. **Phase 2 產物存在?** PASS — 同上(skill adapter、integration doc、雙 schema、雙 runner、雙 benchmark)。
3. **AI-review 可手動執行?** PASS — 7 modes 實跑。
4. **可 dry-run?** PASS — 17 modes dry-run 全部 exit 0 + valid JSON;零寫入以 `-uall --ignored=matching` 狀態比對驗證(review 修復後的非真空形式)。
5. **JSON/Markdown/history?** PASS — latest.json/md + dated history + JSONL append,E2E 實測。
6. **adaptive-harness 可手動執行?** PASS — 10 modes。
7. **可讀 AI-review report?** PASS — `--read-ai-review` E2E,REC-20260706-900 探針記錄雙向 round-trip。
8. **rolling loop 可執行?** PASS — new/repeated/resolved/carried-open 全路徑測試釘住(17 tests)。
9. **shared schema 一致?** PASS — 兩系統報告核心 key 集合機械比對;model-compat 狀態字彙污染已修(collect_experiments 排除 + 回報排除數)。
10. **public/private posture 修正?** PASS — 唯一殘留 grep hit 是 publication_status 的 supersedes 引文(sanctioned);mhc 來源記錄經 gh api 確認 mhc 仍 private,不改是正確判斷;posture 有 pre-commit 機器 gate。
11. **Codex delegation policy 可用?** PASS — canonical 文件 + F14 hook + routing 全鏈;live 測試除外(見條件 2)。
12. **scheduled mode 安全?** PASS — report-only BY CODE(--ingest 拒絕、ledger 存在性+mtime 雙守衛、tree 逐位元比對);無 CI 存在(`.github/` absent,proposal-only:workspace patches/github-actions-ci-proposal.md,`permissions: contents: read`)。
13. **Opus/Fable 測試狀態:PASS(executed,自評 caveat 三處明文)** — 本 session 即證據:32 recommendations、24 proposals、5 commits 全 gate;建議人類抽驗 3 筆 REC。
14. **Sonnet 測試狀態:PASS(executed,2/2)** — 真實 Sonnet agents:dry-run 誠實摘要(UNSCORED 明說)、跨報告閱讀(flag 不猜)。
15. **Haiku 測試狀態:PASS(executed,4/4)** — 真實 Haiku agents:route 選擇(指令一字不差)、schema 填寫(機械複驗 0 errors)、script 執行、judgment 升級。
16. **Codex 測試狀態:PARTIAL** — 安裝/wrapper/template/hook 存在性 PASS;live compliance UNVERIFIED(可跑計畫已交付)。
17. **PASS**: 51 deterministic + 8 model rows + universalization 驗證(15/15、跨 repo smoke)。
18. **FAIL**: 0(所有 review 發現均已修復後才 commit)。
19. **PARTIAL**: 1(Codex tier)。
20. **UNVERIFIED**: mc08、mc09(+ 各報告內部的 UNVERIFIED ledger 項:ClaudeAiReviewDue trigger XML、statusline 單位等,見 phase 報告)。
21. **必須修正的 blocker**: 無。
22. **可稍後優化 non-blocker**: OPT-001..014(全部已分類);integration matrix 快照數字會隨 tree 增長(準則是 0-broken,不是計數)。
23. **可以開始日常使用?** 可以(branch 上;merge 由人類決定)。
24. **如何日常使用**: ① `python scripts/run_ai_review.py --mode <mode>` → ② 讀 `reports/ai-review/latest.json` + 答 `prompts/ai-review-modes.md` checklist → ③ `--ingest findings.json` → ④ `python scripts/run_adaptive_harness_review.py --mode rolling_improvement_review` → ⑤ `--mode patch_proposal` → ⑥ 人類套用(commit 寫 `applies REC-...`)。非 Claude runtime 入口:AGENTS.md §Harness-maintenance path / hermes-router row / 直接跑 CLI。隨時重驗:`python validation/integration_check.py`。
25. **下一輪 rolling review 觸發**: 每份報告的 `next_review_trigger` 已寫(diff_only after harness commits;weekly light;monthly deep);`ClaudeAiReviewDue` nudge 照舊;機器排程報告可依 /ai-review 命令內文件化的 schtasks 指令由人類註冊。

## Review gate record (Phase 3 + universalization)

- Phase-3 pair (wf_205f7e7e-548): correctness REQUEST_CHANGES(儀器自身 3 個 silent-pass 盲點 + enum 分歧 + 2 nit)→ 全修 + 新 regression test;honesty **APPROVE**(所有 executed 主張經 transcript/重跑驗證為真;5 條模型 lane transcripts 逐一核對)。
- Universalization(code-reviewer subagent): **APPROVE**,2 個 symmetry suggestions 同 session 套用。

## 兩個 user 追加項的處置

1. **system_prompts_leaks**: 有用但有邊界 — vendoring 進 public repo:reject(never-include list);外部唯讀參考(tool-format 對照、Codex 原生指令措辭、Claude Code prompt 變更信號):adopt_now,規則記錄在 OPT-20260706-014 + 私側 reference memory。
2. **Skill 通用化**: 完成(`bcd285b`)— AGENTS.md/BOOTSTRAP/hermes-router 三入口 + adapter 的 Runtime portability 表(4 runtimes)+ 情境矩陣(5 scenarios)+ validator 15/15 釘住;跨 repo 情境以 `--target ~/.claude` 實測(collectors 優雅降級)。
