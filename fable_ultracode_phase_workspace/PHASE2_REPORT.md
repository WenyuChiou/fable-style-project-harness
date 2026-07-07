# Phase 2 Completion Report — Adaptive Harness Skill System

Date: 2026-07-06 · Branch: `ai-review-adaptive-harness-v2` · Commit: `9a66093` (21 files, +1635/−138)

## Orchestrator-required summary

- **branch name**: `ai-review-adaptive-harness-v2`(沿用 Phase 1)
- **changed files**: `.gitignore`(+.claude local-state ignores)、`AGENTS.md`、`HARNESS.yaml`(v0.2.0 + `public_safe_after_human_review`)、`INDEX.yaml`(+8 entries、2 updated)、`README.md`(重新定位)、`ROUTES.yaml`(+adapter entrypoint)、`SKILL.md`(launcher 關係)、`context/L0_bootstrap.md`、`context/L5_full_context_map.md`、`docs/retrieval_smoke_test.md`(+2 dated records)、`scripts/hooks/pre-commit`(第二道 gate)、`scripts/run_ai_review.py`(shared writer 參數化 + validate_report(known_modes) + stem 防碰撞)
- **new files**: `scripts/run_adaptive_harness_review.py`(10 modes)、`scripts/test_run_adaptive_harness_review.py`(17 tests)、`scripts/check_adaptive_harness.py`(tier-0 posture validator)、`.claude/skills/adaptive-harness/SKILL.md`、`docs/ai_review_adaptive_harness_integration.md`、`docs/publication_status.md`(取代 private_repo_setup.md)、`benchmarks/harness_cases.yaml`、`validation/retrieval_probe.py`
- **commands run**: 兩套測試(standalone+pytest)、雙 validator、`validation/retrieval_probe.py`、真實 E2E loop(ai-review ingest → rolling → patch_proposal)、gh api visibility 驗證、tree-diff 零寫入驗證(由 review lens 執行)
- **tests run**: 17/17 adaptive + 21/21 ai-review;雙 tier-0 validator exit 0;probes 11/11(131 INDEX entries、0 ghosts)
- **reports generated**: `reports/harness/latest.{json,md}` + history + `rolling_state.json`(37 recs)+ `proposals/PATCH-PROPOSALS-2026-07-06.md`(24 個 high-risk 項,含 apply/rollback 約定)— 全部 gitignored
- **unresolved issues**: OPT-20260706-011(LICENSE 未決,human legal call)、OPT-012(全史 secret scan 未跑)、OPT-001(orchestration_bench INDEX 31 檔)
- **high-risk changes requiring human approval**: 無直接套用;24 個 patch proposals 等待人類逐項決定(P0 首位:cbm-session-reminder 指令衝突)
- **next phase readiness**: **READY**(overlay 04 評估先行,Phase 3 隨後)

## Phase-2 prompt final-report items (§14, 20 項)

1. **整合方式**: 一套系統、兩個 runner、共用 schemas。adaptive runner 以 importlib 匯入 Phase-1 引擎(collectors/validators/writers 零複製);耦合走報告檔案(`--read-ai-review`),process 層彼此獨立,任一模型層級都能單獨呼叫。
2. **public/private 衝突修正**: repo 經 GitHub API 驗證為 PUBLIC;`private_repo_setup.md`→`publication_status.md`(誠實記錄:LICENSE 未決、全史 secret scan 未驗);README/AGENTS/SKILL/HARNESS/L0/L5/INDEX/.gitignore 全數 clean-break;**mhc 來源專案的 "private" 記錄刻意保留**(reviewer 以 gh api 獨立確認 mhc 仍 private,改了反而是偽造 provenance)。
3. **新增/修改檔案**: 上表。
4. **保留 root SKILL.md?** 是 — 並明文寫出 launcher(mhc 工作)vs adapter(harness 維護)的分工。
5. **新增 adapter?** 是 — `.claude/skills/adaptive-harness/SKILL.md`,10 modes,description 窄化防誤觸發。
6. **shared schema?** 是 — Phase 1 已建,Phase 2 直接沿用(零 fork);`validate_report` 增加 `known_modes` 參數消除字串耦合。
7. **rolling improvement loop?** 是 — Observe→Diagnose→Classify→Act-safely→Record→Schedule 寫入 skill+docs+runner;`rolling_state.json` 專屬記憶(guarded write:corrupt state 或 input 缺失時保留記憶並升 P1 issue,絕不靜默重置)。
8. **adaptive runner?** 是(10 modes + `--read-ai-review/--dry-run/--ingest/--changed-files-only/--since-ref`)。
9. **invocation audit?** 是 — `code_invocation_review` mode(共用引擎;獨立 `invocation_audit.py` 刻意不建,見整合文件 Design decision 3)。
10. **report/history scaffold?** 是 — `reports/harness/`,與 ai-review 同構。
11. **benchmark scaffold?** 是 — `harness_cases.yaml` 5 cases(與 ai_review_cases 明確不重複)。
12. **integration doc?** 是。
13. **手動執行 AI-review**: `python scripts/run_ai_review.py --mode <7 modes>` → 語意 checklist → `--ingest`。
14. **手動執行 adaptive review**: `python scripts/run_adaptive_harness_review.py --mode <10 modes>`。
15. **rolling loop**: ai-review ingest run → `--mode rolling_improvement_review` → `--mode patch_proposal` → 人類套用(commit 寫 `applies REC-...`)→ 下輪自動標 resolved。
16. **定時執行**: 既有 `ClaudeAiReviewDue` nudge 不動;機器報告可另註冊 schtasks 跑 `scheduled_review`/`scheduled_harness_review`(文件化指令,人類註冊,report-only by code)。
17. **已自動化**: 全部 deterministic collectors、rolling 連結(new/repeated/resolved/carried-open)、resolved-by-commit(application-verb grep)、patch-proposal 渲染、posture gate(pre-commit)、schema 驗證、JSON→MD、history。
18. **仍需人工**: 語意判斷、proposals 套用、LICENSE、secret scan、benchmark 執行決定、所有 hooks/permissions/settings/CI 變更。
19. **只是 patch proposal 不可直接套用**: `reports/harness/proposals/PATCH-PROPOSALS-2026-07-06.md` 全部 24 項(每項含 evidence 兩面、驗證測試、apply 動詞約定、rollback 約定);外加 OPT-001..012 中標 patch_proposal 者。
20. **research skill suite 擴展**: 記錄於 99 檔案 standing questions — 現有 modes 天生可參數化(`--target` 任意 repo);把 per-domain checklist(如 research repo 的 silent-failure 模式)做成 `prompts/` 下的 mode 變體 + 各自 benchmark case,是 defer 狀態的自然下一步,不在本輪 scope。

## Long-term qualities

- **Maintainability**: 引擎單一來源(importlib 共用);posture 有機器 gate 防回歸;修 reviewer 發現的 16 項全部以 regression test 釘住(17 tests vs 初版 11)。
- **Observability**: rolling metrics(new/repeated/resolved/carried-open)+ 全套 totals(prompts/routes/scripts/subagents/invocations)每 run 記錄。
- **Traceability**: REC-id 貫穿 finding→rolling state→patch proposal→applying commit(`applies REC-...` 動詞約定,拒絕 bare mention/revert 誤判)→resolved。
- **Rollback safety**: 高風險項只到 proposal sheet;每張 proposal 內建 rollback 約定;posture 改動單 commit 可 revert;`9a66093` 原子。

## Review gate record

Adversarial pair (wf_5aff4270-863): correctness REQUEST_CHANGES(11 findings)+ posture/gate-honesty REQUEST_CHANGES(5 findings)。重大者:corrupted rolling_state 靜默重置迴圈記憶、AI-review input 缺失時 rolling_state 被空表覆蓋(部分推翻 carried-open 主張)、dogfood 中實際發生的同秒 history 覆蓋(6 runs 只剩 4 檔)、resolved-by-commit 對 bare-mention/reject/revert 的誤判。**16/16 全修 + regression-pinned,零 skip**;posture 主張 (a)(b)(c)(d) 機械驗證成立,我方 7 個數字全數被獨立複核確認。
