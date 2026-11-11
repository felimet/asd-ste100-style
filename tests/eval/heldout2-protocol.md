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

- 生成者：agy 1.5.5（`gemini-4-argon-medium`）、Codex CLI 0.166.0（設定檔預設模型 `gpt-6.1-sol`，reasoning effort 覆寫為 medium）、Claude Code 2.1.319（`--model sonnet`，effort medium）。每臂每題取樣 1 次。
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

## 失敗處理

- 生成在重試後仍是空回覆的題目，在該生成者的配對差中排除，並報告數量。
- 評審呼叫失敗時，額度恢復後只重跑失敗的評審；仍失敗的評審從該題排除並報告。
