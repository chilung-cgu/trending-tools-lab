# 第三方元件與授權（NOTICE）

本 repo 的原創程式、文件與設定採用 MIT 授權（見 LICENSE）。下列第三方內容保持各自授權；以下資訊逐項查自隨附授權檔、套件資訊或官方頁面（查核日 2026-10-13）。

| 元件 | 版本／來源 | 授權 | 在本 repo 的形式 |
| --- | --- | --- | --- |
| three.js | 0.186.1（package-lock.json） | MIT，Copyright © 2010-2026 three.js authors | 執行檔複本在 artifacts/cad/assets/，授權檔同目錄 LICENSE |
| GSAP | 3.14.2（檔頭） | GSAP Standard "No Charge" License（Webflow）；官方頁面現行條款允許無費用使用，但不得向終端使用者收費，也不得用於與 Webflow 視覺動畫建構功能競爭的工具，且須保留版權與商標標示 | video/assets/gsap.min.js，保留原檔頭；授權連結 https://gsap.com/standard-license |
| JetBrains Mono | Archify 內嵌的子集字型 | SIL Open Font License 1.1 | 內嵌於 artifacts/archify/crawler.html，授權全文與版權聲明保留在檔頭 |
| Archify | 固定 commit，見 data/tool-sources.json | MIT，Copyright (c) 2026 tt-a1i | 只有其產生的 artifacts/archify/crawler.html；原始碼不在本 repo，可用 scripts/fetch_vendor.sh 取得 |
| Impeccable | impeccable 4.5.2（package.json） | Apache-2.0（套件資訊） | 本 repo 只放使用它產生的探索器設計文件與腳本，不含其原始碼 |
| HyperFrames | hyperframes 0.8.150（package.json） | Apache-2.0（套件資訊） | 只放 composition 與渲染腳本；成品 MP4 由它渲染 |
| text-to-cad／cadgen | cadgen 0.7.21（pyproject.toml）；專案 text-to-cad 為 MIT | 見各自專案授權 | 只放模型腳本、匯出成品與工程圖，不含其原始碼 |
| context-mode | context-mode 1.0.169（package.json） | Elastic-2.0（套件資訊）；使用與再散布條件請閱讀其授權 | 只放呼叫它的實驗腳本與實測紀錄；套件由 npm ci 安裝，不隨 repo 發布 |
| OpenRig | @openrig/cli 0.6.10（openrig/package-lock.json） | Apache-2.0 | 本 repo 只放團隊定義、示範腳本與實跑紀錄；套件由 npm ci 安裝，不隨 repo 發布 |
| GitHub Trending 資料 | chilung-cgu/github-trending-crawler 的固定 commit | 資料來自 GitHub 公開頁面的觀測快照 | data/raw/；僅作歷史觀測，不是即時榜單 |

若要修改或再散布，請自行確認上表各授權對你的用途是否適用。
