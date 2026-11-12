# 1.3.0 安裝測試（2026-11-12）

對象是 commit 2881cf4 的 repo（marketplace 根目錄）與同一 commit 重建的 `dist/asd-ste100-style-plugin.zip` 解壓後的 `asd-ste100-style/` 資料夾。安裝都在隔離的設定目錄進行（`CLAUDE_CONFIG_DIR`、`CODEX_HOME`、agy 用 `USERPROFILE`），沒有寫入作者實際使用的設定。

## 結果

| 工具與版本 | 安裝命令 | 來源 | 結果 |
| --- | --- | --- | --- |
| Claude Code 2.1.319 | `claude plugin marketplace add <來源> --scope local`，`claude plugin install asd-ste100-style@asd-ste100-local --scope local` | repo 路徑、ZIP 解壓資料夾 | 兩者都成功；`claude plugin list` 顯示 1.3.0、enabled；`claude plugin details` 列出 1 個 skill（`asd-ste100-zh-tw`），常駐成本約 38 tokens、呼叫時約 890 tokens（工具的估計值）。 |
| Codex CLI 0.166.0 | `codex plugin marketplace add <來源>`，`codex plugin add asd-ste100-style@asd-ste100-local` | repo 路徑、ZIP 解壓資料夾 | 兩者都成功；`codex plugin list` 顯示 installed, enabled、1.3.0；快取目錄有 11 個檔案（兩份 manifest、兩份 LICENSE、SKILL.md、`agents/openai.yaml`、5 份 references）。 |
| agy 1.5.6 | `agy plugin install plugins/asd-ste100-style` | repo 路徑 | 成功，安裝 1 個 skill 到 `<隔離目錄>/.gemini/config/plugins/asd-ste100-style`；`agy plugin list` 顯示 1.3.0、enabled。 |

## 執行時載入

- Claude Code：`claude -p --plugin-dir <安裝後的快取目錄> --setting-sources project,local --strict-mcp-config`，提示為 `/asd-ste100-style:asd-ste100-zh-tw 用一句話說明 DNS 是什麼。`。stream-json 的 init 事件列出 plugin `asd-ste100-style` 1.3.0 與 skill `asd-ste100-style:asd-ste100-zh-tw`，回覆正常產生。
- Codex：`codex debug prompt-input`（隔離的 `CODEX_HOME`，不呼叫模型）輸出的模型可見提示，列出 `asd-ste100-style:asd-ste100-zh-tw` 與其 description，路徑指向安裝後的快取。
- agy：把 `plugins/asd-ste100-style` 複製到空專案的 `.agents/plugins/asd-ste100-style/`，執行 `agy -p "/asd-ste100-zh-tw 用一句話說明 DNS 是什麼。" --model gemini-3.8-flash-high`。工具紀錄顯示讀取了 `.agents/plugins/asd-ste100-style/skills/asd-ste100-zh-tw/SKILL.md`，回覆正常產生。這證實工作區外掛路徑可用；使用者層級安裝後的執行時載入沒有測（隔離目錄沒有登入資訊）。

## 沒有測

- 從 GitHub 安裝（`claude plugin marketplace add felimet/asd-ste100-style`）：遠端仍是 1.0.3 的舊佈局，要推送後才能測。
- Codex 與 agy 在使用者層級安裝後實際呼叫模型：隔離目錄沒有登入資訊，而複製登入檔不在允許範圍內。Codex 以 `debug prompt-input` 代替，agy 以工作區外掛路徑代替。
- 自動觸發：見第三組保留題紀錄的 A 部分。
