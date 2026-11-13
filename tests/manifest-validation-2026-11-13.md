# 套件格式檢查（2026-11-13）

對象是 commit efe90dd（1.3.0）的工作目錄。三條命令都是唯讀的格式檢查，沒有安裝套件、沒有呼叫模型，也沒有變更設定。命令在 repo 根目錄執行。

## 結果

| 工具與版本 | 命令 | 結果 |
| --- | --- | --- |
| agy 1.5.8 | `agy plugin validate plugins/asd-ste100-style --strict` | 通過，退出碼 0；元件為 skills 1、其餘 0；兩則 note（`$schema` 載入方式說明、未宣告 logo），`--strict` 未將其升為錯誤。 |
| Claude Code 2.1.323 | `claude plugin validate plugins/asd-ste100-style --strict` | 通過，退出碼 0；目錄檢查有一則 `ICON_MISSING` warning（沒有圖示），不影響結果。 |
| Claude Code 2.1.323 | `claude plugin validate . --strict`（marketplace） | 通過，退出碼 0。 |

## 沒有測

- 安裝與執行時載入：見 [install-validation-2026-11-12.md](install-validation-2026-11-12.md)。
- 官方 marketplace 上架：`validate` 通過不等於可上架；`ICON_MISSING` 與 agy 的 logo note 都指出套件沒有圖示。
- 這次沒有檢查 ZIP 解壓後的目錄；`-Check` 只比對 ZIP 與工作目錄檔案相同（`scripts/build-dist.ps1 -Check`）。
