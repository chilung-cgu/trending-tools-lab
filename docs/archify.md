# Archify：把 Crawler 程式變成互動流程圖

開啟 [流程圖](../artifacts/archify/crawler.html)，就能看你的 crawler 如何抓取、重試、保存成功快照及處理失敗。HTML 內含圖表與互動資源，不需要登入服務，也不依賴外部 CDN。

## 先玩成品

執行 `sh scripts/serve.sh`，從 `http://127.0.0.1:8765/` 選「操作流程圖」。也可直接開啟成品 HTML；使用 HTTP 入口比較方便閱讀其他教學。

- **找重試流程**：按右下角放大鏡，輸入 `retry`，選 Attempt Retry Loop。節點抽屜會呈現節點與相關連線。
- **比較兩種視覺**：點頂端主題按鈕切換明暗；用樣式選單比較 Flow、Blueprint 等預設。
- **追成功路徑**：開啟 PATH，依指引選起點和終點，觀察連線高亮；這是圖中的可達路徑，並非真正執行爬蟲。
- **帶走圖片**：點 Export，選 SVG · Light 下載向量圖。本次真實 Chromium 已驗證主題、搜尋、路徑探測與 SVG 下載；剪貼簿與 WebM 匯出尚未實測。

其他快捷鍵可按 `?` 查看圖內操作指引；例如 `/` 搜尋、`T` 主題、`R` 路徑探測、`0` 重設視野。

## 圖中的重要行為

圖以固定 commit `c169d08b730d4c995a0c83141565621f47e8ba12` 的程式碼為準。完整節點來源與行號存於 [source mapping](../data/crawler-source-mapping.json)。

抓取每個 period 最多三次，失敗之間等待 2、4 秒；週榜或月榜失敗會產生 error／partial 快照，不用前期資料冒充新結果。只有 crawler exit code 為 0 才更新 `latest-success.json`。

**有效的失敗快照仍先 commit／push。** JSON 結構通過驗證後，CI 即使跳過成功快照複製，仍提交 `latest.json`。Git push 成功後才處理 crawler 失敗的 debug 上傳及 exit 1。若 JSON 驗證或 Git push 本身失敗，job 更早中止，後面的普通 steps 不會執行。

這也是獨立審查找到並修正的圖表契約差異。靜態圖表示可能的控制流程，無法替代每次 GitHub Actions 的執行紀錄，也不會替你 commit 或 push。

## 修改與重新生成

改 [crawler.workflow.json](../diagrams/crawler.workflow.json)，再從專案根目錄執行：

```sh
sh scripts/build_archify.sh
```

腳本使用固定版本的 `vendor/archify/archify/bin/archify.mjs`，依序通過原生 validate、deliver、check、browser-check，並保存 HTML、截圖及 sidecar receipts。幾條例外路徑使用明確座標，改節點位置後需要一併調整；原生 showcase 閘門會檢查交叉、遮擋與閱讀尺寸。

建置 wrapper 在閘門返回失敗或 Python 可捕捉的例外時還原上一份 HTML 與 sidecars；已有會故意破壞輸出的回歸測試。此機制不能保證遭 SIGKILL、斷電或磁碟損壞時復原，也不支援同一輸出目錄的平行 writer。

## 來源與限制

Archify 原生 repo-root evidence 要求 origin 與公開 repo URL 一致；這份 vendor clone 的 origin 是本機研究 checkout。沒有偽造原生 provenance 成功，而是另存固定 commit 的 source mapping。原生图表幾何門禁通過，與來源對照驗證是兩件事。

成品包包含已生成圖，不包含原生引擎。重新建置需要來源檔：[Archify 官方 repo](https://github.com/tt-a1i/archify)，本次 commit 見 [tool-sources.json](../data/tool-sources.json)，以及本專案 Node 22、Playwright Chromium。
