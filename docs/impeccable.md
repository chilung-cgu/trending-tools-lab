# Impeccable：Trending 觀測簿

這個探索器把四週 GitHub Trending 週榜與月榜整理成可搜尋的觀測簿。暖紙色、墨色與編輯式表格讓你先掃描名稱和描述，再開啟詳情核對歷史；手機使用直向資料列，保留來源排名與期間新增 stars。

## 開啟

在專案根目錄執行：

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

在同一台機器開啟 <http://127.0.0.1:8765/web/>。若專案位於遠端 Linux，從自己的電腦另開終端建立 tunnel（替換帳號與主機）：

```sh
ssh -L 8765:127.0.0.1:8765 使用者@遠端主機
```

再於自己的瀏覽器開啟相同 URL。伺服器若已在執行，不必重複啟動。請從專案根目錄提供 HTTP 服務：直接雙擊 HTML 的 file 模式無法可靠 fetch 資料。

## 使用

1. **快照日期與榜單週期**：預設最新日期週榜；切到其他日期或月榜，名稱、排名、期間新增數字與來源一起更新。語言篩選若仍適用就保留，否則回到所有語言；搜尋文字保留。
2. **搜尋與程式語言**：搜尋同時比對 repo 名稱及描述，忽略英文大小寫；語言選項來自目前榜單。兩者以 AND 結合。搜尋不到會顯示空狀態，按「清除篩選」重設搜尋與語言，不更動日期與週期。
3. **查看詳情**：按 repo 的「查看詳情」，清單前方展開描述、語言、累計 stars、forks 與八筆週／月觀測。Tab 可移到按鈕，Enter 開啟，焦點移至詳情標題；按「收起詳情」回到原始按鈕。
4. **核對來源**：控制列下方始終呈現目前快照擷取時間、commit 與原始來源。詳情每筆歷史另有來源；GitHub 專案連結在新分頁開啟。連結限 HTTPS GitHub，異常 URL 不會成為可點擊連結。

載入失敗會指出檔案與啟動位置，按「重新載入」重新 fetch。資料文字不當作 HTML 解析。

## 玩法

選擇同一個 repo 的詳情，比較不同日期是否出現在週榜或月榜，再用來源核對。例如最新週榜的 `boykopovar/AnyPS5` 只有在確實觀測到的期間顯示數字；其餘列明確寫「未觀測」。搜尋 `video` 並切換週／月榜，可探索影片相關描述；若加上語言後無結果，先清除篩選再比較。

修改 [style.css](../web/style.css) 的 `:root` tokens 可實驗紙色、墨色與重點色；修改 [index.html](../web/index.html) 可改介面文字；[app.js](../web/app.js) 管理搜尋、篩選與安全 DOM。靜態 app 沒有編譯步驟，存檔後重新整理即可。換資料須由共用資料流程產生符合契約的 [index.json](../data/index.json)，此 UI 不爬取 GitHub 或修改共享快照。

## 重建與驗證

以專案內 Node 工具鏈執行，無須安裝其他套件：

```sh
export PATH="$PWD/.tools/node/bin:$PATH"
node_modules/.bin/playwright test tests/web.spec.js
```

主專案的 `playwright.config.js` 會提供 loopback 8765 伺服器。worker 獨立驗證使用同樣 URL，將測試輸出限制在本成果的證據目錄：

```sh
node_modules/.bin/playwright test --config evidence/impeccable/worker.config.js
node_modules/.bin/impeccable detect --json web
```

如果 Chromium 尚未備妥，應由主專案環境流程提供瀏覽器；本成果不自行安裝套件。detector 只提供靜態／啟發式意見，不能作為完整 accessibility 證明。

## 實作與證據

真正執行 `impeccable context --target web` 一次，以 [PRODUCT.md](../web/PRODUCT.md) 固定產品事實、[DESIGN.md](../web/DESIGN.md) 固定視覺與互動契約。concept-seed 原始輸出、detector JSON、紅綠測試 log、人工審查皆保存在 [evidence/impeccable/](../evidence/impeccable/)。

測試先確認未實作時 **8 failed**，再驗證 **8 passed**。截圖包含 1920x1080、1280x800、390x844 的清單與詳情，共六張。detector 的 `cream-palette` 警告是使用者指定暖紙色的有意選擇，未以變更設計或關閉 detector 隱藏。

## 限制與資料語意

這是 2026-09-21 至 2026-10-12 的固定歷史快照，每張週／月榜各 Top 10，不能代表所有 repo 或即時熱度。排名沿用來源，不依 stars 重新排序。描述維持來源語言，未提供描述／語言會明確標示。

`period_stars` 是當時的滾動週／月窗口；不同日期的窗口可能重疊，**不能相加當成四週新增 stars**。未上榜代表沒有觀測，不代表 stars 為零，也不能以此推定消失或停止維護。累計 stars 與 forks 是選取快照中的值。

目前驗證使用真實 Chromium 的桌機及手機尺寸模擬，未測其他瀏覽器、實體手機或螢幕閱讀器。無登入、收藏、資料庫、API 設定或背景更新。
