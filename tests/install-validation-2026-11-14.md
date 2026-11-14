# 從 GitHub 安裝 1.3.0 的測試（2026-11-14）

對象是 GitHub 上 `felimet/asd-ste100-style` 的 `main`。測試時它指向 commit `456b281`。這是 1.3.0 推送後，第一次從 GitHub 來源安裝 Claude Code 套件。

## 條件

- Claude Code 2.1.323，Windows 11，在 Git Bash 執行。
- 每個範圍使用一個空的 `CLAUDE_CONFIG_DIR`，與一個剛執行 `git init` 的空專案。兩個範圍互不共用。
- 所用的子命令不呼叫模型。設定目錄沒有登入資訊，也沒有複製任何登入檔，所以沒有實際呼叫 skill。
- CLI 輸出 `SSH not configured, cloning via HTTPS`，所以簡寫 `felimet/asd-ste100-style` 在這台電腦走 HTTPS。沒有檢查 Git 是否套用了憑證。
- 在空專案內，依序執行下列命令。前兩條與 README 相同，只替換 `--scope` 的值：

```text
claude plugin marketplace add felimet/asd-ste100-style --scope <project 或 local>
claude plugin install asd-ste100-style@asd-ste100-local --scope <project 或 local>
claude plugin list
claude plugin list --json
claude plugin details asd-ste100-style
```

- 接著列出專案內新增的檔案（不含 `.git`），並讀取設定目錄內的 `plugins/installed_plugins.json`。

## 結果

兩個範圍的每一步結束碼都是 0。

| 步驟 | `--scope project` | `--scope local` |
| --- | --- | --- |
| `marketplace add` | 成功。輸出 `declared in project settings`。 | 成功。輸出 `declared in local settings`。 |
| `install` | 成功。輸出 `(scope: project)`。 | 成功。輸出 `(scope: local)`。 |
| `plugin list` | `asd-ste100-style@asd-ste100-local`，輸出 `Version: 1.3.0`、`Scope: project`、`Status: ✔ enabled`。 | 同左，`Scope: local`。 |
| 專案內新增的檔案（不含 `.git`） | 只有 `.claude/settings.json`。 | 只有 `.claude/settings.local.json`。 |
| `plugin details` | `Skills (1)`：`asd-ste100-zh-tw`。常駐約 40 token，呼叫時約 930 token（工具的估計值）。 | 同左。 |
| `installed_plugins.json` 的 `gitCommitSha` | `456b28187d6912cb6f18d5c5ae216803d906e841` | 同左 |
| `plugin list --json` 的 `projectEnabled` | `true` | `false` |

兩個範圍寫進專案的檔案內容相同，只有檔名不同：

```json
{
  "extraKnownMarketplaces": {
    "asd-ste100-local": {
      "source": { "source": "github", "repo": "felimet/asd-ste100-style" }
    }
  },
  "enabledPlugins": {
    "asd-ste100-style@asd-ste100-local": true
  }
}
```

`--scope project` 的輸出摘錄。`[…]` 標示省略的進度訊息；`--scope local` 只有 `project` 換成 `local`：

```text
$ claude plugin marketplace add felimet/asd-ste100-style --scope project
Adding marketplace…SSH not configured, cloning via HTTPS: https://github.com/felimet/asd-ste100-style.git
[…]
Clone complete, validating marketplace…
[…]
✔ Successfully added marketplace: asd-ste100-local (declared in project settings)

$ claude plugin install asd-ste100-style@asd-ste100-local --scope project
Installing plugin "asd-ste100-style@asd-ste100-local"...✔ Successfully installed plugin: asd-ste100-style@asd-ste100-local (scope: project)
```

`plugin list --json` 的 `projectEnabled` 在兩個範圍不同。本次沒有查證這個欄位的定義，所以不推論它的意義。兩個範圍的 `plugin list` 都顯示 enabled。

## 寫入位置

- 兩個範圍都在設定目錄寫入 marketplace 的 clone（`plugins/marketplaces/`）、套件快取（`plugins/cache/`）、`plugins/installed_plugins.json`、`plugins/known_marketplaces.json`，以及 `.claude.json` 與它的備份。實際使用時，這些檔案落在使用者層級的設定目錄。
- `--scope` 只決定啟用設定（`enabledPlugins`）與 marketplace 宣告（`extraKnownMarketplaces`）寫進哪個專案檔。
- 安裝不會寫入 `.gitignore`。這台電腦的使用者層級 Git ignore 規則已包含 `.claude/settings.local.json`，所以 `git status` 沒有列出它。另一次重跑改用空的 `core.excludesFile` 後，`git status` 在兩個範圍都列出 `?? .claude/`。

## 獨立重跑

一個沒有看過本次日誌的審查者，用 README 的命令在全新的暫時目錄重跑兩個範圍。結束碼、訊息、版本、範圍、新增的檔案、設定檔內容、`gitCommitSha`、skill 數量、token 估計與 `projectEnabled` 都與上表一致。這個審查者與本次測試屬同一模型家族。

## 沒有測

- 實際呼叫 skill 或模型。
- `--scope user`（不加 `--scope` 時的預設值）。
- 協作者在另一台電腦取得含 `.claude/settings.json` 的專案後，執行 install 的流程。官方文件說明協作者要各自執行 install，本次沒有驗證。
- 測試前後，正式設定目錄是否被改動。隔離只依賴 `CLAUDE_CONFIG_DIR`，沒有另外檢查。
- 其他作業系統、其他 Claude Code 版本、SSH 來源。
- Codex 與 Antigravity 在 commit `456b281` 的安裝。README 沒有從 GitHub 安裝它們。它們的安裝測試見 [2026-11-12 的紀錄](install-validation-2026-11-12.md)，對象是更早的 commit。

## 清理

測試用的設定目錄、專案與原始日誌已在記錄完成後刪除。原始日誌含本機路徑，沒有納入倉庫。
