# 套件與預設風格指引驗證

日期：2026-11-04。

本檔記錄對話風格定位調整前的套件版本，結果對應 `package-results.json` 的版本雜湊。調整後的驗證見 [conversation-style-validation.md](conversation-style-validation.md)。

## 封裝與註冊檔

- `plugin.json` 使用 Agent Plugins 1.0.0 通用格式，作為 Codex 套件入口；已以官方 JSON Schema 驗證。
- `.claude-plugin/plugin.json` 提供 Claude Code 套件識別，使用預設 `skills/` 探索。
- `.claude-plugin/marketplace.json` 與 `.agents/plugins/marketplace.json` 分別登錄同根套件。兩者的套件名稱、來源位置與版本對應一致。
- 兩個平台共用 `skills/asd-ste100-zh-tw/`。套件未加入 hooks、MCP server、個人路徑或自動修改設定的安裝腳本。

選用通用 `plugin.json`，是為了使用 Codex 現行文件建議的格式；Claude Code 則保留其原生描述檔。沒有複製第二套 skill 或建立不必要的 Codex 相容覆蓋檔。

## 實際執行的檢查

| 檢查 | 實際結果 |
| --- | --- |
| Agent Plugins 官方 schema | `Portable Agent Plugins schema: PASS` |
| Claude Code 2.1.316，plugin manifest | `claude plugin validate .claude-plugin/plugin.json --strict --json`：success 為 true，manifest errors/warnings 均為空。 |
| Claude Code 2.1.316，marketplace manifest | `claude plugin validate .claude-plugin/marketplace.json --strict --json`：success 為 true，manifest errors/warnings 均為空。 |
| Skill frontmatter | `quick_validate.py` 回傳 `Skill is valid!`。 |
| README 單一 skill 安裝範例 | 隔離複製至兩平台目錄，六個檔案均與來源相同；既有目的地會拒絕覆寫。套件安裝命令只做語法及 CLI 介面核對，未實際執行安裝。 |
| 來源與路徑 | portable/Claude 描述檔識別一致，兩個 marketplace 均指向同一套件根目錄。 |
| ZIP | 單一 skill ZIP 為六檔，套件 ZIP 為十一檔；兩者 CRC、檔案清單與逐檔位元組比對均通過。 |
| 文件 | README 的九個本機連結/錨點均有效，使用 ASCII `/`，未加入個人設定或先前已移除的內容。 |

官方依據：[Agent Plugins Schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)、[OpenAI 套件文件](https://developers.openai.com/plugins/build/plugins)、[Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)、[Claude Code marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)。

## 文字情境試跑

輸入見 [package-cases.json](package-cases.json)，完整答案、人工檢查項目與版本雜湊見 [package-results.json](package-results.json)。

| 案例 | 檢查內容 | 觀察 |
| --- | --- | --- |
| P1 | 尚未指定安裝形式 | 先詢問 Agent、作用範圍與按需/常駐/個人化形式，並等待回答。 |
| P2 | 已指定 Codex、僅專案、按需 | 沿用選擇，說明所列套件命令的範圍限制，再請使用者選替代方式，未自行升為全域。 |
| L1 | 嚴格操作程序 | 以編號區分步驟，保留檔案不存在時的錯誤處置及順序。 |
| L2 | 三項必要條件 | 使用三項條列，保留必須全部成立與不保證成功的限制。 |
| L3 | 連貫機制說明 | 使用單一段落，保留條件分支、可能性及版本比對要求。 |

文件複核曾指出：安裝 Prompt 的套件優先規則可能把專案範圍擴成跨專案設定。已修正為先保留所選範圍、不相容時交由使用者選擇，並新增 P2 回歸案例。寫作案例使用未改動的既有輸入，Prompt 案例則依修訂後的輸入重新作答。

## 驗證界線

- 未變更全域套件、rules 或個人化設定，也未執行公開發布。
- Codex CLI 0.166.0 的 `plugin list --marketplace asd-ste100-local --available --json` 回傳 installed/available 均為空。這不證明套件已被該 CLI 發現或載入；本輪僅完成其官方封裝格式與 catalog 路徑驗證，原生安裝載入仍待實測。
- Claude 的 manifest 嚴格驗證不等於執行期載入或公開目錄上架驗收。驗證器另提示公開目錄所需的授權檔與圖示尚未提供；本輪沒有自行指定授權或宣稱可直接公開上架。
- 五個案例為同一獨立 agent 人工載入後單次作答，再由主 agent 對照。模型識別及取樣設定不可得，沒有跨模型、盲評或長對話可靠率結論。
