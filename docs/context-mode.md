# context-mode：從大型 Log 找到錯誤

這次完成的是可重跑的本機 MCP 實驗，不需要修改全域 agent 設定。合成 BitBake log 含 2,224 行、三個獨特錯誤標記；腳本透過真實 JSON-RPC 呼叫 `ctx_index`、`ctx_search`、`ctx_stats`，逐一驗證 marker 與診斷上下文。

## 先玩實驗

從專案根目錄執行：

```sh
.venv/bin/python context/generate_fixture.py
.venv/bin/python context/mcp_experiment.py
```

看終端中的單次與批次搜尋結果，再開啟 [benchmark.json](../evidence/context/benchmark.json) 與 [完整收據](../evidence/context/mcp_receipts.json)。三個案例分別模擬下載雜湊不符、seccomp 阻擋、DTS 語法錯誤；都是合成資料，不是你的真實硬體故障。

本版測得原始 log 為 213,030 UTF-8 bytes，三個 marker 的一次批次檢索輸出為 5,079 bytes。這兩個內容大小相差 97.62%，不代表整段 agent 對話或 API 費用減少相同比例；索引回應、三次個別搜尋、tool schema 與指令也會占用上下文。

## 特色與用法

context-mode 將文字切塊存入 SQLite FTS5，再回傳與查詢相關的片段。你可以先留完整 log 在磁碟，用關鍵字找到小段診斷，再回到原始檔核對。這比只看長 log 的尾端更容易找到分散的錯誤。

- 一次找多個錯誤：`ctx_search` 使用 `queries` 陣列。本實驗先單獨查三次，再批次查一次，確認每個已知錯誤都存在。
- 指定來源：本版以 `synthetic-bitbake-build-log` 為 source，避免不同文件混在一起。
- 換成自己的 log：複製實驗腳本，調整 `FIXTURE_PATH`、marker 與預期周邊文字；保留原始檔，不把未命中當作沒有錯誤。

本實驗只呼叫索引、搜尋和統計工具。工具本身還提供執行等功能，這次沒有替你設定 agent hooks 或在目前對話中自動攔截其他工具。

## 專案內隔離

腳本的子行程設定三個環境變數，全部指向專案內 `evidence/context/.storage/`：

| 變數 | 本版查核用途 |
| --- | --- |
| `CONTEXT_MODE_DIR` | content／session SQLite 儲存 |
| `CONTEXT_MODE_DATA_DIR` | adapter 的 context-mode 儲存與記憶目錄 |
| `CLAUDE_CONFIG_DIR` | 本版 `ctx_stats` lifetime analytics 的記憶中繼資料掃描根目錄 |

這些變數只傳給 MCP 子行程，不改你的全域設定檔。只設定第一個變數時，統計工具仍讀到既有專案的記憶分類與數量；補上完整隔離後重跑，交付收據已不含那些中繼資料。此行為查核來自已安裝 `context-mode@1.0.169` 的 `build/session/analytics.js` 與 `build/adapters/base.js`，升版後需要重新驗證。

## 驗證與限制

```sh
.venv/bin/python -m pytest -q tests/test_context_client.py
```

回歸測試使用會送出半段 JSON 的子行程，確認 0.1 秒 timeout 不會被缺少換行的輸出拖住。實作以非阻塞 bytes 讀取與 selector 處理；stderr 寫入本機檔案，以避免尚未觀測到、但審查可識別的 pipe 填滿風險。

伺服器在請求期間傳來的通知或其他非當前回應，會保留為收據中的 `server_message`，方便追查，而不是直接丟棄。此示範一次只送一個 request，沒有實作並行請求或伺服器反向請求處理。關閉時先 terminate，逾時才 kill，並等待子行程結束；另有忽略 SIGTERM 的真實子行程回歸測試。

資料的 bytes 與 Unicode 字元數是直接量測；沒有使用模型 tokenizer，所以不估算 token 數。`ctx_stats` 的 tokens／金額／session 延長字串保留在原始收據供核對，是上游估算，不作本次驗收結果。

這份合成 log 重複且有結構，容易檢索；結果不能推廣為任何真實建置都能省 97.62%。搜尋可能漏掉未知錯誤，也不能取代完整 log、實際編譯或硬體驗證。來源：[context-mode 官方 repo](https://github.com/mksglu/context-mode)。
