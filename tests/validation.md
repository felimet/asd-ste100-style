# 通用版驗證紀錄

日期：2026-11-04。驗證對象為 `skills/asd-ste100-zh-tw` 的通用版本。

## 移除範圍

- 移除固定用字替換、個人禁詞與符號禁令。用詞、標點與排版依當次讀者、領域及文件慣例決定。
- 將主規則與示例中的特定研究領域改為通用設備、訊號與測試樣本；不預設身分、職業、硬體或作業系統。
- 公開文件不記錄個人本機目錄；安裝範例使用可調整的相對路徑。
- 保留繁體中文用途、STE 語意保留原則、真實來源署名，以及當次任務指定的術語與格式。

## 格式、安裝與封裝

實際執行 skill-creator 的 `quick_validate.py`，並以 Python 檢查 UTF-8、相對連結、metadata、套件內容與 ZIP CRC／位元組一致性。README 的 PowerShell 安裝範例已在隔離目錄執行，兩個平台安裝目錄的六個檔案均與來源一致，同名目的地會拒絕覆寫。

```text
Skill is valid!
README installation: PASS; two platform copies match all 6 source files; existing target rejected
ZIP CRC / inventory / byte identity: PASS; 6 files
```

封裝 ZIP 只含六個 skill 檔案，不含個人設定、測試歷史、來源 PDF 或執行環境。

## 行為試跑

重新執行 [當前十一個案例](cases.md)，實際答案見 [forward-test.md](forward-test.md)，完整輸入、輸出與六個檔案的 SHA-256 見 [generic-results.json](generic-results.json)。

T1–T9 檢查一般說明、研究限制、程序條件、同步操作、未知原因、圖解、HTML 文案、合規邊界及必要／充分條件。G1 檢查當次專案譯名能否優先保留；G2 檢查是否避免猜測未提供的個人電腦環境。主 agent 讀取實際輸出並對照原文，G1 的指定術語另以程式檢查。

另一 agent 唯讀核對六個 skill 檔案與 README，未發現剩餘個人設定或本輪新增的語意衝突。此結論限於指定文件，不保證所有輸入的結果。

## 歷史與限制

先前驗證檔案在覆寫前另行備份；納用階段的 JSON 結果保留歷史標記與原始案例正文，不將舊情境改寫成新的實測答案。歷史虛構案例不是執行 skill 時的預設背景，也不包含在 skill ZIP。

本輪為同一 agent 人工載入後按題單次作答，並非每題建立新工作階段；沒有可核對的模型識別、取樣設定、重複抽樣、盲評或統計可靠率。未驗證兩平台原生載入、自動發現、Mermaid 渲染、HTML 瀏覽器互動或影片輸出。此 skill 是非官方中文改編，不提供正式 STE 認證。

## 來源文件與符號整理

`sources.md` 簡化為來源連結及條文對照，移除下載資訊、查核工具與開發歷程。主檔及術語文件僅將全形斜線改為 ASCII `/`，其餘文字保持一致。開發與驗證紀錄不放入 skill 套件。

本次重新執行格式、相對連結、符號掃描及 ZIP CRC/位元組一致性檢查，均通過。文件複核確認使用規則完整。此輪未重跑十一個行為案例；`generic-results.json` 的輸出與內容雜湊保留為先前通用版本的紀錄，不視為整理後版本的重測結果。
