# 對話風格驗證

日期：2026-11-04。套件版本：1.0.1。

本版以日常問答、解釋、建議、討論與進度回報為主，文件處理為延伸用途。結果對應 [conversation-style-results.json](conversation-style-results.json) 的檔案雜湊；先前紀錄保留其原有版本與答案。

## 靜態與封裝檢查

| 檢查 | 本輪結果 |
| --- | --- |
| Skill frontmatter | 以 `python -X utf8 <skill-creator>/scripts/quick_validate.py skills/asd-ste100-zh-tw` 執行官方驗證器，回傳 `Skill is valid!`。 |
| 通用套件描述檔 | 以 Agent Plugins 1.0.0 官方 JSON Schema 驗證通過。 |
| Claude 描述檔 | `claude plugin validate .claude-plugin/plugin.json --strict --json` 與 marketplace 的相同檢查均為 success，manifest errors/warnings 為空。 |
| 平台對應 | 套件識別、版本及說明一致；兩個 marketplace 來源仍指向同一套件根目錄。 |
| README 範例 | PowerShell 語法可解析；只在隔離目錄執行單一 skill 複製範例。兩平台的六個檔案與來源相同，既有目的地會拒絕覆寫。未執行套件安裝命令。 |
| 文件與參照 | README 九個本機連結/錨點有效。套件文字未含個人設定或本機使用者路徑，使用 ASCII `/`。 |
| ZIP | skill 六檔、套件十一檔；CRC、檔案清單及逐檔位元組比對通過。測試紀錄與開發檔案不進入套件。 |

## 文字情境試跑

獨立 agent 讀取 skill 後，依 [conversation-style-cases.json](conversation-style-cases.json) 作答。主 agent 檢視完整輸出並作以下判斷；未將預期答案提供給試跑 agent。

| 案例 | 實際觀察 |
| --- | --- |
| C1 短答 | 以兩句直接回答，沒有要求原文或添加標題、清單。 |
| C2 概念解釋 | 一個連貫段落，以同一生活例子說明必要與充分條件，保留兩者差異。 |
| C3 選項建議 | 提出暫定判斷並說明費用與時間缺口，沒有假造價格、所需時間或保證效益。 |
| C4 進度回報 | 保留三項已完成事項、實測尚未執行與下一步，未把格式檢查說成運作驗證。 |
| C5 接續提問 | 沿用已指定的專案範圍與按需使用，沒有重問選項或自行修改設定。 |
| C6 操作指引 | 使用編號，保留檔案不存在的停止分支，以及開啟、讀取、另存的順序。 |
| C7 指定格式 | 只輸出可解析 JSON，欄位正確，verified 為 false，沒有前言或 Markdown 圍欄。 |

另以獨立唯讀檢視核對 README、兩平台套件描述、marketplace、skill、UI 說明及範例：對話定位一致，未發現一般對話被排除、強迫套用文件格式或安裝後必然常駐的宣稱。

## 驗證界線

- 七題為同一獨立 agent 的單次文字試跑。C5 提供已知前文，並非原生 Agent 的長對話或跨工作階段載入測試。模型識別及取樣參數不可得。
- 未安裝或啟用全域套件，未修改 rules、個人化設定或發布套件。格式驗證與文字試跑不代表 Claude/Codex 原生載入已驗收。
- Claude 驗證器另提示公開目錄所需的授權與圖示尚未提供；本版未指定授權，亦不宣稱已符合公開上架條件。
