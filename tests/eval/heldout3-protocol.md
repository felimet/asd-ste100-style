# 第三組保留題與觸發測試的判定規則（跑之前先寫定，2026-11-12；事前登錄審查後修正，2026-11-13）

這一輪回答兩個問題，各自有寫定的判定規則：

- A 部分：SKILL.md 的 `description` 要不要改成帶「非官方改編」標示的寫法，以及要不要擴大觸發說法。判準是自動觸發。
- B 部分：把 1.2.0 候選版的篇幅規則單獨換進 1.1.1 的 SKILL.md，能不能提高篇幅限制的遵守率，而且不減少必要內容。這條是第二組保留題 g02 的事後觀察（1.1.1 在 agy 與 Claude 超過上限，v120 沒有），不是事前假設，所以用新的題目確認。

判定由 `heldout3_decide.py` 計算，規則與門檻寫在程式與下文，兩者不一致時以本文件為準並修正程式。

## 共同設定

- 生成者：agy 1.5.6（`gemini-3.8-flash-high`）、Codex CLI 0.166.0（設定檔預設模型 `gpt-6.1-sol`，reasoning effort 覆寫為 medium）、Claude Code 2.1.319（`--model sonnet`，effort medium）。
- Claude 生成者隔離：不載入任何 `CLAUDE.md`、使用者設定、plugins、hooks、MCP 與 auto memory；只載入工作目錄的 `.claude/skills/`。agy 與 Codex 沿用先前做法，會載入作者的全域指令與使用者層級的 skill 與外掛。全域指令各臂相同；skill 清單的長度則會影響 description 顯示多少（2026-11-13 量測）：
  - Codex：作者機器上列出 249 個 skill，每則 description 只顯示前 77 字（`codex debug prompt-input`，不呼叫模型）；`-c skills.max_context_tokens` 調高沒有效果。`old` 與 `descA` 的觸發句（第一句，46 字）完整顯示；`descB` 的觸發子句有 82 字，被截在「使用者已將此風格設為對話預設」。
  - agy：列出 80 個 skill。請模型不用工具、照抄系統指令中這個 skill 的條目，`old` 與 `descB` 都是完整的 description（模型自述，不是程式量測）。
  - Claude：隔離後只看到這一個 skill。
- 執行程式：`run_cli_eval.py`，執行腳本在 `heldout3_run/`；工作目錄與輸出放在 repo 外。執行條件沿用第二組的調整（Codex 兩路並行、逾時 480 秒；agy 評審加「不要使用任何工具」一句、逾時 480 秒）。
- 題目由看不到 skill 與 repo 的子代理撰寫，經審查者修正後由定稿者直接寫檔。修改 skill 的人在評測結束前不讀題目內容，只看題數、雜湊與驗證程式的通過與否。

## A 部分：description 的觸發測試

### 臂

三臂只差 SKILL.md 第 4 行（`description`），其餘檔案與 commit 2881cf4 的 `plugins/asd-ste100-style/skills/asd-ste100-zh-tw/` 相同。

| 臂 | description | SKILL.md sha256 |
| --- | --- | --- |
| `old` | 使用者要求 STE 風格、清楚精確且易於掃讀的繁體中文回覆，或已將此風格設為對話預設時使用。依 ASD-STE100 原則調整 AI Agent 的繁體中文對話風格，適用於日常問答、概念解釋、建議、討論與進度回報，也可延伸至文件表達。 | `0dca1520bf83eaf1f4c49daa3190a18e9ceefcd1825b9e3123136759f7c8fcad` |
| `descA` | 使用者要求 STE 風格、清楚精確且易於掃讀的繁體中文回覆，或已將此風格設為對話預設時使用。參考 ASD-STE100 部分原則的非官方改編，調整 AI Agent 的繁體中文對話風格，適用於日常問答、概念解釋、建議、討論與進度回報，也可延伸至文件表達。 | `d35efa7187081266bb78764c77224bfe1ff0d3b16e37ce687fcb40b74d778160` |
| `descB` | 使用者要求 STE 或 ASD-STE100 風格，或要求以清楚、精確、一句一重點且易於掃讀的繁體中文回覆、說明或改寫時使用；使用者已將此風格設為對話預設時也使用。參考 ASD-STE100 部分原則的非官方繁體中文對話風格，適用於日常問答、概念解釋、建議、討論與進度回報，也可延伸至文件表達。 | `6cb562d2f3cf388988b5d6d1f3d03c7981187a181676ac5375f22ae275814595` |

`descA` 只把「依 ASD-STE100 原則調整」改成非官方標示，觸發條件的文字不變。`descB` 是 1.2.0 候選版的 description，觸發說法較寬。

### 題目與執行

- `triggers2.json`：24 則新的單輪提問，12 則應觸發（明說 STE 4、描述清楚精確的技術寫作式寫法 5、要求設為之後的預設 3），12 則不應觸發（程式 2、翻譯 2、創作 2、其他指定風格 3、一般問答 3）。舊的 `triggers.json` 在 2026-11-09 用過，不再用來做決定。
- 不加 `/skill` 或 `$skill` 前綴，每臂每題每個生成者 1 次。
- 載入的判定沿用 `run_cli_eval.py`：agy 與 Codex 看工具紀錄有沒有讀這個 skill 的 SKILL.md；Claude 看有沒有呼叫 Skill 工具或讀 SKILL.md。

### 判定

只用 agy 與 Claude 判定，因為 Codex 對三臂截掉的內容不同（見共同設定）。Codex 的計數照樣報告，不列入判定。

`P(X)` 是臂 X 在 agy 與 Claude 合計 24 則應觸發題中載入的次數，`N(X)` 是合計 24 則不應觸發題中載入的次數；排除的題目不計。

1. 臂 X 可接受：`P(X) ≥ P(old) − 5` 且 `N(X) ≤ N(old) + 3`。
2. `descB` 可接受，而且 `P(descB) − P(descA) ≥ 6`、`N(descB) ≤ N(descA) + 3` 時，選 `descB`。
3. 否則 `descA` 可接受時選 `descA`；不可接受時保留 `old`。

`descA` 是預設：它的觸發句與 `old` 逐字相同，只改非官方標示。`descB` 一定要比 `descA` 多觸發 6 次以上才選，所以三臂沒有差異時，`descB` 不會因為 `descA` 的雜訊就勝出。`descA` 真的較差、`descB` 與 `old` 相當時，規則會選 `descB`，這是刻意的：`descB` 同樣帶有非官方標示，觸發也沒有變差。

門檻由 `heldout3_decide.py simulate` 校準（seed 1，每個情境 4000 次）。三臂真實觸發率相同時，四種情境選 `descA` 的比率是 0.898 至 1.000，選 `descB` 的比率最多 0.036。代價是檢定力低：

- 情境 N3 中，`descB` 在兩家各 8 則應觸發題的觸發率真的提高（agy 0.80 → 1.00、Claude 0.50 → 1.00，合計期望多 5.6 次）時，選 `descB` 的比率是 0.48。
- 情境 N1 中，`descA` 在兩家每則應觸發題的觸發率都真的降低 0.25 時，選 `descA` 0.29、`descB` 0.56、`old` 0.15。

所以結論只寫成「沒有觀察到明顯變差」或「`descB` 比 `descA` 明顯較常觸發」，不寫成證明較好。

### 失敗處理

呼叫失敗（rc ≠ 0 或逾時）時重跑一次；仍失敗的題目，在該生成者的三臂中一起排除，並報告數量。

## B 部分：篇幅規則的單一變更

### 臂

- `ship`：commit 2881cf4 的 `plugins/asd-ste100-style/skills/asd-ste100-zh-tw/`，SKILL.md 第 4 行換成 A 部分選定的 description。
- `len`：`ship` 再把 SKILL.md「在對話中套用」第二段的最後一句換掉，其餘完全相同。

原句：

> 使用者限定篇幅（例如「一句話」「簡單說」）時，只交付符合限制的答案；補充說明與免責聲明只在會改變答案時才附。

換成（1.2.0 候選版原文）：

> 使用者限定篇幅（例如「一句話」「簡單說」「50 字內」）時，整則回覆都要符合限制，附註、免責說明與「此處省略……」之類的句子也算在內。放不下的補充就刪除。少了它答案會變成錯的限定，壓縮主答案後放進限制內；使用者限定句數時，併入既有句子，不另起一句。「省略了什麼」「未檢查什麼」不算這類限定。

各臂實際檔案的 sha256 由 harness 寫在工作目錄的 `arms.json`，結果紀錄會附上。

### 題目

- `heldout3-prompts.json`：18 題，h01 至 h18。12 題 `length_limited`（明確字數 4、限定句數 4、模糊的簡短要求 4；約一半是健康、金錢、法律或安全等自然會想加但書的主題），6 題 `general`（explain、advice、progress、debug、procedure、rewrite 各一，不限篇幅）。
- 機械檢查：明確字數題 `max_chars = ceil(N × 1.4)`；句數題 `max_sentences = N`，另設寬鬆的 `max_chars`；模糊題由撰寫者設 `max_chars` 並在 `gold_note` 寫理由。句數以 `。！？!?` 與換行切分、含文字的片段計，`；，、：` 與英文句點不切句（`run_cli_eval.count_sentences`）。progress 題可另設 `first_line_regex`。
- 參考答案在 `heldout3-gold.json`，驗證用的通過與不通過回覆在 `heldout3-probes.json`；評審都不使用。
- 鎖定雜湊（sha256）：見文末「題目鎖定」。

### 執行

每臂每題每個生成者取樣 3 次（rep 0 至 2），共 18 × 2 × 3 × 3 = 324 筆生成。生成時以 `/asd-ste100-zh-tw`（agy、Claude）或 `$asd-ste100-zh-tw`（Codex）明確呼叫。每筆由另外兩家評審，不自評；同一題同一 rep 的兩臂回覆一起評。標籤順序依題號與 rep 輪替，同一個生成者的兩位評審看到相反的順序，所以每題 6 次評審中 `len` 恰好 3 次標為 A（`order_for` 的 `gen_target` 參數；selftest 檢查）。評分表與第二組相同（atoms、directness、readability、tone、fabricated、best）。

### 指標

- 篇幅遵守：`length_limited` 題的回覆是否通過該題全部的 `max_chars` 與 `max_sentences` 檢查。每個（生成者、臂、題）取 3 次的平均。
- atoms 滿足率：每筆回覆兩位評審的平均，每個（生成者、臂、題）再取 3 次的平均。

### 判定（`len` 對 `ship`）

主要效益 P：對每道 `length_limited` 題，先算各生成者的篇幅遵守率差（`len − ship`），再對三個生成者取平均；12 題的平均 ≥ +0.05，且 bootstrap 95% CI 下界 > 0。

退步規則（任一成立就不採用）：

1. 任一生成者的 atoms 逐題配對差平均 ≤ −0.03，且 bootstrap 95% CI 上界 < 0。以全部 18 題與 12 題 `length_limited` 題各算一次，任一組成立即算。
2. 三個生成者的 atoms 配對差平均再取平均 ≤ −0.02。同樣以 18 題與 12 題各算一次，任一組成立即算。
3. 任一生成者在 `length_limited` 題所有回覆的篇幅遵守率，`len` 比 `ship` 低超過 0.08。

換掉的句子只在使用者限定篇幅時適用，必要內容的損失會集中在 12 題 `length_limited`；只用 18 題計算會把這類損失稀釋三分之一，所以規則 1 與 2 另用 12 題計算。

P 成立且三條退步規則都不成立時，採用 `len`，把該句換進 SKILL.md；否則 SKILL.md 維持 `ship`。bootstrap 沿用 `run_cli_eval.boot_ci_raw`（4000 次、seed 7）。採用時寫成「在限定篇幅的題目上提高遵守率，沒有觀察到必要內容退步」；不採用時照實寫出哪一條不成立。

### 一併報告、不列入判定

- 各生成者的篇幅遵守率（依題型細分）、中位字數、general 題的字數比（`len / ship`，檢查是否外溢到不限篇幅的題目）。
- 每位評審單獨計算的 atoms、directness、readability、tone 逐題配對差，與 fabricated 比率差（`len − ship`，附 bootstrap CI；`descriptives` 的 `per_judge_*`）。
- 每個生成者與臂的整段重複次數（以回覆計，不分評審）。

### 失敗處理

- 生成：`run_ab.sh` 跑兩輪，每輪先刪掉 rc ≠ 0 或空回覆的紀錄再重跑；每次呼叫內另有 2 次嘗試。仍有 rc ≠ 0 或缺檔時不進評審，額度恢復後重跑腳本。兩輪後仍是空回覆（rc = 0）的紀錄保留，照常與另一臂一起送評；判定時 `decide_ab` 把它排除，另一臂同 rep 的回覆照常列入（因為取 3 次平均），並報告數量。
- 評審：跑兩輪，每輪先刪掉失敗的評審紀錄再重跑。仍失敗的評審不計，該筆以另一位評審的分數計；兩位都失敗時該筆不列入 atoms。數量列在 `judge_failures` 與 `missing_cross_judges`。

## 題目鎖定

題目由一位撰寫者寫草稿；保留題經事實核對與可評性兩位審查者提出 18 項修改、接受 17 項（拒絕的一項與另一項接受的提議衝突），觸發題經一位審查者提出 3 項、全部接受。修改 skill 的人只執行了下列不輸出題目內容的驗證：題號與題型配比正確（12 題限定篇幅：字數、句數、模糊各 4；6 題 general 各一種），18 題涵蓋 18 個領域；每題參考答案與 `probe_pass` 通過該題全部機械檢查，有機械檢查的題目 `probe_fail` 都被擋下；觸發題 24 則，類別配比符合上文。

| 檔案 | sha256 |
| --- | --- |
| `heldout3-prompts.json` | `1bb6194ea19342993d9dfa6b9a47ba9206bae007c4cc9c5b3470c6a57d40c1e6` |
| `heldout3-gold.json` | `af45a69994202118edf4906a4da40b235e1a012b3ba0b4ecf7a04b3fe242341d` |
| `heldout3-probes.json` | `64be23deed66d0dc9f1312360a7f86982fe55719f39cc3838d34a3548f5d1084` |
| `triggers2.json` | `f860d5ebb5162ba88b22d7b1d678df40a1e8a3f495870065e9c58fd199fcdc89` |

## 事前登錄審查

commit 前，兩位審查者檢查本文件、`heldout3_decide.py`、`run_cli_eval.py` 的變更與執行腳本，一位看程式與規則是否一致（含變異測試），一位找設計缺陷，都不讀題目內容。23 項指摘各由一位驗證者查證，6 項成立，都在產生任何資料前修正：

1. 兩臂時，Codex 生成者的兩位評審看到相同的標籤順序：`order_for` 加上 `gen_target`。
2. 本文件列出逐評審的 directness 等數字，程式卻沒有計算：`descriptives` 補上。
3. A 部分原規則（每家 ±1、`descB` 可因 `descA` 不可接受而勝出）在三臂沒有差異時約有 27% 選 `descB`：改成兩家合計、以模擬校準門檻、`descA` 為預設。
4. Codex 截斷 description，各臂被截掉的內容不同：Codex 改為只報告。
5. 規則 1 與 2 只用 18 題，會稀釋限定篇幅題上的損失：另用 12 題計算。
6. 原執行腳本做不到「空回覆不列入、另一臂照常列入」：改寫失敗處理與 `heldout3_run/`。

其餘 17 項經查證不影響判定，多數是 selftest 沒有釘住的邊界值。

修正後由另一位審查者只檢查這 6 項修正，又找到 4 項，同樣在產生資料前修正：

1. 評審開始後重跑 `run_ab.sh` 時，重新生成的空回覆會沿用舊的評審分數：`clean gen` 刪除生成紀錄時，同時刪除同一生成者、題號與 rep 的評審紀錄。
2. `run_ab.sh` 印出的評審預期筆數應為 324。
3. 檢定力情境的效果量寫錯（模擬把機率截在 1）：改寫為實際的觸發率。
4. 「`descB` 不會因為 `descA` 不可接受就勝出」與模擬結果不符：保留規則，改寫說明並補上該情境的三個比率。

審查者與驗證者都是 Claude，屬同一模型家族，未經外部驗證。
