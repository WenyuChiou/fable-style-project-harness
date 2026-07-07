# Phase 3 Prompt — AI-review + Adaptive Harness Skill 全整合測試與多模型驗證

你現在是我的 **senior integration test architect + model-compatibility evaluator + Fable-style harness validation lead**。  
請開啟 **ultracode** 模式處理這個任務。

這是三階段任務的 **Phase 3**。  
只有在 Phase 1（AI-review 大優化）和 Phase 2（Adaptive Harness Skill 動態更新系統）都完成後，才執行本階段。

本階段目標不是再新增功能，而是 **真正測試整套 AI-review + adaptive-harness skill system 是否能被使用、能穩定執行、能被不同等級模型理解與操作**。

需要測試的模型層級至少包含：

- Opus / Fable / highest reasoning model
- Sonnet / mid-tier model
- Haiku / low-tier or cheaper model
- Codex or code-execution-oriented agent, if available

如果實際 runtime 沒有某些模型可用，請不要假裝完成。  
請建立可重現的 manual test plan、標記 UNVERIFIED，並輸出缺口清單。

---

## 0. 任務背景

Phase 1 應已建立或優化：

- AI-review slash command
- AI-review runner
- harness cleanup review
- code invocation review
- Codex delegation review
- structured reports
- history log
- benchmark scaffold
- CLAUDE.md / Codex delegation efficiency policy

Phase 2 應已建立或優化：

- `.claude/skills/adaptive-harness/SKILL.md`
- adaptive harness rolling improvement loop
- AI-review integration
- shared schema
- reports/harness
- invocation audit
- benchmark scaffold
- public-safe posture cleanup
- validator / tests

Phase 3 要確認：

> 這整套系統不是只有文件存在，而是真的可以被不同能力等級的模型使用。

---

## 1. 先做 repo state inventory

請先檢查 repo 目前狀態：

- 是否有 AI-review command / skill
- 是否有 adaptive-harness skill
- 是否有 root `SKILL.md`
- 是否有 `.claude/skills/adaptive-harness/SKILL.md`
- 是否有 AI-review runner
- 是否有 adaptive-harness runner
- 是否有 shared schema
- 是否有 report folders
- 是否有 history logs
- 是否有 benchmark cases
- 是否有 Codex delegation policy
- 是否有 integration doc
- 是否有 public-safe docs
- 是否有 validators / tests
- 是否有 GitHub Actions or scheduled workflow

請輸出 inventory table，標記：

- PASS
- FAIL
- PARTIAL
- UNVERIFIED

---

## 2. 驗證 public/private posture

請檢查是否仍存在矛盾文字：

- PRIVATE
- must stay private
- private remote required
- no public remote
- private_until_reviewed
- never make public

如果這些文字仍存在，請判斷是：

- legitimate historical note
- obsolete contradiction
- safety policy still valid
- needs rewrite

請不要只 grep 後報數字，要打開語境判斷。  
最後輸出：

- remaining private-related references
- whether each is acceptable
- required fixes

---

## 3. 驗證 CLI / script 可用性

請實際執行或設計可重現指令，至少檢查：

```bash
python scripts/run_ai_review.py --help
python scripts/run_ai_review.py --mode harness_cleanup_review --dry-run
python scripts/run_ai_review.py --mode code_invocation_review --dry-run
python scripts/run_ai_review.py --mode codex_delegation_review --dry-run
python scripts/run_adaptive_harness_review.py --help
python scripts/run_adaptive_harness_review.py --mode harness_inventory --dry-run
python scripts/run_adaptive_harness_review.py --mode ai_review_integration --read-ai-review reports/ai-review/latest.json --dry-run
python scripts/run_adaptive_harness_review.py --mode rolling_improvement_review --dry-run
python scripts/check_agent_artifacts.py
```

如果任何 script 不存在，請標記 FAIL。  
如果 script 存在但不能跑，請修正。  
如果不能修正，請明確輸出原因與最小 patch proposal。

請確認：

- commands exit 0 where expected
- failures are meaningful, not silent
- dry-run does not modify files
- reports can be generated
- JSON is valid
- Markdown report is generated from structured data
- history JSONL can append
- scheduled mode defaults to report-only

---

## 4. 驗證 AI-review + adaptive-harness 資料流

請測試完整資料流：

1. Run AI-review dry-run
2. Confirm `reports/ai-review/latest.json` exists
3. Confirm `reports/ai-review/latest.md` exists
4. Confirm AI-review history log appended
5. Run adaptive-harness with `--read-ai-review reports/ai-review/latest.json`
6. Confirm adaptive-harness reads AI-review findings
7. Confirm adaptive-harness produces `reports/harness/latest.json`
8. Confirm adaptive-harness produces `reports/harness/latest.md`
9. Confirm adaptive-harness history log appended
10. Confirm recommendations can link back to source AI-review IDs

請特別檢查：

- AI-review 與 adaptive-harness 是否真的共用 schema
- 是否出現兩套互不相通的 report format
- adaptive-harness 是否能讀取 AI-review output
- AI-review 是否知道 adaptive-harness 的角色
- history 是否可追蹤 repeated / resolved issue

---

## 5. 驗證 skill activation 與文件路由

請測試或模擬以下入口：

- root `SKILL.md`
- `.claude/skills/adaptive-harness/SKILL.md`
- `AGENTS.md`
- `BOOTSTRAP.md`
- `core/GLOBAL_BOOTSTRAP.md`
- AI-review slash command
- harness-review slash command, if any

請檢查：

- 入口不互相矛盾
- root `SKILL.md` 和 adaptive skill adapter 關係清楚
- 非 method-harness-compiler 專案不會錯讀 project-bound phase files
- adaptive-harness skill description 不會太廣，避免每個任務亂觸發
- AI-review 可以作為 local review
- adaptive-harness 可以作為 rolling improvement layer
- lower-tier model 是否能靠 minimal entry 正確找到下一步

---

## 6. 多模型可用性測試設計

請建立或執行多模型測試。至少測以下能力層級：

## 6.1 Opus / Fable / highest reasoning model

測試它是否能：

- 完整理解 AI-review + adaptive-harness 分工
- 做 semantic judgment
- 判斷 Keep / Simplify / Remove / Replace / Experiment
- 解讀 history
- 設計 benchmark
- 不過度新增 scaffolding
- 不直接改 main
- 產生 patch proposal

## 6.2 Sonnet / mid-tier model

測試它是否能：

- 依照 route 和 skill instructions 正確執行
- 跑 dry-run scripts
- 讀 structured reports
- 產生 reasonable summary
- 不 bulk-read whole repo
- 不跳過 safety boundary
- 在不確定時標記 UNVERIFIED

## 6.3 Haiku / lower-tier model

測試它是否能：

- 讀 minimal entrypoint
- 選對 mode 或 route
- 執行簡單 deterministic script
- 依照 JSON schema 填寫基本欄位
- 不亂改檔案
- 不產生 fabricated completion claim
- 遇到複雜 judgment 時升級到 higher-tier model

## 6.4 Codex / code agent

測試它是否能：

- 接收 scoped mechanical task brief
- 遵守 allowed-files
- 遵守 out-of-scope
- 不做 architecture judgment
- 不 commit unless explicitly asked
- 產生 diff 後交回 Claude Code / Fabo review
- 執行 deterministic scripts / tests

如果無法實際呼叫所有模型，請至少建立：

- `benchmarks/model_compatibility_cases.yaml`
- `docs/model_compatibility_test_plan.md`
- manual command template
- expected transcript markers
- UNVERIFIED ledger

不要假裝測過。

---

## 7. 建立 model compatibility benchmark cases

請新增或更新：

- `benchmarks/model_compatibility_cases.yaml`

至少包含：

1. Haiku minimal route selection
2. Haiku JSON report filling
3. Sonnet dry-run execution
4. Sonnet AI-review report summary
5. Opus/Fable semantic harness cleanup judgment
6. Opus/Fable rolling improvement diagnosis
7. Codex scoped mechanical edit
8. Codex no-commit compliance
9. AI-review only vs AI-review + adaptive-harness
10. one-time review vs rolling improvement loop

每個 case 包含：

- `case_id`
- `model_tier`
- `task_prompt`
- `allowed_files`
- `expected_behavior`
- `forbidden_behavior`
- `success_criteria`
- `verification_method`
- `status`: proposed / runnable / executed / failed / unverified
- `result_artifact`
- `notes`

---

## 8. 建立 smoke test matrix

請建立或更新：

- `docs/integration_test_matrix.md`

matrix 至少包含：

- Test name
- Layer tested
- Command / prompt
- Expected output
- Actual result
- Status: PASS / FAIL / PARTIAL / UNVERIFIED
- Evidence file
- Next action

必測 layers：

- AI-review command
- AI-review runner
- AI-review report schema
- AI-review history
- adaptive-harness skill
- adaptive-harness runner
- shared schema
- report writer
- invocation audit
- Codex delegation policy
- public-safe posture
- model compatibility
- scheduled report-only behavior
- dry-run safety
- benchmark scaffold

---

## 9. 確認低階模型可用性

請特別針對低階模型做壓力測試，因為這套 harness 如果只有 Opus/Fable 看得懂，就不算成功。

請檢查：

- entrypoint 是否夠短
- skill description 是否夠明確
- mode names 是否不模糊
- required files 是否太多
- lower-tier model 是否會 bulk-read whole repo
- lower-tier model 是否能依照 route 找到 runner
- lower-tier model 是否知道何時升級
- JSON schema 是否太複雜
- report format 是否可由 deterministic script 產生，降低 LLM 負擔
- Haiku 是否只需做 deterministic / filling / routing，不需做 complex judgment

請提出：

- 哪些內容適合 Haiku
- 哪些內容適合 Sonnet
- 哪些內容必須 Opus/Fable
- 哪些內容適合 Codex
- 哪些內容必須 human

---

## 10. 驗證 scheduled behavior

請確認 scheduled review 設計可以安全執行：

- scheduled AI-review = report-only by default
- scheduled adaptive-harness review = report-only by default
- no direct main modification
- no deletion of prompts / hooks / subagents
- no permission changes
- no GitHub Actions changes without PR
- patch proposal only for high-risk changes
- human approval needed for merge

若 GitHub Actions / cron / scheduled task 已建立，請檢查其安全性。  
若尚未建立，請建立 minimal workflow proposal，但不要啟用高風險自動修改。

---

## 11. 整合修正

如果測試中發現：

- script 缺失
- schema 不一致
- report 無法互讀
- public/private 衝突
- skill activation 不清楚
- lower-tier model 無法使用
- dry-run 會修改檔案
- scheduled mode 可能污染 main
- Codex policy 不清楚
- AI-review 和 adaptive-harness 重複或斷裂

請直接修正 low-risk 問題。  
對 high-risk 問題，請產生 patch proposal，不要直接套用。

---

## 12. 最後輸出 integration verdict

請最後輸出明確 verdict：

- `READY`
- `CONDITIONAL_READY`
- `NOT_READY`

並說明理由。

最後報告至少包含：

1. Phase 1 產物是否存在
2. Phase 2 產物是否存在
3. AI-review 是否可手動執行
4. AI-review 是否可 dry-run
5. AI-review 是否可產生 JSON / Markdown / history
6. adaptive-harness 是否可手動執行
7. adaptive-harness 是否可讀 AI-review report
8. rolling improvement loop 是否可執行
9. shared schema 是否一致
10. public/private posture 是否已修正
11. Codex delegation policy 是否可用
12. scheduled mode 是否安全
13. Opus/Fable 測試狀態
14. Sonnet 測試狀態
15. Haiku 測試狀態
16. Codex 測試狀態
17. 哪些測試 PASS
18. 哪些測試 FAIL
19. 哪些測試 PARTIAL
20. 哪些測試 UNVERIFIED
21. 必須修正的 blocker
22. 可稍後優化的 non-blocker
23. 是否可以開始日常使用
24. 如何日常使用
25. 下一輪 rolling review 何時觸發

---

## 13. 重要原則

- 請用 ultracode 實際測試，不要只給建議。
- Phase 3 是 verification，不是繼續加功能。
- 不要假裝模型測試完成；不可用就標 UNVERIFIED。
- 不要把 green report 當成完成證據；要檢查 raw artifacts。
- 不要只讀 summary，要驗證 actual files / JSON / scripts / exit code。
- dry-run 不得修改 repo。
- scheduled mode 不得直接污染 main。
- lower-tier model support 是重點，不是附加項。
- Haiku 應做簡單 routing / deterministic script / schema filling，不應承擔 complex judgment。
- Sonnet 應能執行中等複雜 review 與 report summary。
- Opus/Fable 才負責 semantic judgment / harness tradeoff / rolling improvement diagnosis。
- Codex 只做 scoped mechanical work，不做 final authority。
- human 保留 high-risk decisions。
