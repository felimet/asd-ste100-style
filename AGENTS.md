# asd-ste100-style

給 Claude Code、Codex 與 Antigravity 使用的繁體中文對話風格套件（skill `asd-ste100-zh-tw`），以 public GitHub repo 與 `dist/` 內的 ZIP 發行；skill 本身是純文件指令，沒有執行期程式。

本檔的專案事實與慣例優先於全域指令；全域指令的「風險」一節不因本檔放寬。

## 指令

- 驗證（宣告完成前必須通過）：`pwsh -NoProfile -File scripts/build-dist.ps1 -Check`。需要 PowerShell 7（`pwsh`），Windows PowerShell 5.1 會失敗。
- 重建 ZIP：`pwsh -NoProfile -File scripts/build-dist.ps1`
- 套件格式檢查：`claude plugin validate plugins/asd-ste100-style --strict`、`claude plugin validate . --strict`（marketplace）、`agy plugin validate plugins/asd-ste100-style --strict`
- 評測統計自測：`python -I -B tests/eval/run_cli_eval.py selftest`、`python -I -B tests/eval/heldout2_decide.py selftest` 與 `python -I -B tests/eval/heldout3_decide.py selftest`
- 第二組保留題的判定：`python -I -B -X utf8 tests/eval/heldout2_decide.py tests/heldout2-eval-2026-11-12.json --sensitivity`
- 第三組保留題與觸發測試的判定：`python -I -B -X utf8 tests/eval/heldout3_decide.py tests/heldout3-eval-2026-11-13.json`；協定引用的門檻校準數字：`python -I -B tests/eval/heldout3_decide.py simulate`
- 跨 CLI 評測：`python -I -X utf8 tests/eval/run_cli_eval.py setup|gen|judge|report|trigger|trigreport ...`，參數見該檔開頭與各組的 protocol。會呼叫 agy、Codex、Claude 並消耗額度；`--work` 必須在 repo 外（程式會拒絕 repo 內的路徑）。Windows 上先把 `CODEX_BIN` 設為實際使用的 codex 執行檔。第三組的整套執行腳本在 `tests/eval/heldout3_run/`（Git Bash：先 `python build_trig_arms.py <E4>` 建三個 description 臂，再 `E4=<repo 外目錄> CODEX_BIN=<codex.exe> bash run_trig.sh`，然後 `build_ab_arms.py`、`run_ab.sh`、`consolidate.py`）。

## 慣例

- repo 根目錄是 marketplace（`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`），套件本身在 `plugins/asd-ste100-style/`。本檔與 `CLAUDE.md` 只屬於 repo，不在套件目錄內。
- `dist/*.zip` 是產生檔但進版控。改動 `README.md`、`LICENSE`、兩個 marketplace 檔或 `plugins/asd-ste100-style/` 底下任何檔案後要重建，CI 會用 `-Check` 擋下不同步的 ZIP。只打包已追蹤的檔案，新檔要先 `git add`。
- 版本號寫在 `plugins/asd-ste100-style/plugin.json` 與 `plugins/asd-ste100-style/.claude-plugin/plugin.json` 兩處，必須一致（CI 檢查）。
- README 與 `references/sources.md` 的效果宣稱必須對得上 `tests/` 裡的評測紀錄；沒有評測支持的效果不寫成事實。
- 評測的保留題用過一次就算用掉。要用評測決定版本時，先寫定新的保留題與判定規則，再看結果。
- `tests/*-results.json`、`tests/*-eval-*.json` 與已發布的評測報告是當時的紀錄，事後不改；更正寫進新的勘誤檔。
- skill 與 README 用繁體中文（臺灣用語）；commit message、程式碼與註解用英文。

## 界線

- `.work/`（gitignored，只在主 checkout）放 ASD-STE100 Issue 9 的 PDF 與文字檔，不進版控、不打包。
- push、打 tag、發 GitHub release 之前先問。

## 參考

- 標準原文：`d:/_mydev/asd-ste100-style/.work/ASD-STE100_ISSUE9.txt`（含 `[PDF page N]` 頁碼標記）。
- 評測紀錄索引：`tests/README.md`。
