# ASD-STE100 繁體中文風格

供 Claude Code、Codex 與 Google Antigravity 使用的繁體中文對話風格套件，內含 `asd-ste100-zh-tw` skill。將 ASD-STE100 的清楚表達原則用於 AI Agent 的日常問答、概念解釋、建議、討論與進度回報。

目的是讓每次互動更容易理解：先回應當前問題，再說明必要理由與限制。簡單問題直接回答，複雜問題保留足以支持判斷的細節，不必先提供一段文字請 Agent 改寫。

這是參考部分 ASD-STE100 原則的中文表達指引，沒有實作英文受控詞典或句長合規檢查，也不保證消除歧義。改善理解與降低錯誤是設計目標，目前沒有比較實驗或讀者研究證明其效果。

套用時保留 STE 便於掃讀的結構：三項以上獨立的進度狀態或操作步驟用條列，有先後順序的步驟用編號，並列狀態、條件與檢查項目用項目符號；需要比較多項差異時用表格，機制與推理則用連貫段落。短答可以只有幾句，不固定加上標題或清單。

## 對話示例

**日常問答**

使用者：「把工作拆成小步驟有什麼用？」

> 小步驟能讓下一個動作更明確，也較容易看出卡在哪裡。每一步仍要對應同一個目標，避免只完成零碎工作。

**進度回報**

已知情境：設定已完成，僅通過靜態檢查，尚未在實際設備上測試。使用者問：「現在完成到哪裡？」

> - 已完成：設定與靜態檢查。
> - 待驗證：尚未在實際設備上測試，目前不能確認設備能否正常運作。
> - 下一步：在設備上執行測試。

同一風格也可延伸至文件撰寫、改寫與檢查。更多情境見 [對話與改寫範例](skills/asd-ste100-zh-tw/references/examples.md)。

## 快速開始

可讓 AI Agent 協助安裝，或依下列步驟手動安裝套件。套件與單一 skill 安裝擇一即可。

### 複製安裝 Prompt

將下列 Prompt 貼給要協助安裝的 Agent，並填入來源。Agent 應先詢問作用範圍與套用形式，取得選擇後再寫入設定。

```text
請協助我安裝 ASD-STE100 繁體中文風格套件（asd-ste100-style），其中的 skill 名稱是 asd-ste100-zh-tw。
用途：調整 AI Agent 在日常問答、解釋、建議與進度回報中的表達風格，也可延伸至文件表達。
來源：https://github.com/felimet/asd-ste100-style

先閱讀來源的 README、套件描述檔與 SKILL.md，確認支援的安裝方式。
開始修改檔案或設定前，主動詢問我：
1. 要用在哪些 AI Agent？例如 Claude Code、Codex、Google Antigravity（agy CLI 或 IDE）、Gemini CLI，或其他工具。
2. 使用範圍是目前專案，還是跨專案的全域範圍？
3. 希望以什麼形式存在？請提供下列選項並說明差異：
   A. 僅安裝套件或 skill，按需使用。
   B. 加入 rules 或指令檔，作為所選範圍的常駐預設風格；例如全域常駐或專案常駐。
   C. 納入工具的個人化設定或自訂指令。
   D. 其他方式，先提出方案再由我選擇。
如果我已明確指定某項選擇，就沿用，不要重複詢問。其餘選項尚未確定時，先等待我的回答，不自行假定全域安裝或修改個人化設定。

收到選擇後：
- Claude Code 與 Codex 優先使用本專案的套件與 marketplace；Antigravity 的專案範圍優先使用 `.agents/skills/` 單一 skill。安裝方式必須符合我選定的作用範圍。若工具無法在該範圍安裝套件，先說明限制，讓我選擇該範圍的單一 skill 或其他方案，不自行改為全域安裝。
- 列出實際安裝位置與規則檔位置，保留既有內容，僅合併相關設定；遇到衝突時指出差異。
- 若要設為預設風格，將精簡規則加入工具支援的 rules、CLAUDE.md、AGENTS.md、GEMINI.md 或個人化指令，並引用實際可讀的 SKILL.md 路徑。
- 若目標工具不能讀取本機檔案，改提供可直接貼上的自足規則；無法代為操作設定介面時，提供文字與步驟，不宣稱已套用。
- 三項以上獨立的進度狀態或操作步驟用條列；有先後順序的步驟用編號，並列狀態、條件與檢查項目用項目符號，同時保留數值、條件、否定、時序、引用及不確定性。
- 完成後列出變更位置、作用範圍、啟用方式，以及實際完成與尚未完成的驗證。

請區分「全域可用」與「預設風格常駐」：只安裝套件或 skill，不代表每次回覆都會自動套用。
```

### 套件安裝

[下載套件 ZIP](dist/asd-ste100-style-plugin.zip) 並解壓，或使用包含 `plugin.json`、`.claude-plugin/`、`.agents/plugins/` 與 `skills/` 的完整專案資料夾。

以下命令從套件根目錄執行。Claude Code 範例使用專案範圍：

```powershell
claude plugin marketplace add . --scope project
claude plugin install asd-ste100-style@asd-ste100-local --scope project
```

不下載 ZIP 時，可直接從 GitHub 登錄 marketplace。兩個命令都保留專案範圍；這組命令尚未在乾淨環境實測：

```powershell
claude plugin marketplace add felimet/asd-ste100-style --scope project
claude plugin install asd-ste100-style@asd-ste100-local --scope project
```

`asd-ste100-local` 只是 marketplace 識別名稱，不表示套件必須在本機。

Codex CLI 可登錄本機 marketplace 並安裝套件；這會更新該機器的 Codex 套件設定：

```powershell
codex plugin marketplace add .
codex plugin add asd-ste100-style@asd-ste100-local
```

這組 Codex CLI 命令沒有專案 scope 選項。若只允許變更目前專案，請先確認可用的專案套件安裝方式，或選擇下方的專案單一 skill 安裝，不要直接採用跨專案設定。

Antigravity CLI（`agy`）可從本機目錄安裝套件，並提供驗證命令：

```powershell
agy plugin validate .
agy plugin install .
```

`agy plugin validate .` 與 `--strict` 已在 agy 1.5.3 對本專案根目錄的 `plugin.json` 執行並通過（僅有兩則 note：未宣告 logo、`$schema` 的載入方式說明）；`agy plugin install` 尚未實際執行。依官方文件，CLI 外掛安裝在使用者層級的 `~/.gemini/config/plugins/`，`agy plugin install` 沒有專案 scope 選項。官方文件另載明可把外掛資料夾放進工作區的 `.agents/plugins/`，僅在該專案啟用，但此做法尚未測試，需確認。若只允許變更目前專案，改用下方的專案單一 skill 安裝。官方文件只列出 `plugin.json` 與 `.antigravity-plugin/plugin.json` 兩種 manifest 位置，也未記載 marketplace 檔案格式，因此本專案沒有為 Antigravity 另建 manifest 或 marketplace。

本專案的 Codex marketplace 名稱為 `asd-ste100-local`。在支援本機 marketplace 的 Codex 桌面介面，也可從 Plugins 目錄選取該來源並安裝。套件安裝後，預設對話風格仍由下方的 [常駐規則](#設為-ai-agent-的預設風格) 決定。

### 單一 skill 安裝（選用）

將整個 `skills/asd-ste100-zh-tw` 資料夾複製到目標專案的對應位置，保留其中的參考文件。

| 工具 | 專案內的安裝位置 | 呼叫方式 |
| --- | --- | --- |
| Claude Code | `.claude/skills/asd-ste100-zh-tw/` | `/asd-ste100-zh-tw` |
| Codex | `.agents/skills/asd-ste100-zh-tw/` | `$asd-ste100-zh-tw` |
| Antigravity（CLI 與 IDE） | `.agents/skills/asd-ste100-zh-tw/`（與 Codex 同一路徑） | CLI：`/asd-ste100-zh-tw`；IDE：官方文件未說明斜線呼叫，由 Agent 依 `description` 判斷，或在提示中指名此 skill |

也可解壓 [skill ZIP](dist/asd-ste100-zh-tw.zip)，將其中的 `asd-ste100-zh-tw` 資料夾放入上述位置。`SKILL.md` 應直接位於該資料夾內，避免多放一層同名資料夾。

以下 PowerShell 範例從本儲存庫根目錄執行，同時安裝到 Claude Code 與 Codex 的專案目錄；Antigravity 讀取 `.agents/skills/`，與 Codex 同一路徑，因此不需要第三個目的地。請將 `../target-project` 改為既有專案的路徑；同名目的地已存在時會停止。

```powershell
$skillSource = (Resolve-Path './skills/asd-ste100-zh-tw').Path
$targetProject = (Resolve-Path '../target-project').Path
$skillTargets = @(
    (Join-Path $targetProject '.claude/skills/asd-ste100-zh-tw')
    (Join-Path $targetProject '.agents/skills/asd-ste100-zh-tw')
)
foreach ($skillTarget in $skillTargets) {
    if (Test-Path -LiteralPath $skillTarget) { throw "目的地已存在：$skillTarget" }
}
foreach ($skillTarget in $skillTargets) {
    New-Item -ItemType Directory -Path (Split-Path $skillTarget) -Force | Out-Null
    Copy-Item -LiteralPath $skillSource -Destination $skillTarget -Recurse
}
```

此 skill 以文件指令運作，不需要額外的 API 密鑰或執行期套件。安裝格式可參閱 [Claude Code 文件](https://code.claude.com/docs/en/skills)、[Codex 文件](https://learn.chatgpt.com/docs/build-skills) 與 [Antigravity Skills 文件](https://antigravity.google/docs/skills)。

若只需跨專案使用單一 skill，Claude Code 可放在 `~/.claude/skills/asd-ste100-zh-tw/`，Codex 可放在 `~/.agents/skills/asd-ste100-zh-tw/`，Antigravity 可放在 `~/.gemini/config/skills/asd-ste100-zh-tw/`（IDE 舊版路徑 `~/.gemini/antigravity/skills/` 仍受支援）。官方文件未列出 `~/.agents/skills/`，Antigravity 是否讀取該路徑需確認；要在 Antigravity 使用，請放在上述官方路徑。這只改變可用範圍，不會自動建立常駐風格規則。

### 呼叫 skill

在目標專案開啟 Claude Code、Codex 或 Antigravity 工作階段，輸入 skill 名稱及任務。

Claude Code 套件安裝後使用命名空間：

```text
/asd-ste100-style:asd-ste100-zh-tw 請用此風格回答：為什麼把工作拆成小步驟比較容易開始？
```

Claude Code 直接安裝單一 skill，或 Antigravity CLI 載入該 skill 時：

```text
/asd-ste100-zh-tw 請用此風格回答：為什麼把工作拆成小步驟比較容易開始？
```

Codex 可在 `$` 技能選單選取本套件的 `asd-ste100-zh-tw`；直接安裝單一 skill 時也可使用：

```text
$asd-ste100-zh-tw 請用此風格回答：為什麼把工作拆成小步驟比較容易開始？
```

一般說明採連貫段落，三項以上的進度狀態採條列，依序執行的操作段落採編號；同一答案可以結合這些結構，不為整段對話自動切換模式。需要固定格式、讀者背景或專案術語時，直接在同一個請求中說明。若工具未列出新安裝的 skill，重新開啟工作階段後再確認；Antigravity CLI 可執行 `/skills reload` 或開新對話。

## 設為 AI Agent 的預設風格

若希望 Agent 預設採用此風格，除了讓它能讀取 skill，還需要在該工具的個人化設定、rules 或指令檔加入預設規則。**全域安裝代表跨專案可用；全域常駐則需要全域指令來源載入這些規則。**

| Agent | 專案預設規則 | 全域預設規則 |
| --- | --- | --- |
| Claude Code | `CLAUDE.md` 或 `.claude/rules/*.md` | `~/.claude/CLAUDE.md` 或 `~/.claude/rules/*.md` |
| Codex | `AGENTS.md` | `~/.codex/AGENTS.md` |
| Antigravity | `AGENTS.md` 或 `GEMINI.md`（或 `.agents/rules/*.md`） | `~/.gemini/AGENTS.md` 或 `~/.gemini/GEMINI.md` |
| Gemini CLI（舊版） | `GEMINI.md` | `~/.gemini/GEMINI.md` |
| 其他 Agent | 工具支援的專案 rules 或指令 | 工具支援的個人化設定、自訂指令或全域 rules |

Codex 的標準檔名是 `AGENTS.md`（複數），不是 `AGENT.md`。Antigravity 的 `AGENTS.md` 或 `GEMINI.md` 不需要 frontmatter，載入後常駐；`.agents/rules/*.md` 需要有效的 `trigger` frontmatter（設為 `always_on` 才每回合注入）。Antigravity 的規則會累加而非互相覆寫，官方文件未定義 `AGENTS.md` 與 `GEMINI.md` 的優先順序；單檔上限 24 KB，全域與 `always_on` 規則共用 20,000 token 預算。`~/.gemini/GEMINI.md` 同時是 Gemini CLI 的全域檔，寫入會影響兩個工具。表列為預設位置；自訂設定目錄、override 檔與載入規則仍以目標工具為準。

上述設定方式依據 [Claude Code 指令與 rules 文件](https://code.claude.com/docs/en/memory)、[Codex AGENTS.md 文件](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Gemini CLI GEMINI.md 文件](https://geminicli.com/docs/cli/gemini-md/) 及 [Antigravity Rules 文件](https://antigravity.google/docs/rules)。依 Google 於 2026-05-19 發布的[轉換公告](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)，Gemini CLI 已由 Antigravity CLI 接替，個人方案自 2026-06-18 停止服務，僅部分組織授權仍可使用；本表保留 Gemini CLI 一列供舊環境參考。其他 Agent 是否原生支援此套件格式，需依其支援方式決定。

### 可複製的預設規則

將下列文字合併到所選範圍的設定中。最後一行的路徑由安裝 Agent 填入實際位置；只能使用設定介面的工具，可保留自足規則並省略路徑行。

```text
對話預設採用 ASD-STE100 繁體中文風格，適用於問答、解釋、建議、討論與進度回報；依當次指定語言、語氣及格式調整。
使用者自己的指令（CLAUDE.md、AGENTS.md、persona 或當次要求）規定回覆順序、必備內容或語氣時，以其為準；數值、否定、條件、時序與不確定性的規則仍然適用。
未被上述指令規定時，先回答當前問題，再補必要理由、條件與限制。簡單問題直接回答，複雜問題保留足以支持判斷的細節。
使用清楚的主體、動作與一致術語；保留數值、條件、否定、時序、引用及不確定性，區分已知、推論與尚未驗證。
三項以上獨立的進度狀態或操作步驟用條列，一至兩項用句子；使用者問是非判斷時，列表前先用一句寫結論。有先後順序的步驟用編號，並列狀態、條件與檢查項目用項目符號。機制與推理保留連貫段落，短答不固定加標題或清單。
此風格可延伸至文件表達；保留指定創作文體，不把風格調整當成內容修正或外部操作的授權。
需要完整規則時，讀取：<實際可讀的 SKILL.md 路徑>。
```

設定後，在相同範圍開啟新工作階段，確認 Agent 讀到的規則來源，再以日常問答、接續提問及操作指引各試一題。只完成檔案安裝，不能當作預設規則已載入的證據；跨回合及跨工作階段的預設效果，仍取決於目標工具實際載入規則的方式。

## 對話中的表達方式

| 情境 | 回覆重點 | 適合的結構 |
| --- | --- | --- |
| 簡短問答 | 直接回答，補上必要條件。 | 幾句即可，不固定加標題。 |
| 概念解釋與討論 | 先說主要意思，再用理由或例子銜接。 | 一段一主題；並列資訊再用條列。 |
| 建議與選擇 | 說明建議依據，以及會改變判斷的條件。 | 簡短段落、條列或比較表。 |
| 進度回報 | 說明目前結果、尚未確認之處與下一步。 | 優先採狀態條列；單一簡短狀態可用句子。 |
| 逐步指引 | 先寫必要條件，再寫操作；保留同步關係。 | 只在操作段落使用編號。 |

結構依交付內容決定；使用者明確指定自然或嚴格模式時，沿用其選擇。接續提問保留已確定的背景，依新資訊調整答案。

文件處理是延伸用途。一般潤飾可更正由已提供資訊唯一判定的錯誤，並說明更正；指定純成品或固定格式時只交付正確內容。資訊不足的主張先釐清或標為待確認。只有明確要求忠實保留時才保存原錯誤，並清楚標示，避免將其當成可發布成品。

## 常見用法

以下以單一 skill 的 Codex 語法示範。Claude Code 套件安裝時改用 `/asd-ste100-style:asd-ste100-zh-tw`，直接安裝單一 skill 時改用 `/asd-ste100-zh-tw`。

```text
$asd-ste100-zh-tw 用一個生活中的例子，說明「必要條件」和「充分條件」有什麼差別。

$asd-ste100-zh-tw 我有兩個選項：A 成本較低但需要手動整理，B 成本較高但能自動整理。每週只用一次，你會怎麼判斷？

$asd-ste100-zh-tw 目前只完成設定，測試還沒開始。請幫我向同事說明現在的進度。

$asd-ste100-zh-tw 說明以下操作順序：先確認檔案存在，再開啟檔案；不存在時回報錯誤並停止。
```

專案已定義的術語、介面名稱、命令、識別字、引文與指定輸出格式會優先保留。英文單字上限不直接換算為中文字數；句子是否需要拆分，取決於主題、條件層次與指涉是否清楚。

## 圖解與其他表達形式

也可要求以圖解、HTML 或影片腳本說明內容，例如：

```text
$asd-ste100-zh-tw 用簡短文字與 Mermaid 說明以下資料流程，區分處理順序與統計相關。

$asd-ste100-zh-tw 將以下內容寫成單檔 HTML 解說頁，清楚標示假設，讓核心說明在不操作互動元件時也能閱讀。

$asd-ste100-zh-tw 為以下主題撰寫解說影片腳本，分列畫面、旁白與字幕，保留必要條件及限制。
```

各種形式共用語意保留原則。實際圖像、網頁互動、影片渲染與配音，取決於執行環境提供的工具；腳本或程式碼本身不代表成品已完成或通過驗證。

## 規範依據

本 skill 參考 [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf) 的部分寫作原則。英文詞典、詞性與句長限制不直接套用於中文；中文規則、讀檔條件與編輯界線均為本專案設計，不是正式 STE 合規依據。媒介延伸與無障礙要求的來源另列於 [來源與規則對照](skills/asd-ste100-zh-tw/references/sources.md)。

文風調整不等於事實查核、專業審查或實際測試。需要查證或修正內容時，請在任務中明確說明。

## 授權

本專案採用 [MIT License](LICENSE)，著作權人為 Jia-Ming Zhou（Felimet）。單一 skill 亦附有 [LICENSE](skills/asd-ste100-zh-tw/LICENSE)，下載 ZIP 內均包含授權文件。

此授權適用於本專案內容，不變更外部 ASD-STE100 標準文件的著作權或授權條件。

ASD-STE100 Simplified Technical English 是 ASD 的註冊商標。本專案為獨立的第三方、受 STE 啟發的中文表達指引，與 ASD、STEMG 無隸屬、合作、認證或背書關係，也不提供 STE 合規。

## 文件導覽

| 文件 | 內容 |
| --- | --- |
| [SKILL.md](skills/asd-ste100-zh-tw/SKILL.md) | 對話風格、情境調整與回覆檢查。 |
| [文件與操作指引](skills/asd-ste100-zh-tw/references/documents.md) | 文件改寫、審查與操作步驟的處理界線；僅在這類任務時讀取。 |
| [對話與改寫範例](skills/asd-ste100-zh-tw/references/examples.md) | 問答、建議、接續討論、進度回報，以及文件延伸示例。 |
| [術語與語意控制](skills/asd-ste100-zh-tw/references/terminology.md) | 情態、量詞、領域術語及量值比較。 |
| [媒介規則](skills/asd-ste100-zh-tw/references/formats.md) | 圖解、HTML 與解說影片的表達原則。 |
| [來源與規則對照](skills/asd-ste100-zh-tw/references/sources.md) | 來源連結與英文標準原則的中文改編對照。 |
