# Phase 1 Completion Report — AI-review 大優化

Date: 2026-07-06 · Branch: `ai-review-adaptive-harness-v2` · Commits: repo `f55459d`, ~/.claude `9caaf65`

## Orchestrator-required summary

- **branch name**: `ai-review-adaptive-harness-v2` (created from clean `main`; working tree had only the untracked `fable_ultracode_phase_workspace/`, preserved untracked)
- **changed files (repo)**: `.gitignore` (+`reports/` ignore block), `INDEX.yaml` (+7 entries), `docs/retrieval_smoke_test.md` (+dated probe record)
- **new files (repo)**: `scripts/run_ai_review.py`, `scripts/test_run_ai_review.py`, `schemas/review_report.schema.yaml`, `schemas/recommendation.schema.yaml`, `prompts/ai-review-modes.md`, `docs/codex-delegation-policy.md`, `benchmarks/ai_review_cases.yaml`
- **changed files (~/.claude, git-tracked dotfiles)**: `commands/ai-review.md` — ONE additive section (37 insertions, zero removals); patch record at `fable_ultracode_phase_workspace/patches/ai-review-command-upgrade.patch`; revert = `git -C ~/.claude revert 9caaf65`
- **workspace artifacts (untracked, user-owned)**: `phase1_findings.json` (REC-20260706-001..032 + 16 invocation findings), `99_OPEN_OPTIMIZATION_SPACE.md` (+10 OPT entries), this report
- **commands run**: `python scripts/test_run_ai_review.py` · `python -m pytest scripts/test_run_ai_review.py` · `python scripts/check_agent_artifacts.py` · all 7 runner modes for real (`--ingest` on harness_cleanup) + `--dry-run --no-home` hermetic passes · scripted retrieval smoke probe · explicit-path staging with count assertions (10 asserted / 1 asserted)
- **tests run**: 21/21 pass (standalone AND pytest); pre-commit validator green
- **reports generated**: `reports/ai-review/latest.{json,md}` + `history/review-log.jsonl` (8 runs logged) + dated history files — all local-only (gitignored by design, see High-risk/OPT-009)
- **unresolved issues**: (1) OPT-20260706-001 — 31 pre-existing unregistered `distillation/orchestration_bench/` files, machine-flagged every run, awaiting register-vs-exempt decision; (2) UNVERIFIED items carried in the report's `unresolved_questions` (ClaudeAiReviewDue task trigger XML not dumped; hooks-dir git coverage for .bak deletion; statusline refresh units); (3) one synthetic `audit-probe` telemetry line in `~/.claude/logs/hook_events.jsonl:10769` left in place (never-edit-captured-evidence) — inert, disclosed
- **high-risk changes requiring human approval (NONE applied — all patch proposals)**: OPT-002/003 hook merges, OPT-004 statusline removal, OPT-005 cbm hook text fix, OPT-007 CLAUDE.md slim (benchmark_first, gated on claude_md_eval), OPT-010 telemetry rotation. CLAUDE.md itself was NOT edited.
- **next phase readiness**: **READY**

## Phase-1 prompt final-report items (§11)

1. **現有 AI-review 在哪裡**: `~/.claude/commands/ai-review.md` (242→279 行) + 8 個 `~/.claude/scripts/*` 決定性腳本 + `check_ai_review_due.py` SessionStart nudge + `ClaudeAiReviewDue` Windows 排程(只寫 due-flag)+ `~/.claude/audits/`(6 份週報、proposals.jsonl 75 rows: 42 applied/18 proposed/15 rejected)。
2. **最大問題**: 組合邏輯全在 LLM prose(無 runner/modes/JSON report/run-history);報告數字由 LLM 手寫(DR-004 風險);無 diff-scoping;`scheduled` 概念與「passive cron 會爛」教義未調和。全部已在本 phase 解決或以教義相容方式界定。
3. **CLAUDE.md 過時/重複 scaffolding**(見 REC-001..015): P0 — cbm-session-reminder hook 與 CLAUDE.md §Code Exploration 每個 session 注入互相矛盾的指令;P1 — 雙 review-gate 章節佔 43% 檔案、~70% trigger 重疊;檔案數門檻四處不一致(≥2/≥3/50-LOC-only);Gemini 殘留 45 行/16 個 tombstone;AGENTS.md 高估機器強制(rm/git merge 不在 deny list);DELEGATION.md REJECT 路徑指示被 deny-list 擋掉的 `git checkout --`。
4. **Codex 指派效率問題**(REC-016..025): 政策異常完善(F14 blocking hook 有 telemetry:27 blocks);主要問題是 tripwire 門檻漂移(≥3 vs ≥5)、CLAUDE.md:79 仍把 governance/root-cause 導向 Codex(與 routing table 衝突)、gemini 殘留、Codex-不可-commit 只有 prose 無機械 gate(已列為 benchmark case)。
5. **新增/修改檔案**: 上表。
6. **保留原本 slash command?** 是 — `/ai-review` 與 weekly/monthly/quarterly tier 全保留,只增加 modes/runner 區段(additive)。
7. **新增 runner?** 是 — `scripts/run_ai_review.py`,7 modes + `--dry-run/--output/--changed-files-only/--since-ref/--ingest/--no-home`。
8. **Codex delegation policy?** 是 — `docs/codex-delegation-policy.md`(canonical;CLAUDE.md 未加肥,command 指向它;CLAUDE.md pointer 一行列為 patch proposal)。
9. **structured report?** 是 — JSON+MD 雙生,schema 驗證後才寫。
10. **history log?** 是 — `reports/ai-review/history/review-log.jsonl` + dated 檔案。
11. **benchmark scaffold?** 是 — 8 cases 全部 pre-registered、連結 REC id、標注 Opus ceiling 風險。
12. **手動執行**: `python scripts/run_ai_review.py --mode <mode>` → 讀 latest.json → 依 `prompts/ai-review-modes.md` 作答 → `--ingest findings.json`。
13. **定時執行**: 已存在的 `ClaudeAiReviewDue`(nudge)+ 文件化的 `schtasks /create ... --mode scheduled_review`(人類自行註冊,絕不自動)。
14. **已自動化**: inventory、INDEX↔disk 漂移(新增的機器覆蓋)、ROUTES 完整性、deprecated/bak/TODO 掃描、diff scoping、telemetry 收割、schema 驗證、JSON→MD 渲染、history append。
15. **仍需人工**: 全部語意判斷(checklists)、findings 的採納、高風險變更(hooks/permissions/settings/CI/刪除任何 prompt/subagent)、排程註冊、ledger 處置。
16. **Keep/Simplify/Remove/Replace/Experiment**: 32 recommendations + 16 invocation findings,全in `phase1_findings.json` 且已 ingest 至報告;十大可行動項歸檔為 OPT-20260706-001..010(含分類)。
17. **Phase 2 如何讀取**: `run_adaptive_harness_review.py --read-ai-review reports/ai-review/latest.json`;shared schemas(`review_report` + `recommendation`)已內建 `source: adaptive_harness` 與 rolling-loop 欄位(`status: open/repeated/resolved/...`、`linked_benchmark_case`)— Phase 2 直接沿用,不另起格式。

## Long-term qualities (how this phase moved them)

- **Maintainability**: 判斷邏輯集中在 1 個 prompts 檔 + 1 個 policy 檔(指標式引用);runner 純 stdlib、複用既有腳本(DR-020),零新依賴;CLAUDE.md 零增肥。
- **Observability**: 每 run 都有 JSON+MD+JSONL row(runtime、collector 狀態、計數);deterministic issues 有類別與嚴重度。
- **Traceability**: recommendation_id ↔ source_review_id ↔ linked_benchmark_case ↔ OPT 條目 ↔ commit trailers 全鏈路;佐證都到 file:line。
- **Rollback safety**: 兩個 commit 都是原子的、可單獨 revert;高風險項全部停在 patch proposal;runner 從不寫 harness 檔案(review pair 以 tree-diff 機械驗證)。

## Review gate record

Adversarial pair (wf_2f34c64b-f2a): correctness lens REQUEST_CHANGES(1 blocking+3 should-fix+2 nit)、gate-honesty lens REQUEST_CHANGES(4 should-fix+2 nit;安全主張 a/b/d/e/g 機械驗證成立;我方數字 4/4 被複核確認)。9 個獨立 finding 全部修復並以 regression test 釘住(21 tests vs 原 13),零 skipped。修復後才 commit。
