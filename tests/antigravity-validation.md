# Google Antigravity 支援驗證

日期：2026-11-08。

本檔記錄 README 新增的 Antigravity（`agy` CLI 與 IDE）說明所做的核對。範圍限於官方文件比對與唯讀的本機命令；沒有安裝套件、沒有呼叫模型，也沒有變更全域設定。

## 實際執行的檢查

| 檢查 | 實際結果 |
| --- | --- |
| 官方文件逐項比對 | 重新讀取下列四頁，核對 README 中的 skill 路徑、規則檔路徑、24 KB 與 20,000 token 上限、`/skills reload`、manifest 位置與 `agy plugin` 命令。除下方兩項已修正的敘述外，其餘均與文件一致。 |
| `agy --version` | `1.5.3` |
| `agy --help`、`agy plugin --help` | 子命令為 `list`、`import`、`install`、`uninstall`、`enable`、`disable`、`validate [path] [--strict] [--json]`、`link`；`install` 沒有 scope 選項。 |
| `agy plugin validate .`（儲存庫根目錄） | 通過，退出碼 0；元件為 skills 1、其餘 0；兩則 note（`$schema` 載入方式說明、未宣告 logo）。 |
| `agy plugin validate . --json`、`--strict`、`--strict --json` | 同樣通過，退出碼 0，finding 僅有上述兩則 note，`--strict` 未將其升為錯誤。 |
| 重建 ZIP 後的驗證 | 將重建的 `dist/asd-ste100-style-plugin.zip` 解壓至全新暫存目錄，`agy plugin validate <dir> --strict` 通過（退出碼 0，內容同上）；暫存目錄已刪除。 |
| Claude Code 2.1.319，同一份解壓目錄 | `claude plugin validate <dir>/.claude-plugin/plugin.json --strict --json`：success 為 true，manifest errors/warnings/notes 均為空；目錄檢查另有一則 `ICON_MISSING` warning（非 blocking）。 |
| `scripts/build-dist.ps1` | 重建兩個 ZIP 後 `-Check` 通過；重建前的 `-Check` 偵測到舊 ZIP 的 README 版本落後，且 `SKILL.md`、`openai.yaml`、`sources.md`、`terminology.md` 以 CRLF 封裝，其餘檔案為 LF。重建後兩次建置的 ZIP 雜湊相同。 |

README 修正：

- 原稿寫「Antigravity 不讀取 `~/.agents/skills/`」。官方 Skills 文件只是未列出該路徑，沒有明言不讀取，已改為「未列出，是否讀取需確認」。
- 原稿只說 `agy plugin install` 無專案 scope。外掛文件另載明可把外掛資料夾放進工作區 `.agents/plugins/` 而僅在該專案啟用，已補上並標示尚未測試。

## 未執行的項目

- `agy plugin install`、`import`、`link`、`enable`：未執行，因此不知道此套件實際安裝後是否被 CLI 或 IDE 載入。
- skill 探索：`agy` 沒有不需模型的唯讀「列出 skills」命令（列出的子命令只有 `agents`、`models`、`plugin` 等），而執行 `-p` 或互動工作階段需要登入與模型呼叫，且可能在使用者目錄留下對話狀態（未確認），因此未在暫存專案中測試 `.agents/skills/` 的實際探索。`agy plugin validate` 只確認套件內 skills 數量為 1，不證明 workspace skill 會被載入。
- `/asd-ste100-zh-tw` 斜線呼叫、`/skills reload`：只比對文件，未在 CLI 實測。IDE 的呼叫方式官方文件未說明，也未實測。
- 常駐規則載入：未寫入任何 `AGENTS.md`、`GEMINI.md`、`.agents/rules/*.md`，未驗證 `trigger: always_on` 注入、24 KB 截斷或 20,000 token 預算降級的實際行為。
- 模型行為：未用 Antigravity 內的任何模型驗證本風格的輸出，沒有跨模型或長對話結論。
- 官方 marketplace 上架與簽核：未涉及；`agy plugin validate` 通過不等於可上架。官方文件指出上架需要 `displayName`、`version`、`logo`、`author` 等欄位及 `README.md`，本套件的 `plugin.json` 未宣告 logo。

## 文件來源

文件以網頁擷取工具讀取，工具回傳的是摘要與短引文，不是逐字全文；路徑、數字與觸發值已與頁面摘要一一核對，但未做原始 HTML 逐字比對。

- [Antigravity Skills](https://antigravity.google/docs/skills)：工作區 `.agents/skills/`、全域 `~/.gemini/config/skills/`、IDE 舊版 `~/.gemini/antigravity/skills/`、CLI 轉為 `/<skill-name>` 與 `/skills reload`；未列出 `~/.agents/skills/`。
- [Antigravity Rules](https://antigravity.google/docs/rules)：`AGENTS.md`、`GEMINI.md`、`.agents/rules/*.md`、`trigger` 值、單檔 24,000 bytes、全域與 `always_on` 共用 20,000 token、規則累加且未定義優先順序。
- [Antigravity Plugins（CLI 分頁）](https://antigravity.google/docs/plugins?tab=cli)：`agy plugin` 子命令、`~/.gemini/config/plugins/`、工作區 `.agents/plugins/`、`validate --strict`。
- [Build Antigravity Plugins](https://antigravity.google/docs/build-plugins)：`plugin.json` 與 `.antigravity-plugin/plugin.json` 兩個 manifest 位置、plugin 內 `skills/<name>/SKILL.md` 結構、上架要求。
- [Gemini CLI GEMINI.md](https://geminicli.com/docs/cli/gemini-md/)：`~/.gemini/GEMINI.md` 為 Gemini CLI 的全域指令檔，用於 README 的共用檔案警告。
