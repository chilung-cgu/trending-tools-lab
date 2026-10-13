# 實驗室完成紀錄

既有規格與計畫保存在 [設計規格](superpowers/specs/2026-10-13-trending-playground-design.md) 與 [實作計畫](superpowers/plans/2026-10-13-trending-playground.md)。本次由目前 session 統籌，在 `lab/trending-tools` worktree 完成工具實踐；沒有修改原 crawler repo、沒有發布或推送。

| 任務 | 實際成果與驗證 |
| --- | --- |
| 四週資料 | 四份原始快照與 commit provenance，週／月榜各 10 筆，47 個 unique repo |
| Impeccable | 真實 CLI context/detect；八項 Chromium UI 測試與三種 viewport 截圖 |
| Archify | 原生 showcase 閘門與 browser-check、互動測試；依 source 修正失敗快照持久化路徑 |
| HyperFrames | 原生 lint/render/check；H.264 30 秒、1280×720、24 fps，實際畫面人工檢視 |
| text-to-cad | 真實 STEP/STL/GLB、幾何與第二組尺寸驗證、3D viewer、PDF 版面回歸測試 |
| context-mode／Worktrunk | 真實 MCP 握手與三 marker 檢索、半段 JSON timeout 測試；wt 安裝校驗與所有同 repo worktree 的 marker 隔離檢查 |

Ruling: 沿用目前 session + 獨立 worktree，不另開統籌 session，避免上下文與責任分散；若選擇不合適，成本是之後重新拆分工作。

Ruling: 外部 worker 用量不當作 Codex quota 使用量，本專案不聲稱節省或消耗多少 quota；不同 provider 的用量要由各自帳戶查核。

Final review: 獨立 reviewer 的原始報告在 `evidence/final-review.md`；修正結果見 [review-resolution.md](review-resolution.md)。所有 Critical／Important 發現已處理；最後重跑測試與 native 閘門後，精確結果寫入 `evidence/verification.json`。

Final: minor (deferred): 有結果時沒有常駐的一鍵清除篩選按鈕，仍可清空搜尋及選擇所有語言。影片原生 lint 的七項場景拆分建議與 Impeccable 暖紙色警告保留，已在教學說明。

產物保存於本機工作區，另提供帶 SHA-256 manifest 的可攜 ZIP。所有工具的特色、操作、修改方式與實測限制都從 `index.html` 連到繁中 HTML 教學；README 提供 localhost 與 SSH tunnel 啟動方式。


## 第七項：OpenRig（使用者改變主意後加入）

Ruling: 使用者原本以為 OpenRig 需要多個 Codex 帳號而排除；官方 README 寫明單一帳號即可，且不需第二份訂閱，故補做。
Ruling: 示範使用 stub 席位，不呼叫模型、不需登入，也不碰使用者的真實 Codex 或 Claude 設定；真實席位未測，已寫在限制。
Ruling: 在隔離 HOME、OPENRIG_HOME、tmux socket 與隨機 loopback 埠執行，結束後自動清理，並以前後雜湊證明 ~/.codex、~/.claude、~/.tmux.conf 未變。

驗證：scripts/openrig_demo.sh 產出 run.json，10 項檢查全過（三席就緒、三次佇列交接、未加 --fresh 時等待決定、加 --fresh 後重新啟動、send --verify 只代表出現在 pane）。測試先失敗再通過；打包曾誤排除隱藏的 stub 劇本，已加回歸測試。
