# ASD-STE100 繁體中文風格

給 Claude Code、Codex 與 Google Antigravity 使用的繁體中文對話風格 skill（`asd-ste100-zh-tw`，隨套件 `asd-ste100-style` 發行），設計目標是讓回覆更直接、易於掃讀。它參考 ASD-STE100 的部分清楚表達原則，用於日常問答、概念解釋、建議、討論與進度回報：先回應當前問題，再補必要的理由與限制。簡單問題直接回答，複雜問題保留足以支持判斷的細節，不必先貼一段文字請 Agent 改寫。

> **範圍與證據。** 這是非官方的中文表達指引，沒有實作 ASD-STE100 的英文受控詞典或句長檢查，不提供 STE 合規，也不保證消除歧義。在明確呼叫 skill 的盲評（量測的是 1.1.1）中，agy 與 Claude Code 的回覆變短，Codex 沒有觀察到好處；自動觸發與常駐規則下的效果沒有量測，也沒有人類讀者研究證明它改善理解。細節與限制見[評測結果](#評測結果)。

## 範例

**日常問答**

使用者：「把工作拆成小步驟有什麼用？」

> 小步驟能讓下一個動作更明確，也較容易看出卡在哪裡。每一步仍要對應同一個目標，避免只完成零碎工作。

**進度回報**

已知情境：設定已完成，僅通過靜態檢查，尚未在實際設備上測試。使用者問：「現在完成到哪裡？」

> - 已完成：設定與靜態檢查。
> - 待驗證：尚未在實際設備上測試，目前不能確認設備能否正常運作。
> - 下一步：在設備上執行測試。

同一風格也可延伸至文件撰寫、改寫與檢查。更多情境見[對話與改寫範例](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/references/examples.md)。

## 風格重點

結構依回覆要交付的內容決定，不固定套用模板；使用者明確指定自然或嚴格模式時，沿用其選擇。接續提問保留已確定的背景，依新資訊調整答案。

| 情境 | 回覆重點 | 適合的結構 |
| --- | --- | --- |
| 簡短問答 | 直接回答，補上必要條件。 | 幾句即可，不固定加標題。 |
| 概念解釋與討論 | 先說主要意思，再用理由或例子銜接。 | 一段一主題；並列資訊再用條列。 |
| 建議與選擇 | 說明建議依據，以及會改變判斷的條件。 | 簡短段落、條列或比較表。 |
| 進度回報 | 說明目前結果、尚未確認之處與下一步；使用者問是否完成等是非判斷時，列表前先用一句寫結論。 | 三項以上獨立狀態用條列，一至兩項寫進句子。 |
| 工作中的更新 | 只寫新結果或阻礙。 | 一句即可。 |
| 逐步指引 | 先寫必要條件，再寫操作；保留同步關係。 | 只在操作段落使用編號。 |

- 有先後順序的步驟用編號；並列狀態、條件與檢查項目用項目符號；比較多項差異用表格；機制與推理用連貫段落。
- 保留數值、條件、否定、時序、引用與不確定性，區分已知、推論與尚未驗證。
- 專案已定義的術語、介面名稱、命令、識別字、引文與指定輸出格式優先保留。
- 中文句長依語意處理。英文單字上限不直接換算為中文字數，句子是否拆分取決於主題、條件層次與指涉是否清楚。
- 文件處理是延伸用途。一般潤飾只更正可由已提供資訊唯一判定的錯誤，並說明更正處；指定純成品或固定格式時只交付正確內容。資訊不足的主張先釐清或標為待確認。只有明確要求忠實保留時才保存原錯誤，並清楚標示，避免將其當成可發布成品。

## 快速開始

先決定安裝形式，兩種擇一：

- **套件**：經 marketplace 或套件資料夾安裝，內含 skill 與套件描述檔。
- **單一 skill**：把 `asd-ste100-zh-tw` 資料夾複製到專案或使用者目錄，範圍由放置位置決定。

可以請 AI Agent 代為安裝（下一節），也可以照後面的步驟手動安裝。

### 複製安裝 Prompt

將下列 Prompt 貼給要協助安裝的 Agent，並填入來源。Agent 應先詢問作用範圍與套用形式，取得選擇後再寫入設定。

<details>
<summary>展開安裝 Prompt</summary>

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
- 若要設為預設風格，將精簡規則加入工具支援的 rules、CLAUDE.md、AGENTS.md、GEMINI.md 或個人化指令。以套件安裝時，用 skill 名稱引用完整規則，因為套件的快取路徑會隨版本改變；只有單一 skill 放在固定位置時，才寫實際的 SKILL.md 路徑。
- 若目標工具不能讀取本機檔案，改提供可直接貼上的自足規則；無法代為操作設定介面時，提供文字與步驟，不宣稱已套用。
- 三項以上獨立的進度狀態或操作步驟用條列；有先後順序的步驟用編號，並列狀態、條件與檢查項目用項目符號，同時保留數值、條件、否定、時序、引用及不確定性。
- 完成後列出變更位置、作用範圍、啟用方式，以及實際完成與尚未完成的驗證。

請區分「全域可用」與「預設風格常駐」：只安裝套件或 skill，不代表每次回覆都會自動套用。
```

</details>

### 套件安裝

本儲存庫的根目錄是 marketplace，套件本身在 `plugins/asd-ste100-style/`。[套件 ZIP](dist/asd-ste100-style-plugin.zip) 解壓後的 `asd-ste100-style/` 資料夾有相同結構，下文稱為「套件資料夾」。

各工具的安裝範圍不同。只允許變更目前專案時，不要直接採用跨專案的設定：

| 工具 | 套件安裝的範圍 | 只限目前專案的做法 |
| --- | --- | --- |
| Claude Code | `--scope project` 寫進專案的 `.claude/settings.json`，可提交、隨專案共用，協作者仍須各自執行 install；`--scope local` 寫進 `.claude/settings.local.json`，只對你、這個專案有效，不提交；不加 `--scope` 時預設為 `user`，跨專案。 | `--scope local`（只影響自己）或 `--scope project`（團隊共用）。 |
| Codex CLI | `codex plugin add` 沒有 `--scope` 選項，安裝在使用者層級，更新該機器的 Codex 套件設定。官方文件另載明可用專案的 `.codex/config.toml` 控制外掛是否啟用，本專案沒有測。 | 改用下方的專案單一 skill。 |
| Antigravity CLI（`agy`） | 使用者層級的 `~/.gemini/config/plugins/`；`agy plugin install` 沒有專案 scope 選項。 | 把 `<套件資料夾>/plugins/asd-ste100-style` 複製為工作區的 `.agents/plugins/asd-ste100-style/`（官方文件載明，已實測可載入），或改用專案單一 skill。 |

**Claude Code，從 GitHub**，在目標專案的根目錄執行：

```powershell
claude plugin marketplace add felimet/asd-ste100-style --scope project
claude plugin install asd-ste100-style@asd-ste100-local --scope project
```

這組命令尚未用 1.3.0 驗證，見[已驗證與未驗證的範圍](#已驗證與未驗證的範圍)。

**Claude Code，從套件資料夾**，在目標專案的根目錄執行，並把 `<套件資料夾>` 換成絕對路徑。本機路徑只對這台電腦有效，所以用不提交、只對自己有效的 `--scope local`；Claude Code 直接從該資料夾讀取套件，安裝後不要刪除它：

```powershell
claude plugin marketplace add <套件資料夾> --scope local
claude plugin install asd-ste100-style@asd-ste100-local --scope local
```

`asd-ste100-local` 只是 marketplace 識別名稱，不表示套件必須在本機。

**Codex CLI**：

```powershell
codex plugin marketplace add <套件資料夾>
codex plugin add asd-ste100-style@asd-ste100-local
```

**Antigravity CLI** 從套件目錄本身安裝，不經過 marketplace：

```powershell
agy plugin validate <套件資料夾>/plugins/asd-ste100-style --strict
agy plugin install <套件資料夾>/plugins/asd-ste100-style
```

官方文件只列出 `plugin.json` 與 `.antigravity-plugin/plugin.json` 兩種 manifest 位置，也未記載 marketplace 檔案格式，因此本專案沒有為 Antigravity 另建 manifest 或 marketplace。

套件安裝後，預設對話風格仍由[常駐規則](#設為-ai-agent-的預設風格)決定。

#### 已驗證與未驗證的範圍

- **安裝測試**（2026-11-12，隔離的設定目錄；對象是 commit 2881cf4，不含 2026-11-13 對 `description` 與篇幅段落的修改；[紀錄](tests/install-validation-2026-11-12.md)）：
  - Claude Code 2.1.319：以 repo 路徑與 ZIP 解壓資料夾各安裝一次（`--scope local`），套件 enabled，含 1 個 skill。
  - Codex CLI 0.166.0：同樣兩種來源，安裝後模型可見的提示列出此 skill。
  - agy 1.5.6：以 repo 路徑執行 `agy plugin install`，安裝 1 個 skill。把 `plugins/asd-ste100-style` 複製到空專案的 `.agents/plugins/asd-ste100-style/` 後，`/asd-ste100-zh-tw` 讀取了 `.agents/plugins/asd-ste100-style/skills/asd-ste100-zh-tw/SKILL.md`。
- **格式檢查**（2026-11-13；[紀錄](tests/manifest-validation-2026-11-13.md)）：`claude plugin validate`（套件與 marketplace，`--strict`）與 `agy plugin validate --strict` 都通過。
- **沒有測**：
  - 從 GitHub 安裝 1.3.0。2026-11-12 的安裝測試時，遠端仍是 1.0.3 的舊佈局，推送後才能測。
  - Codex 與 agy 在使用者層級安裝後實際呼叫模型。
  - Antigravity IDE 的呼叫方式與常駐規則的實際載入行為。

### 單一 skill 安裝（選用）

將整個 `plugins/asd-ste100-style/skills/asd-ste100-zh-tw` 資料夾複製到目標專案的對應位置，保留其中的參考文件。

| 工具 | 專案內的安裝位置 | 呼叫方式 |
| --- | --- | --- |
| Claude Code | `.claude/skills/asd-ste100-zh-tw/` | `/asd-ste100-zh-tw` |
| Codex | `.agents/skills/asd-ste100-zh-tw/` | `$asd-ste100-zh-tw` |
| Antigravity（CLI 與 IDE） | `.agents/skills/asd-ste100-zh-tw/`（與 Codex 同一路徑） | CLI：`/asd-ste100-zh-tw`；IDE：官方文件未說明斜線呼叫，由 Agent 依 `description` 判斷，或在提示中指名此 skill |

也可解壓 [skill ZIP](dist/asd-ste100-zh-tw.zip)，將其中的 `asd-ste100-zh-tw` 資料夾放入上述位置。`SKILL.md` 應直接位於該資料夾內，避免多放一層同名資料夾。

以下 PowerShell 範例從本儲存庫根目錄執行，同時安裝到 Claude Code 與 Codex 的專案目錄；Antigravity 讀取 `.agents/skills/`，與 Codex 同一路徑，因此不需要第三個目的地。請將 `../target-project` 改為既有專案的路徑；同名目的地已存在時會停止。

```powershell
$skillSource = (Resolve-Path './plugins/asd-ste100-style/skills/asd-ste100-zh-tw').Path
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

此 skill 以文件指令運作，不需要額外的 API 金鑰或執行期套件。安裝格式可參閱 [Claude Code 文件](https://code.claude.com/docs/en/skills)、[Codex 文件](https://learn.chatgpt.com/docs/build-skills)與 [Antigravity Skills 文件](https://antigravity.google/docs/skills)。

只需跨專案使用單一 skill 時，可放在使用者目錄。這只改變可用範圍，不會自動建立常駐風格規則。

| 工具 | 使用者目錄 |
| --- | --- |
| Claude Code | `~/.claude/skills/asd-ste100-zh-tw/` |
| Codex | `~/.agents/skills/asd-ste100-zh-tw/` |
| Antigravity | `~/.gemini/config/skills/asd-ste100-zh-tw/`（IDE 舊版路徑 `~/.gemini/antigravity/skills/` 仍受支援） |

Antigravity 的官方文件未列出 `~/.agents/skills/`，是否讀取該路徑需確認；要在 Antigravity 使用，請放在上表的官方路徑。

### 呼叫 skill

在目標專案開啟工作階段，輸入 skill 名稱及任務。範例任務：「請用此風格回答：為什麼把工作拆成小步驟比較容易開始？」

| 工具與安裝形式 | 呼叫方式 |
| --- | --- |
| Claude Code，套件安裝 | `/asd-ste100-style:asd-ste100-zh-tw <任務>`（套件使用命名空間） |
| Claude Code，單一 skill | `/asd-ste100-zh-tw <任務>` |
| Antigravity CLI | `/asd-ste100-zh-tw <任務>` |
| Codex，套件安裝 | 官方文件的做法是在提示中輸入 `@` 提及外掛或其內含的 skill；`$` 選單是否列出外掛內的 skill，沒有驗證 |
| Codex，單一 skill | `$asd-ste100-zh-tw <任務>` |

需要固定格式、讀者背景或專案術語時，直接在同一個請求中說明。若工具未列出新安裝的 skill，重新開啟工作階段後再確認；Antigravity CLI 可執行 `/skills reload` 或開新對話。

**自動觸發不穩定。** 不加 `/skill` 前綴時，使用者點名 STE 或要求設為預設，三個 CLI 幾乎都會載入此 skill；只描述風格而沒有點名（例如「寫得清楚精確、一句一重點」）時，agy 與 Claude Code 合計只載入 4/10（舊版 2/10；事後分組，5 題、每格 1 次取樣，不是已測得的改善），Codex 5/5。需要穩定使用時，明確呼叫 skill；也可設為下一節的常駐規則，但該模式的效果沒有評測過。Codex 在 skill 很多的環境會把每則 `description` 截短（作者機器有 249 個 skill 時只顯示前 77 字），所以自動觸發的條件放在 `description` 的最前面。

## 設為 AI Agent 的預設風格

若希望 Agent 預設採用此風格，除了讓它能讀取 skill，還需要在該工具的個人化設定、rules 或指令檔加入預設規則。**全域安裝代表跨專案可用；全域常駐則需要全域指令來源載入這些規則。** 各工具的效果不同，Codex 上沒有觀察到好處，見[評測結果](#評測結果)。

| Agent | 專案預設規則 | 全域預設規則 |
| --- | --- | --- |
| Claude Code | `CLAUDE.md` 或 `.claude/rules/*.md` | `~/.claude/CLAUDE.md` 或 `~/.claude/rules/*.md` |
| Codex | `AGENTS.md` | `~/.codex/AGENTS.md` |
| Antigravity | `AGENTS.md` 或 `GEMINI.md`（或 `.agents/rules/*.md`） | `~/.gemini/AGENTS.md` 或 `~/.gemini/GEMINI.md` |
| Gemini CLI（舊版） | `GEMINI.md` | `~/.gemini/GEMINI.md` |
| 其他 Agent | 工具支援的專案 rules 或指令 | 工具支援的個人化設定、自訂指令或全域 rules |

表列為預設位置；自訂設定目錄、override 檔與載入規則仍以目標工具為準。幾個容易出錯的地方：

- Codex 的標準檔名是 `AGENTS.md`（複數），不是 `AGENT.md`。
- Antigravity 的 `AGENTS.md` 或 `GEMINI.md` 不需要 frontmatter，載入後常駐；`.agents/rules/*.md` 需要有效的 `trigger` frontmatter，設為 `always_on` 才每回合注入。
- Antigravity 的規則會累加而非互相覆寫，官方文件未定義 `AGENTS.md` 與 `GEMINI.md` 的優先順序；單檔上限 24 KB，全域與 `always_on` 規則共用 20,000 token 預算。這些載入行為只比對了官方文件，沒有在 agy 實測。
- `~/.gemini/GEMINI.md` 同時是 Gemini CLI 的全域檔，寫入會影響兩個工具。
- 專案的 `AGENTS.md` 也會被 Codex 讀取；只想讓 Antigravity 常駐此風格時，改用 `.agents/rules/` 下的規則檔並設 `trigger: always_on`。

設定方式依據 [Claude Code 指令與 rules 文件](https://code.claude.com/docs/en/memory)、[Codex AGENTS.md 文件](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Gemini CLI GEMINI.md 文件](https://geminicli.com/docs/cli/gemini-md/)及 [Antigravity Rules 文件](https://antigravity.google/docs/rules)。依 Google 於 2026-05-19 發布的[轉換公告](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)，Gemini CLI 已由 Antigravity CLI 接替，Google AI Pro、Ultra 與免費個人版自 2026-06-18 停止服務，Standard 或 Enterprise 授權的組織與付費 API key 不受此影響；本表保留 Gemini CLI 一列供舊環境參考。其他 Agent 是否原生支援此套件格式，需依其支援方式決定。

### 可複製的預設規則

將下列文字合併到所選範圍的設定中。最後一行由安裝 Agent 依安裝方式填寫：以套件安裝時寫帶套件命名空間的名稱 `asd-ste100-style:asd-ste100-zh-tw`（Claude Code 與 Codex 的安裝測試紀錄都是這個名稱），因為套件的快取路徑會隨版本改變；單一 skill 放在固定位置時，可改寫成實際的 SKILL.md 路徑。只能使用設定介面的工具，可保留自足規則並省略最後一行。

```text
對話預設採用 ASD-STE100 繁體中文風格（非官方改編），適用於問答、解釋、建議、討論與進度回報；依當次指定語言、語氣及格式調整。
使用者自己的指令（CLAUDE.md、AGENTS.md、persona 或當次要求）規定回覆順序、必備內容或語氣時，以其為準；數值、否定、條件、時序與不確定性的規則仍然適用。
未被上述指令規定時，先回答當前問題，再補必要理由、條件與限制。簡單問題直接回答，複雜問題保留足以支持判斷的細節。
使用清楚的主體、動作與一致術語；一句處理一個主要意思，依中文語意拆句，不套用英文 STE 的字數上限。保留數值、條件、否定、時序、引用及不確定性，區分已知、推論與尚未驗證；比較百分比時區分百分點與相對變化。
三項以上獨立的進度狀態或操作步驟用條列，進度狀態只有一至兩項時用句子；使用者問是非判斷時，列表前先用一句寫結論。有先後順序的步驟用編號，並列狀態、條件與檢查項目用項目符號。機制與推理保留連貫段落，短答不固定加標題或清單。使用者限定篇幅時，只交付符合限制的答案；補充說明與免責聲明只在會改變答案時才附。
此風格可延伸至文件表達：一般潤飾只更正可由已提供資訊唯一判定的錯誤並說明（指定純成品或固定格式時只交付正確內容）；無法唯一判定時詢問或標為待確認；保留指定創作文體；不把風格調整當成事實查核或外部操作的授權。
需要完整規則時，載入 asd-ste100-zh-tw skill。
```

這份範本的篇幅句仍是舊版，沒有換成 1.3.0 SKILL.md 的新篇幅段落。範本與 skill 同時載入時，兩套篇幅規則並存；這個組合沒有評測，常駐規則模式整體也沒有評測過。

設定後，在相同範圍開啟新工作階段，確認 Agent 讀到的規則來源，再以日常問答、接續提問及操作指引各試一題。只完成檔案安裝，不能當作預設規則已載入的證據；跨回合及跨工作階段的預設效果，仍取決於目標工具實際載入規則的方式。

## 用法示例

以下以單一 skill 的 Codex 語法示範。Claude Code 套件安裝時改用 `/asd-ste100-style:asd-ste100-zh-tw`，直接安裝單一 skill 時改用 `/asd-ste100-zh-tw`。

```text
$asd-ste100-zh-tw 用一個生活中的例子，說明「必要條件」和「充分條件」有什麼差別。

$asd-ste100-zh-tw 我有兩個選項：A 成本較低但需要手動整理，B 成本較高但能自動整理。每週只用一次，你會怎麼判斷？

$asd-ste100-zh-tw 目前只完成設定，測試還沒開始。請幫我向同事說明現在的進度。

$asd-ste100-zh-tw 說明以下操作順序：先確認檔案存在，再開啟檔案；不存在時回報錯誤並停止。
```

也可要求以圖解、HTML 或影片腳本說明內容：

```text
$asd-ste100-zh-tw 用簡短文字與 Mermaid 說明以下資料流程，區分處理順序與統計相關。

$asd-ste100-zh-tw 將以下內容寫成單檔 HTML 解說頁，清楚標示假設，讓核心說明在不操作互動元件時也能閱讀。

$asd-ste100-zh-tw 為以下主題撰寫解說影片腳本，分列畫面、旁白與字幕，保留必要條件及限制。
```

各種形式共用語意保留原則。實際圖像、網頁互動、影片渲染與配音，取決於執行環境提供的工具；腳本或程式碼本身不代表成品已完成或通過驗證。

## 評測結果

[`tests/`](tests/README.md) 有 agy（Gemini）、Codex 與 Claude Code 的小規模盲評，由另外兩家模型交叉評審。**證據只支持：agy 與 Claude Code 的回覆變短，評審對這兩者的可讀性評分較高。沒有觀察到必備內容滿足率提高，Codex 上沒有觀察到好處，也沒有人類讀者測試。**

### 載入 skill 對不載入

2026-11-12 的第二組保留題，24 題，每個版本每題生成 1 次，比較 1.1.1 的 SKILL.md 與不載入 skill。所有生成都明確呼叫 skill（`/asd-ste100-zh-tw` 或 `$asd-ste100-zh-tw`），沒有測自動觸發。括號為逐題配對差的 bootstrap 95% CI，只以 24 題重抽，僅供量級參考。

| 生成者 | 必備內容滿足率差（紀錄中稱 atoms） | 評審的可讀性分數差（1 至 5 分） | 平均字數（不載入 → 1.1.1） |
| --- | --- | --- | --- |
| agy（Gemini 3.8 Flash） | +0.040（−0.023 至 0.101） | +1.42（0.85 至 1.96） | 1838 → 975 |
| Codex | −0.027（−0.085 至 0.029） | −0.06（−0.31 至 0.21） | 575 → 563 |
| Claude Code（Sonnet） | +0.005（−0.031 至 0.045） | +0.29（0.02 至 0.56） | 713 → 553 |

- **agy**：回覆長度約減半，其中一部分來自整段重複減少，整段答案重複一次的比例由 0.375 降到 0.125。可讀性分數隨回覆縮短而提高（長度比與可讀性差的逐題 Spearman 相關 −0.95），所以這項提高不能當成縮短之外的另一項改善。
- **Codex**：可讀性沒有提高。2026-11-10 的保留題，必備內容滿足率差也略低（−0.045，CI −0.105 至 0.005），不能排除小幅退步。
- **Claude Code**：長度約少兩成。長度與可讀性的相關較弱（−0.28），+0.29 是否獨立於縮短仍未確定。

評測環境不同：agy 與 Codex 在作者的個人環境執行，會載入作者自己的全域指令（含與本 skill 重疊的風格規則）；Claude Code 以隔離設定執行，不載入 CLAUDE.md、使用者設定、plugins、hooks、MCP 與 auto memory。評審與生成者是同三個模型家族。

### 目前出貨的 1.3.0

上表量測的是 1.1.1。1.2.0 候選版的 SKILL.md 在 agy 端比 1.1.1 低 0.043（v120 − 1.1.1 的配對差，CI −0.090 至 −0.003），觸發事前登錄的退步規則，因此沒有採用，見[第二組保留題紀錄](tests/heldout2-eval-2026-11-12.md)。

1.3.0 的 SKILL.md 是 1.1.1 的文字，加上兩處由 2026-11-13 第三組保留題與觸發測試（[紀錄](tests/heldout3-eval-2026-11-13.md)）決定的修改：`description` 改為標示非官方改編，篇幅限制的句子改為整則回覆都要符合限制。上表沒有對 1.3.0 的檔案重做。出貨的 skill 資料夾（8 個檔案，含已修正內容錯誤的 references）與第三組 B 部分的 `len` 臂逐檔相同；第三組以明確呼叫測過它與 `ship` 臂的差別，沒有測自動觸發時的新篇幅段落，也沒有拿它與不載入 skill 比較。

- **篇幅限制**：18 題、每格 3 次取樣、3 個生成者。使用者限定篇幅的 12 題，篇幅遵守率平均由 0.58 升到 0.68（差 +0.093，CI 0.028 至 0.167）。必備內容滿足率沒有觀察到退步，但 Codex 在這 12 題為 −0.039（CI −0.111 至 0.019），不能排除小幅損失；遵守率提高的 5 題，必備內容平均降 0.031（事後分組，CI 包含 0）。評審的整體偏好沒有支持新段落較好（150 比 174 次）。採用後遵守率仍只有 0.53 至 0.81。
- **自動觸發**：見[呼叫 skill](#呼叫-skill)一節的說明；新舊 `description` 的差異來自第三組的 A 部分。

### 沒有測的項目

- 人類讀者對理解度或錯誤率的影響。
- 不明確呼叫（自動觸發）時，回覆長度與品質的整體效果。
- 常駐規則模式的效果。
- 對 1.3.0 與不載入 skill 的直接比較。
- 自動觸發時的新篇幅段落。

完整紀錄與限制見 [`tests/README.md`](tests/README.md) 的索引。判定可用 `python -I -B -X utf8 tests/eval/heldout2_decide.py tests/heldout2-eval-2026-11-12.json --sensitivity` 與 `python -I -B -X utf8 tests/eval/heldout3_decide.py tests/heldout3-eval-2026-11-13.json` 從結果檔重跑。

## 規範依據與範圍

本 skill 參考 [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf) 的部分寫作原則。英文詞典、詞性與句長限制不直接套用於中文；中文規則、讀檔條件與編輯界線均為本專案設計，不是正式 STE 合規依據。媒介延伸與無障礙要求的來源另列於[來源與規則對照](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/references/sources.md)。

文風調整不等於事實查核、專業審查或實際測試。一般潤飾只更正可由已提供資訊唯一判定的錯誤並說明；需要查證外部事實或修正其他內容時，請在任務中明確說明。

## 授權

本專案採用 [MIT License](LICENSE)，著作權人為 Jia-Ming Zhou（Felimet）。單一 skill 亦附有 [LICENSE](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/LICENSE)，下載 ZIP 內均包含授權文件。

此授權適用於本專案內容，不變更外部 ASD-STE100 標準文件的著作權或授權條件。

ASD-STE100 Simplified Technical English 是 ASD 的註冊商標。本專案為獨立的第三方、受 STE 啟發的中文表達指引，與 ASD、STEMG 無隸屬、合作、認證或背書關係，也不提供 STE 合規。

## 文件導覽

| 文件 | 內容 |
| --- | --- |
| [SKILL.md](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/SKILL.md) | 對話風格、情境調整與回覆檢查。 |
| [文件與操作指引](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/references/documents.md) | 文件改寫、審查與操作步驟的處理界線；僅在這類任務時讀取。 |
| [對話與改寫範例](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/references/examples.md) | 問答、建議、接續討論、進度回報，以及文件延伸示例。 |
| [術語與語意控制](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/references/terminology.md) | 情態、量詞、領域術語及量值比較。 |
| [媒介規則](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/references/formats.md) | 圖解、HTML 與解說影片的表達原則。 |
| [來源與規則對照](plugins/asd-ste100-style/skills/asd-ste100-zh-tw/references/sources.md) | 來源連結與英文標準原則的中文改編對照。 |
| [評測紀錄索引](tests/README.md) | 各版本的盲評、保留題、安裝測試與勘誤。 |
| [AGENTS.md](AGENTS.md) | 維護者的驗證命令、重建 ZIP 與評測慣例。 |
