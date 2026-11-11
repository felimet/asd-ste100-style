# 第二組保留題的判定規則（跑之前先寫定，2026-11-11）

## 題目

- `heldout2-prompts.json`：24 題，g01 至 g24。題型為 short_qa 3、explain 4、advice 3、progress 3、debug 3、rewrite 3、procedure 2、format_constrained 2、emotional 1，涵蓋 9 個領域。
- 撰寫者看不到 skill 與 repo；事實核對與偏誤檢查兩位審查者修正 atoms 與機械檢查，共 40 項提議、接受 20 項。驗證程式確認每題的參考答案通過自己的機械檢查，13 個錯誤回覆被擋下，20 個正確回覆沒有被誤判。參考答案在 `heldout2-gold.json`，評審不使用。
- 鎖定雜湊（sha256）：`heldout2-prompts.json` 為 `c90206947a092a90cf21694a190bdfe8c66d5a7fff1052edbbc366d563893b0f`，`heldout2-gold.json` 為 `bfcd58b36e65c4786a520526db136dabcdc9ea51ebcbb2161e9d51582ecfc185`。
- 修改 skill 的人在評測結束前沒有讀題目內容。撰寫規格裡提到的題型包含「可以說完成了嗎」式的是非進度題與一題情緒題，這兩類和 skill 範例同型，所以另做排除這些題型的穩健性檢查（見下方）。

## 臂

- `base`：不載入 skill。
- `lean`：1.1.1，commit 5581050 的 `skills/asd-ste100-zh-tw/`。
- `v120`：1.2.0 候選，`plugins/asd-ste100-style/skills/asd-ste100-zh-tw/`。各臂實際檔案的 sha256 由 harness 寫在工作目錄的 `arms.json`，結果紀錄會附上。

## 生成者與評審

- 生成者：agy 1.5.5（原定 `gemini-4-argon-medium`，見下方修訂）、Codex CLI 0.166.0（設定檔預設模型 `gpt-6.1-sol`，reasoning effort 覆寫為 medium）、Claude Code 2.1.319（`--model sonnet`，effort medium）。每臂每題取樣 1 次。
- Claude 生成者完全隔離：不載入任何 `CLAUDE.md`、使用者設定、plugins、hooks、MCP 與 auto memory。agy 與 Codex 沿用先前做法，會載入作者的全域指令；這是已知限制，三臂相同。
- 評審：每則回覆由另外兩家評審，不自評。標籤順序以題號與評審輪替，每臂在每個位置出現的次數相同。

## 主要指標與判定（v120 對 lean）

主要指標是 atoms 滿足率：每題兩位評審的平均，再逐題做 v120 − lean 配對差。下列任一成立，就不採用 v120 的 SKILL.md，改回 1.1.1 的 SKILL.md 文字；references、README 與封裝的修正照常保留。

1. 任一生成者的配對差平均 ≤ −0.03，且 bootstrap 95% CI 上界 < 0。
2. 三個生成者的配對差平均再取平均 ≤ −0.02。
3. 任一生成者的機械檢查全過率，v120 比 lean 低超過 0.08（約 24 題中的 2 題）。

其餘情形採用 v120。除非 CI 下界 > 0，結論寫成「沒有觀察到退步」，不寫成「證明改善」。

## 一併報告、不列入判定

- Claude 端的 v120 − base 與 lean − base。若 v120 − base 的 atoms CI 上界 < 0，README 要寫明 skill 在 Claude 上可能減少必要內容。
- 穩健性：排除 progress、emotional、short_qa 三類題目後重算配對差；若方向與全部題目相反，照實寫出。
- directness、readability、tone、fabricated、字數、條列比例、整段重複率。

## 修訂（2026-11-12，看到任何評分前）

- agy 的 `gemini-4-argon-medium` 在開跑後立刻回報個人額度用完（RESOURCE_EXHAUSTED，約 63 小時後重置），前 6 筆 agy 生成全部失敗。擁有者決定把 agy 的生成者與評審模型改為 `gemini-3.8-flash-high`。這時只有 5 筆 Claude 生成完成，還沒有任何評審結果，也沒有人讀過回覆內容。
- 失敗的 agy 生成與 3 個評到空回覆的評審檔已刪除；5 筆 Claude 生成保留，因為它們來自同一份凍結的臂與設定。
- 判定規則與其他設定不變。agy 端結果不能和 2026-11-09、11-10 用 Argon 的紀錄直接比較。

## 執行層調整（2026-11-12，看評分之前）

- Codex：六路並行時，約 01:06 之後的呼叫連續逾時（兩次 240 秒），失敗分散在各題型與各臂，含 base；之後在 01:39 撞到用量上限（03:58 重置）。Codex 生成改為兩路並行、逾時 480 秒（`CODEX_TIMEOUT`），Codex 評審改為單路並行；失敗紀錄刪除後重跑。
- agy 評審：Gemini 3.8 Flash 擔任評審時，部分題目會嘗試呼叫指令工具，非互動模式自動拒絕後沒有輸出（24 份中 4 份失敗；`--mode plan` 無效）。Claude 評審以 `--tools ""` 執行、Codex 評審在空的唯讀目錄執行，所以 agy 評審的提示末尾加上一句「不要使用任何工具，也不要執行指令或讀取檔案；只依上面提供的內容評分，直接輸出 JSON。」，評分標準不變；逾時改為 480 秒（`AGY_JUDGE_TIMEOUT`）。為了讓同一位評審前後條件一致，已完成的 agy 評審全部刪除，用新提示重跑。
- 這兩項只改執行條件，題目、臂、判定規則與 Claude 評審都不變。做這些調整時，沒有人讀過回覆內容或評分。

## 失敗處理

- 生成在重試後仍是空回覆的題目，在該生成者的配對差中排除，並報告數量。
- 評審呼叫失敗時，額度恢復後只重跑失敗的評審；仍失敗的評審從該題排除並報告。
