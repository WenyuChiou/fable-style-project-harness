# Phase 2 Prompt — Adaptive Harness Skill 動態更新系統

你現在是我的 **senior Fable-style adaptive harness architect + AI-review integration engineer + skill system designer**。  
請開啟 **ultracode** 模式處理這個任務。

這是三階段任務的 **Phase 2**。  
本階段目標是把 `WenyuChiou/fable-style-project-harness` 從一次性的 skill / harness template，升級成可以和 Phase 1 的 AI-review 搭配使用、動態持續調整的 **Adaptive Harness Skill System**。

請不要只給建議。  
請實際檢查 repo、修改必要檔案、建立 skill package、整合 AI-review structured output、建立 rolling improvement loop、補上 scripts / reports / benchmarks / tests。

---

## 0. 任務背景

Phase 1 已經或正在優化 AI-review，使它能夠：

- 檢查 prompt / workflow / CLAUDE.md / Codex delegation / tool invocation
- 產生 structured report
- 累積 history
- 建議 Keep / Simplify / Remove / Replace / Experiment
- 設計 benchmark
- scheduled mode report-only

現在 Phase 2 要做的是：

> 建立一個 skill 版的 adaptive harness，讓 AI-review 不只是一次性 review，而是能進入長期滾動式改良 loop。

也就是：

- AI-review = local reviewer  
- Adaptive Harness Skill = 管理 AI-review 如何長期演化、汰換、排程、記錄、benchmark 的 meta-skill

請避免建立兩套互不相通的 review system。

---

## 1. 檢查 Phase 1 的 AI-review 產物

請先檢查 Phase 1 已建立或修改的內容：

- AI-review slash command
- AI-review skill or command
- AI-review runner
- `reports/ai-review/latest.md`
- `reports/ai-review/latest.json`
- `reports/ai-review/history/review-log.jsonl`
- AI-review report schema
- Codex delegation policy
- code/tool invocation review
- benchmark scaffold
- CLAUDE.md pointer-based changes

請判斷：

- 哪些功能應留在 AI-review？
- 哪些功能應上移到 adaptive-harness skill？
- 哪些 schema / checklist / report format 應共用？
- AI-review 是否應呼叫 adaptive-harness？
- adaptive-harness 是否應讀取 AI-review history？
- scheduled review 應由 AI-review runner、adaptive-harness runner，還是共同 runner 負責？

請建立或更新：

- `docs/ai_review_adaptive_harness_integration.md`

---

## 2. 修正 public/private 狀態衝突

目前 repo 已經 public。  
請搜尋並修正所有仍宣稱 repo 必須 private 的內容：

- PRIVATE
- must stay private
- private remote required
- no public remote
- private_until_reviewed
- never make public
- public flip checklist
- private repo setup

請改成 public-safe posture：

- public-safe after human review
- no secrets
- no hidden reasoning
- no private chat exports
- no credentials
- no proprietary/private system prompts
- no private personal data
- public safety review must be repeated before major publication/release

請至少更新：

- `README.md`
- `AGENTS.md`
- `HARNESS.yaml`
- `docs/private_repo_setup.md`

如果需要，請新增或重命名：

- `docs/publication_status.md`
- `docs/public_safety_review.md`
- `SECURITY.md`
- `LICENSE`

不要讓 agent 讀到「repo must stay private」後和 public repo 現實狀態衝突。

---

## 3. 重新定位 repo

請把 repo 定位成：

# Fable-style Adaptive Harness Skill System

它不是：

- prompt collection
- README template
- static skill package
- one-time harness export
- 一次性 AI-review 工具

它應該是：

- skill layer
- routing layer
- AI-review integration layer
- benchmark layer
- report/history layer
- public-safe harness template
- rolling harness maintenance system

請更新 README / docs，讓定位清楚。

---

## 4. 保留現有架構，不要推倒重來

請保留並延伸現有優點：

- `BOOTSTRAP.md`
- `AGENTS.md`
- root-level `SKILL.md`
- `ROUTES.yaml`
- `HARNESS.yaml`
- `context/L0-L5`
- `core/GLOBAL_BOOTSTRAP.md`
- progressive disclosure
- route-specific required / optional file loading
- append-only memory discipline
- completion honesty gate
- agent routing policy
- `scripts/check_agent_artifacts.py`

請在此基礎上補 adaptive loop，不要重寫成普通 prompt dump。

---

## 5. 新增 adaptive-harness skill package

請新增真正的 skill package adapter：

`.claude/skills/adaptive-harness/SKILL.md`

description 要精準，避免太廣泛亂觸發。建議：

Use this skill when auditing, simplifying, benchmarking, or refactoring an AI/agent project harness, including CLAUDE.md, AGENTS.md, slash commands, skills, subagents, hooks, tool routing, scheduled reviews, AI-review reports, benchmark scaffolds, and rolling harness maintenance.

此 skill 至少支援以下 modes：

- `harness_inventory`
- `harness_cleanup_review`
- `code_invocation_review`
- `ai_review_integration`
- `skill_fit_review`
- `diff_only_review`
- `scheduled_harness_review`
- `experiment_design`
- `patch_proposal`
- `rolling_improvement_review`

請說明：

- root `SKILL.md` = repo-level launcher / compatibility entry
- `.claude/skills/adaptive-harness/SKILL.md` = skill-aware runtime 可調用的 adaptive harness skill
- AI-review 可以呼叫 adaptive-harness
- adaptive-harness 可以讀取 AI-review structured output 與 history

---

## 6. 建立 shared schema

請建立或整合共用 schema，使 AI-review 和 adaptive-harness 不會輸出不相容報告。

建議新增：

- `schemas/review_report.schema.json`
- `schemas/recommendation.schema.json`
- 或使用專案既有 schema conventions

共用欄位至少包含：

- `review_id`
- `review_date`
- `source`: ai_review / adaptive_harness / scheduled_runner / manual_review
- `mode`
- `files_inspected`
- `components_inspected`
- `issues_found`
- `obsolete_scaffolding`
- `inefficient_invocations`
- `recommendations`
- `experiments_proposed`
- `changes_made`
- `unresolved_questions`
- `metrics`
- `next_review_trigger`

每個 recommendation 至少包含：

- `recommendation_id`
- `component_name`
- `component_type`
- `file_path`
- `current_purpose`
- `evidence_it_still_helps`
- `evidence_it_may_be_obsolete`
- `recommendation`: Keep / Simplify / Remove / Replace / Experiment
- `expected_impact`
- `risk_if_changed`
- `suggested_test`
- `confidence`
- `priority`
- `source_review_id`

---

## 7. 建立 rolling improvement loop

請設計並實作動態 loop，而不是一次性 review。

loop 應為：

1. Observe
   - 讀取 AI-review latest report
   - 讀取 adaptive-harness history
   - 掃描 changed files / diff
   - 掃描 current harness structure

2. Diagnose
   - 判斷哪些 scaffolding 過時
   - 判斷哪些 invocation 不效率
   - 判斷哪些 prompt / routing / Codex / subagent / script 場景錯配
   - 判斷哪些安全邊界與實際狀態衝突

3. Classify
   - Keep
   - Simplify
   - Remove
   - Replace
   - Merge
   - Cache
   - Experiment

4. Act safely
   - low-risk docs drift → patch proposal or direct edit only if explicitly allowed
   - high-risk harness / routing / permission changes → report / patch proposal only
   - uncertain value → benchmark / A/B test
   - generated metrics → deterministic script
   - semantic judgment → LLM summary

5. Record
   - append to history log
   - update latest report
   - connect findings to previous findings
   - mark repeated issues
   - mark resolved issues

6. Schedule next review
   - diff-only review after harness-related commits
   - weekly light review
   - monthly deep review
   - benchmark review when Experiment remains unresolved

請把此 loop 寫入 skill、docs、runner。

---

## 8. 新增或整合 scripts

請新增或整合：

- `scripts/harness_inventory.py`
- `scripts/invocation_audit.py`
- `scripts/report_writer.py`
- `scripts/run_adaptive_harness_review.py`

若 Phase 1 已有類似 scripts，請共用或重構，不要複製一套平行工具。

`run_adaptive_harness_review.py` 至少支援：

- `--mode harness_inventory`
- `--mode harness_cleanup_review`
- `--mode code_invocation_review`
- `--mode ai_review_integration`
- `--mode scheduled_harness_review`
- `--mode diff_only_review`
- `--mode experiment_design`
- `--mode rolling_improvement_review`
- `--dry-run`
- `--output reports/harness`
- `--read-ai-review reports/ai-review/latest.json`
- `--changed-files-only`
- `--since-ref <git-ref>`

預設：

- scheduled mode = report-only
- 不直接修改 main
- 不 commit
- high-risk changes = patch proposal only

---

## 9. Report / history / memory 整合

請建立或整合：

- `reports/harness/latest.md`
- `reports/harness/latest.json`
- `reports/harness/history/review-log.jsonl`
- `reports/ai-review/latest.md`
- `reports/ai-review/latest.json`
- `reports/ai-review/history/review-log.jsonl`

若 Phase 1 已建立 AI-review reports，adaptive-harness 要讀取它們，而不是另外建立斷裂格式。

每次 rolling review 要記錄：

- review date
- mode
- source reports read
- files inspected
- harness components inspected
- invocation components inspected
- issues found
- obsolete scaffolding found
- inefficient invocation found
- repeated issues from previous reviews
- resolved issues
- recommendations
- experiments proposed
- changes made
- unresolved questions
- total files scanned
- total prompts detected
- total routes detected
- total scripts detected
- total subagents detected
- total code invocations
- review runtime
- dry-run status

---

## 10. AI-review 與 adaptive-harness 分工

請在 `docs/ai_review_adaptive_harness_integration.md` 中明確寫出：

## AI-review 負責

- review current output quality
- review prompt / workflow quality
- review code/tool/Codex invocation efficiency
- detect local harness issues
- produce structured findings
- suggest Keep / Simplify / Remove / Replace / Experiment

## adaptive-harness 負責

- read AI-review history
- detect repeated patterns
- maintain shared schemas
- evolve skill / runner / routing structure
- decide whether to convert checklist into script
- decide whether to benchmark uncertain scaffolding
- produce rolling improvement plan
- keep safety boundaries
- prevent harness bloat
- coordinate scheduled reviews

## deterministic scripts 負責

- file inventory
- path validation
- route validation
- report generation
- history appending
- diff scan
- metrics collection

## LLM 負責

- semantic judgment
- tradeoff reasoning
- prioritization
- deciding whether a rule is still useful
- interpreting benchmark results
- proposing safe refactors

## human 負責

- approving high-risk changes
- deleting prompts / subagents / hooks
- changing permissions
- merging patch proposals
- public release decisions

---

## 11. Benchmark scaffold

請新增或整合：

- `benchmarks/harness_cases.yaml`

至少包含：

- with planning vs direct execution
- with todo vs without todo
- broad scan vs diff-only scan
- root SKILL.md only vs `.claude/skills/adaptive-harness`
- AI-review only vs AI-review + adaptive-harness
- one-time skill review vs rolling improvement loop
- LLM-only report vs script-generated JSON + LLM summary
- current invocation path vs simplified invocation path
- Codex delegation vs main-agent mechanical edit
- subagent vs single-agent
- context reset vs continuous context

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

## 12. 更新 validator / tests

請更新 `scripts/check_agent_artifacts.py` 或新增 validator，檢查：

- public/private posture 不再衝突
- `.claude/skills/adaptive-harness/SKILL.md` exists
- AI-review integration doc exists
- shared report schema exists
- adaptive-harness runner exists
- report/history folders exist
- benchmark scaffold exists
- root `SKILL.md` 與 adaptive skill adapter 的關係有文件說明
- new scripts can run `--help` or dry-run
- scheduled mode defaults to report-only

請更新或新增 tests。

---

## 13. Safety boundary

請強制以下原則：

- scheduled review defaults to dry-run / report-only
- high-risk harness changes produce patch proposal only
- deleting prompts / subagents / hooks requires human approval
- changing permissions requires human approval
- changing `.claude/settings.json` requires human approval
- changing GitHub Actions / CI requires human approval or PR
- no self-modifying skill loop without review
- no direct main mutation from scheduled review
- AI-review findings are recommendations, not automatic commands
- adaptive-harness may propose changes, but human decides what merges

---

## 14. 最後回報

完成後請回報：

1. 你如何把 AI-review 和 adaptive-harness 整合
2. 你修正了哪些 public/private 衝突
3. 你新增或修改了哪些檔案
4. 你是否保留 root `SKILL.md`
5. 你是否新增 `.claude/skills/adaptive-harness/SKILL.md`
6. 你是否建立 shared schema
7. 你是否建立 rolling improvement loop
8. 你是否新增 adaptive harness runner
9. 你是否新增 invocation audit
10. 你是否新增 report/history scaffold
11. 你是否新增 benchmark scaffold
12. 你是否新增 AI-review integration doc
13. 現在如何手動執行 AI-review
14. 現在如何手動執行 adaptive-harness review
15. 現在如何執行 AI-review + adaptive-harness rolling loop
16. 現在如何設定定時執行
17. 哪些部分已自動化
18. 哪些部分仍需要人工確認
19. 哪些 changes 只是 patch proposal，不應直接套用
20. 下一步如何擴展成 research skill suite

---

## 重要原則

- 請用 ultracode 實際處理，不要只給建議。
- 這不是一次性的 skill 專案。
- 這是可以和 AI-review 搭配使用的 dynamic adaptive harness system。
- 不要建立兩套互不相通的 review system。
- 不要把 repo 變成更肥的 prompt collection。
- 優先讓它可執行、可觀察、可測量、可迭代。
- Fable-style 不等於更多規則；Fable-style 是更少無效 scaffolding、更強 routing、更主動驗證、更清楚人類邊界。
- code 做 deterministic work。
- LLM 做 judgment work。
- AI-review 做 local review。
- adaptive-harness 做 rolling system improvement。
- human 保留高風險決策權。
- scheduled runner 預設只產生 report，不直接污染 main。
