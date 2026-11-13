# 測試紀錄說明

- 本目錄的案例與結果檔記錄各版本當時的人工試跑。結果檔內的版本雜湊對應當時的 SKILL.md，早於 1.0.3 的紀錄不代表目前版本。
- 這些紀錄由同一個 agent 作答並評分，沒有「未載入 skill」的對照組，樣本數小，只能作為回歸檢查，不能證明風格改善了理解。
- `ab-eval-2026-11-08.md` 是較嚴謹的盲評比較（無 skill、舊版、新版），結果與限制見該檔。
- `cli-eval-2026-11-09.md` 以 agy（Gemini 4 Argon medium）與 Codex CLI 互為生成者與評審，比較 5 個版本臂與自動觸發；程式與題目在 `eval/`。結論、限制與資料處理紀錄見該檔。
- `heldout-eval-2026-11-10.md` 是 lean（1.1.1）的獨立保留題重測（10 題、2 次取樣、base 對 v110 對 lean），判定規則在跑之前寫定；結果是沒有觀察到相對 v110 的退步，不是證明改善。
- `errata-2026-11-11.md` 更正上面兩份紀錄的錯誤，並列出未揭露的偏差（agy 整段重複、評審一致性、題目與範例重疊、評測環境）。讀舊紀錄前先讀這份。
- `eval/heldout2-protocol.md` 是 1.2.0 候選版評測的判定規則與第二組保留題（24 題），在跑之前單獨提交（commit 26f3f00）。這次加入 Claude Code 作為第三個生成者，Claude 端不載入任何使用者設定。
- `heldout2-eval-2026-11-12.md` 是第二組保留題的結果（3 個生成者、3 臂、每臂每題 1 次取樣）。1.2.0 候選版的 SKILL.md 在 agy 端觸發事前登錄的退步規則，所以 1.3.0 沿用 1.1.1 的 SKILL.md 文字；判定的計算可用 `eval/heldout2_decide.py` 從結果檔重跑。
- `eval/heldout3-protocol.md` 是第三組保留題與觸發測試的判定規則，在跑之前單獨提交（commit ad243af）。A 部分比較三種 `description` 的自動觸發，B 部分比較 1.2.0 候選版的篇幅句換進 1.1.1 之後的篇幅遵守率與必要內容。
- `heldout3-eval-2026-11-13.md` 是第三組的結果（216 筆觸發、324 筆生成、324 份評審）。A 部分選 `descA`，B 部分依規則採用新的篇幅段落，1.3.0 的 SKILL.md 據此修改；判定可用 `eval/heldout3_decide.py` 從結果檔重跑。
- `install-validation-2026-11-12.md` 記錄 commit 2881cf4 的 1.3.0（SKILL.md sha256 `0dca1520…`）在 Claude Code、Codex 與 agy 的安裝測試。不含 2026-11-13 對 `description` 與篇幅句的修改；推送後要從 GitHub 重測。
- `errata-2026-11-13.md` 更正第二組 protocol 的鎖定雜湊所對應的檔案版本。
- `manifest-validation-2026-11-13.md` 記錄 commit 64ba85d 的 `claude plugin validate` 與 `agy plugin validate --strict` 結果；不含安裝與執行時載入。
- 套件封裝可用 `scripts/build-dist.ps1 -Check` 重現檢查；CI 於 `.github/workflows/validate.yml`。
