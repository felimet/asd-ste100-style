# 前提審查後的修訂與驗證

日期：2026-11-04。套件版本：1.0.2。此紀錄另立版本；先前的結果與雜湊保留不變。

## 審查判斷與修訂

| 議題 | 判斷 | 修訂 |
| --- | --- | --- |
| STE 名稱與效力 | 中文指引未實作英文受控詞典或句長檢查，不能宣稱同等效力。評估中的「STE 保證零歧義」也過強：官方仍要求檢查歧義，GR-2 明列 `with` 的多個核准意義。[1] | 明示名稱為參考來源、清楚表達為設計目標；區分官方原則與本專案規則。 |
| 自動模式切換 | 未有多輪可靠性證據支持穩定分類。 | 改依實際交付內容選結構：說明用段落、操作段落用編號，明確指定的模式才沿用。 |
| 補充文件路由 | 偵測輸入特徵不等於模型能察覺自己的錯誤。 | 核心數量、邏輯、統計與完成狀態檢查留在主檔；以可辨識的內容列出補充讀檔條件。 |
| 臺灣用語 | 抽象語感要求不足以交代專案的用語選擇；任意全域替換也會破壞正式名稱。 | 加入常用術語預設與具體空泛措辭例子，保留專案詞彙表、引文及介面名稱優先。 |
| 潤飾中的已知錯誤 | 一般潤飾與明確要求忠實保留應分開。 | 唯一可判定的錯誤可更正；資訊不足先釐清或標記；明確保留錯誤時在引用前標明。純成品與固定格式不額外加欄位或說明。 |
| 多媒體來源 | 社群貼文內容未核實，不能替 HTML 細則背書。 | 移除該來源；媒介選擇標為專案延伸，HTML 無障礙另列 W3C 依據。[2-4] |

來源核對採官方頁面與官方 PDF 搜尋索引，未重新逐頁核對來源表的全部歷史頁碼。依 Snowflake 位移式 `(2105819303471976479 >> 22) + 1288834974657` 計算，該 ID 時間為 `2026-10-02T00:37:00.835Z`，不是十月中旬；時間計算無法驗證作者或貼文內容。

## 本輪靜態與封裝檢查

- Agent Plugins 1.0.0 官方 JSON Schema：`PASS`；兩個 plugin 描述檔版本同為 `1.0.2`，授權同為 MIT。
- Claude plugin 與 marketplace 的 `--strict --json` 檢查：`success: true`，manifest errors/warnings 為空。目錄建議仍有缺少圖示與 `.agents` 掃描未完成提示，不等於市集上架驗收。
- skill-creator `quick_validate.py`：`Skill is valid!`。
- skill ZIP 七檔、plugin ZIP 十三檔：授權副本、檔案清單、CRC 與來源逐檔位元組一致性均通過。十六項本機連結的目標檔案存在；未全面驗證錨點。
- `git diff --check` 通過。封裝未納入 `.cache/`、`.work/` 或 tests。

## 獨立文字情境試跑

輸入見 [critical-review-cases.json](critical-review-cases.json)，完整回答、試跑者記錄的新增參考文件與版本雜湊見 [critical-review-results.json](critical-review-results.json)。兩個獨立 agent 各處理五題；僅提供修訂後 skill 與案例，未提供預期答案。主 agent 檢視實際回答後作以下判斷。

| 案例 | 實際觀察 |
| --- | --- |
| R1 一般潤飾 | 更正百分點差值，保留端點並說明更正。 |
| R2 明確忠實保留 | 保留原主張，錯誤標記先於改寫句，另列正確比較。 |
| R3 分母缺漏 | 保留成功件數，將成功率變化標為無法確認，沒有猜測總件數。 |
| R4 正確相對增幅 | 保留 25% 至 30% 的相對增幅 20%，未誤改成錯誤數值。 |
| R5 混合內容 | 解釋採段落，操作採編號，保留不存在時回報並停止。 |
| R6 條件與統計 | 保留核准的必要條件、核准後的重新檢查，以及未達顯著不能推出相同。 |
| R7 固定 JSON | 只交付 `text` 欄位與正確百分點表述，無額外前言。 |
| R8 術語例外 | 一般敘述採臺灣用語，保留專案「影格」與按鈕「數據匯出」。 |
| R9 效力主張 | 拒絕宣稱正式合規或保證消除歧義，區分設計目標與驗證。 |
| R10 來源界線 | 將 HTML 細則連到 W3C 來源，未歸因於 STE 或未核實社群貼文。 |

十題均符合本輪檢查項目；這不是可靠率估計。兩組首次遇到觸發內容時均記錄讀取 `terminology.md`；R10 另讀來源與媒介文件。讀檔紀錄由試跑者提供，並非原生 Agent 載入機制的儀器量測。

## 驗證界線

每題僅單次作答，同組案例共用前文與已讀文件；不是十個彼此隔離的執行期試驗。未記錄模型識別與取樣設定，未做跨模型、讀者理解、長對話、延遲或 token 比較。未執行 Claude/Codex 原生安裝、常駐載入、完整無障礙驗收或 GitHub 上傳。

## 參考來源

[1] ASD, [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf), Jan. 15, 2025, Rules 1.1–1.3, 5.1, 5.2, 6.3 and GR-2；另見 [官方 FAQ](https://www.asd-ste100.org/STE_faq.html)。

[2] W3C, [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/), success criteria 1.4.3, 2.1.1, 2.4.7 and 3.1.1。

[3] W3C, [H57: Using the language attribute on the HTML element](https://www.w3.org/WAI/WCAG22/Techniques/html/H57)。

[4] W3C, [C39: Using the CSS prefers-reduced-motion query to prevent motion](https://www.w3.org/WAI/WCAG22/Techniques/css/C39)。
