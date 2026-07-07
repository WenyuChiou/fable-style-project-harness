# Phase 1 Prompt — AI-review 大優化與 Codex/Tool 調用效率審查

你現在是我的 **senior AI-review system architect + Claude Code harness optimizer + Codex delegation efficiency reviewer**。  
請開啟 **ultracode** 模式處理這個任務。

這是三階段任務的 **Phase 1**。  
本階段只聚焦在我現有專案中的 **AI-review slash command / AI-review workflow / CLAUDE.md / Codex delegation / tool-code invocation efficiency**。

請不要只給建議。  
請實際檢查 repo、修改必要檔案、建立可執行 runner、更新文件、補上 minimal tests，並輸出可驗證結果。

---

## 0. 任務背景

我目前已經有一套 **AI-review slash command**，但它現在主要是手動觸發。  
我想把它升級成一個可以：

1. 手動執行  
2. 定期自動執行  
3. 累積 review history  
4. 檢查 prompt / workflow / CLAUDE.md / slash command / subagent / context reset 是否過時  
5. 檢查 code / tool / script / Codex / subagent 調用效率  
6. 產生 structured report  
7. 設計 A/B test 或 benchmark  
8. 但不直接污染 main branch  

的 **AI-review maintenance loop**。

核心問題是：

> 有什麼是我現在可以停止做的？  
> 哪些 prompt、workflow、todo、planning、context reset、subagent、tool format、Codex delegation、script invocation 已經不再提高成功率，反而拖慢模型、增加 token 成本、增加合併成本或增加維護負擔？

---

## 1. 盤點現有 AI-review 與 Claude Code harness

請先搜尋 repo 中所有與以下內容相關的檔案：

- AI-review slash command
- `.claude/commands/`
- `.claude/skills/`
- `.claude/agents/`
- `.claude/hooks/`
- `.claude/settings.json`
- `CLAUDE.md`
- `AGENTS.md`
- `prompts/`
- `scripts/`
- `tools/`
- `src/`
- `docs/`
- GitHub Actions / CI
- Codex delegation prompt / Codex task brief / codex workflow
- any planner / todo / context reset / handoff / subagent / tool schema / workflow files

請建立 inventory report，回答：

- 現有 AI-review 在哪裡？
- 它目前做什麼？
- 是否只能手動執行？
- 是否可以被 CLI、script、CI、cron 或 scheduled task 呼叫？
- 是否會產生 report？
- 是否會留下 history？
- 是否會修改檔案？
- 是否依賴 subagent、todo、planning、context reset、handoff？
- CLAUDE.md 是否有過度規則、重複規則、過時規則？
- CLAUDE.md 是否清楚規定何時要指派 Codex？
- Codex 目前是否被用在正確場景？
- 哪些地方像是舊模型時代留下的 scaffolding？

---

## 2. 保留 slash command，但升級成可排程 workflow

請盡量保留我原本的使用習慣，例如 `/ai-review`。  
但請把它升級成更模組化、可重複執行、可排程、可輸出 structured data 的 workflow。

新的 AI-review 至少支援以下 mode：

- `standard_review`：一般品質檢查
- `harness_cleanup_review`：檢查 prompt、CLAUDE.md、todo、subagent、context reset、handoff、hook、tool format 是否過時
- `code_invocation_review`：檢查 code / tool / script / subagent 調用效率
- `codex_delegation_review`：檢查 CLAUDE.md 與 workflow 中 Codex 指派是否正確、過度或不足
- `scheduled_review`：定時任務使用，少互動，輸出 structured report
- `diff_review`：只檢查最近變更
- `experiment_review`：針對不確定是否該移除的 harness 或 invocation 設計 A/B test

---

## 3. CLAUDE.md 與 Codex 指派效率審查

請特別檢查 `CLAUDE.md` 或等效 agent instruction file。

請回答：

1. CLAUDE.md 是否太長、太硬、太像舊模型補丁？
2. 哪些規則是必要的 safety / correctness boundary？
3. 哪些規則只是慣性保留？
4. 是否有規則互相衝突？
5. 是否有重複要求 plan / todo / self-check，導致延遲與 token 浪費？
6. 是否清楚規定何時使用 Codex？
7. Codex 是否被錯誤用在需要 high-level judgment 的任務？
8. Codex 是否沒有被用在它適合的 mechanical multi-file work？
9. Codex task brief 是否有固定格式？
10. Codex 回傳結果是否必須被 Claude Code / Fabo review，而不是直接當 final authority？
11. 是否可以把 Codex 指派決策寫成簡單 routing rule？

請建立或更新一份 **Codex delegation policy**，至少包含：

- Codex 適合：
  - mechanical multi-file edits
  - boilerplate generation
  - stable-pattern refactor
  - test skeleton creation
  - deterministic migration
  - clear acceptance criteria tasks
- Codex 不適合：
  - architecture judgment
  - ambiguous root cause
  - research direction
  - safety / permission / governance decisions
  - final verification authority
  - release / done claim
- Codex 必須：
  - brief-first
  - allowed-files 明確
  - out-of-scope 明確
  - acceptance criteria 明確
  - verification commands 明確
  - 不 commit，除非明確要求
  - 回傳 diff 後由 Claude Code / Fabo review

請把這份政策整合進 AI-review 或 CLAUDE.md，但不要讓 CLAUDE.md 變成更肥。必要時把長內容放到 docs 或 skill reference，CLAUDE.md 只保留 pointer。

---

## 4. Harness cleanup checklist

請把以下問題整合進 AI-review：

1. 這條 prompt 約束還在提高成功率嗎，還是只是慣性留著？
2. 這個強制 planning / todo 步驟還在防止模型偏離任務嗎，還是只是拖慢它？
3. 這個 context reset 或 handoff 還在避免錯誤嗎，還是已經打斷模型長程推理？
4. 這個 subagent 真的提高品質嗎，還是只增加合併成本？
5. 這個 tool format 還是目前模型最熟、最穩定、最有效的格式嗎？
6. 這個 Codex delegation 是否真的節省主 agent 成本，還是增加 merge/review overhead？
7. 有沒有任何規則只是為了舊模型、舊限制、舊錯誤而存在？
8. 有沒有規則重複、互相衝突、過度保守，或讓模型無法自然完成任務？
9. 哪些東西應該 Keep / Simplify / Remove / Replace / Experiment？

每個 finding 至少包含：

- `component_name`
- `component_type`
- `file_path`
- `current_purpose`
- `evidence_it_still_helps`
- `evidence_it_may_be_obsolete`
- `recommendation`: Keep / Simplify / Remove / Replace / Experiment
- `expected_impact`
- `risk_if_removed`
- `suggested_test`
- `confidence`
- `priority`

---

## 5. Code / tool / script / subagent / Codex invocation efficiency review

請建立固定的 invocation audit。

每個 invocation finding 至少包含：

- `invocation_name`
- `invocation_type`: script / shell command / tool / subagent / Codex / LLM-only / hybrid
- `current_usage_scenario`
- `value_provided`
- `likely_cost`: latency / token / tool calls / merge overhead / review burden
- `can_be_merged`
- `can_be_replaced_by_deterministic_code`
- `can_be_replaced_by_LLM_reasoning`
- `should_be_cached`
- `should_be_removed`
- `recommendation`: Keep / Simplify / Merge / Replace / Cache / Remove / Experiment
- `expected_efficiency_gain`
- `risk_if_changed`
- `suggested_test`

請特別檢查：

- 是否每次都大範圍掃 repo？
- 是否可以改為 changed-files-only 或 diff-only scan？
- 是否有 repeated file reads？
- 是否有重複 tool calls？
- 是否有可以 deterministic script 化的檢查？
- 是否有不該用 Codex 卻指派 Codex 的任務？
- 是否有應該用 Codex 卻全部讓主 agent 做的 mechanical work？
- 是否有 subagent 只是增加合併成本？
- 是否 report generation 可以改成 JSON → Markdown，而不是每次 LLM 從零寫？

---

## 6. Structured report 與 shared schema

請讓 AI-review 輸出固定格式。至少支援：

- Markdown report
- JSON report
- JSONL history

建議輸出位置：

- `reports/ai-review/latest.md`
- `reports/ai-review/latest.json`
- `reports/ai-review/history/review-log.jsonl`
- `reports/ai-review/history/YYYY-MM-DD-ai-review.md`
- `reports/ai-review/history/YYYY-MM-DD-ai-review.json`

共用欄位至少包含：

- `review_id`
- `review_date`
- `source`: ai_review
- `mode`
- `files_inspected`
- `components_inspected`
- `issues_found`
- `obsolete_scaffolding`
- `inefficient_invocations`
- `codex_delegation_findings`
- `recommendations`
- `experiments_proposed`
- `changes_made`
- `unresolved_questions`
- `metrics`
- `next_review_trigger`

---

## 7. 新增 runner

請新增或修改 runner：

- `scripts/run_ai_review.py`

runner 至少支援：

- `--mode standard_review`
- `--mode harness_cleanup_review`
- `--mode code_invocation_review`
- `--mode codex_delegation_review`
- `--mode scheduled_review`
- `--mode diff_review`
- `--mode experiment_review`
- `--dry-run`
- `--output reports/ai-review`
- `--changed-files-only`
- `--since-ref <git-ref>`

預設：

- scheduled mode = report-only
- dry-run 不修改檔案
- 不直接 commit
- 不直接改 main

---

## 8. Benchmark / A-B test scaffold

請新增或更新：

- `benchmarks/ai_review_cases.yaml`

至少包含：

- with planning vs direct execution
- with todo vs without todo
- broad repo scan vs diff-only scan
- subagent vs single-agent
- Codex delegation vs main-agent mechanical edit
- Codex with brief vs Codex without brief
- LLM-only report vs script-generated JSON + LLM summary
- old CLAUDE.md rule set vs simplified CLAUDE.md pointer-based rule set

每個 case 包含：

- `case_name`
- `task_type`
- `variant_a`
- `variant_b`
- `expected_metrics`
- `success_criteria`
- `manual_review_notes`
- `status`: proposed / running / completed / rejected
- `linked_recommendation_id`

---

## 9. Safety boundary

請強制以下原則：

- AI-review findings are recommendations, not automatic commands.
- scheduled review defaults to dry-run / report-only.
- high-risk harness changes produce patch proposal only.
- deleting prompts / subagents / hooks requires human approval.
- changing permissions requires human approval.
- changing `.claude/settings.json` requires human approval.
- changing GitHub Actions / CI requires human approval or PR.
- Codex must not commit unless explicitly asked.
- Codex output must be reviewed by Claude Code / Fabo before shipping.
- no direct main mutation from scheduled review.

---

## 10. 測試與驗證

請新增或更新 tests，至少確認：

- AI-review runner `--help` 可以執行
- `--mode harness_cleanup_review --dry-run` 可以產生 report
- `--mode code_invocation_review --dry-run` 可以產生 report
- `--mode codex_delegation_review --dry-run` 可以產生 report
- latest Markdown / JSON report 可產生
- history JSONL 可 append
- dry-run 不修改 repo
- scheduled mode 預設 report-only
- Codex delegation policy 存在且被 AI-review 引用
- CLAUDE.md 不變成過長 rule dump，而是 pointer-based

---

## 11. 最後回報

完成後請回報：

1. 現有 AI-review 在哪裡
2. 目前 AI-review 最大問題
3. CLAUDE.md 有哪些過時或重複 scaffolding
4. Codex 指派效率有哪些問題
5. 你新增或修改了哪些檔案
6. 你是否保留原本 slash command
7. 你是否新增 runner
8. 你是否新增 Codex delegation policy
9. 你是否新增 structured report
10. 你是否新增 history log
11. 你是否新增 benchmark scaffold
12. 如何手動執行
13. 如何定時執行
14. 哪些部分已自動化
15. 哪些部分仍需人工確認
16. 哪些項目建議 Keep / Simplify / Remove / Replace / Experiment
17. 下一階段 adaptive-harness skill 應如何讀取 AI-review 的結果

---

## 重要原則

- 請用 ultracode 實際處理，不要只給建議。
- 不要把系統變成更肥的 prompt collection。
- 優先簡化、刪除、合併、實驗驗證。
- CLAUDE.md 應該 pointer-based，不要塞滿長規則。
- Codex 做 mechanical scoped work。
- Claude Code / Fabo 做 judgment、review、integration。
- AI-review 做 local review 與 structured findings。
- scheduled runner 預設只產生 report，不直接污染 main。
