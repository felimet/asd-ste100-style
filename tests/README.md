# 測試紀錄說明

- 本目錄的案例與結果檔記錄各版本當時的人工試跑。結果檔內的版本雜湊對應當時的 SKILL.md，早於 1.0.3 的紀錄不代表目前版本。
- 這些紀錄由同一個 agent 作答並評分，沒有「未載入 skill」的對照組，樣本數小，只能作為回歸檢查，不能證明風格改善了理解。
- `ab-eval-2026-11-08.md` 是較嚴謹的盲評比較（無 skill、舊版、新版），結果與限制見該檔。
- `cli-eval-2026-11-09.md` 以 agy（Gemini 4 Argon medium）與 Codex CLI 互為生成者與評審，比較 5 個版本臂與自動觸發；程式與題目在 `eval/`。結論、限制與資料處理紀錄見該檔。
- 套件封裝可用 `scripts/build-dist.ps1 -Check` 重現檢查；CI 於 `.github/workflows/validate.yml`。
