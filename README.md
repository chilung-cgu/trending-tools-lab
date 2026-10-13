# Trending 工具實驗室

把 GitHub Trending 上值得玩的開源工具，各做成一個可以打開、操作、重跑的小成果，並誠實記錄限制。第一期取自 2026-09-21 到 2026-10-12 四週的 Trending 快照，共 6 個工具實驗加 1 個多代理團隊實驗。

資料來源是 [chilung-cgu/github-trending-crawler](https://github.com/chilung-cgu/github-trending-crawler) 保存的快照。這些是歷史觀測，不是即時榜單。

## 線上瀏覽

**https://chilung-cgu.github.io/trending-tools-lab/** ：打開就能用，不需要安裝或下載任何東西。

網站每次 main 更新時由 GitHub Actions 自動部署，內容只來自 repo 裡被追蹤的檔案。

## 在自己的電腦打開

```sh
git clone https://github.com/chilung-cgu/trending-tools-lab.git
cd trending-tools-lab
python3 -m http.server 8765 --bind 127.0.0.1
```

開啟 `http://127.0.0.1:8765/` 。離線也能用，或想修改後立刻看效果時使用。

| 成果 | 你可以做什麼 | 教學 |
| --- | --- | --- |
| Impeccable：榜單探索器 | 換日期、週月榜，搜尋與篩選語言，展開跨期紀錄 | [docs/impeccable.md](docs/impeccable.md) |
| Archify：Crawler 流程圖 | 搜尋節點、追蹤成功與失敗路徑、切換主題、匯出 SVG | [docs/archify.md](docs/archify.md) |
| HyperFrames：30 秒影片 | 播放影片；改文案或配色後重新渲染 | [docs/hyperframes.md](docs/hyperframes.md) |
| text-to-cad：參數化理線器 | 旋轉 3D 模型、改尺寸、匯出 STEP 與 STL | [docs/text-to-cad.md](docs/text-to-cad.md) |
| context-mode：大型 log 檢索 | 在合成建置 log 中找錯誤，量測檢索輸出大小 | [docs/context-mode.md](docs/context-mode.md) |
| Worktrunk：工作區隔離 | 建立獨立 worktree，驗證檔案互不污染 | [docs/worktrunk.md](docs/worktrunk.md) |
| OpenRig：多代理團隊 | 啟動三席團隊、佇列交接、關閉還原；不需要第二個帳號 | [docs/openrig.md](docs/openrig.md) |

每份教學都包含功能、操作步驟、可以怎麼玩、重建方式與已知限制。

## 資料與誠實原則

- 滾動週榜與月榜區間會重疊，stars 不能跨期相加。
- 沒進 Top 10 代表「未觀測」，不代表 0 stars。
- 各工具有沒有警告、哪些功能沒測，都寫在對應教學與 [第二輪審查](docs/re-review.md)。
- 沒有實體列印過 CAD 模型；沒有在真實 Claude Code 或 Codex 席位上測 OpenRig。

## 重建

重建需要 Node 22、Python 3.13（uv）、Chromium 與 FFmpeg。從乾淨環境開始：

```sh
npm ci
uv sync
sh scripts/fetch_vendor.sh        # 取得固定 commit 的 crawler 與 archify 原始碼
cd openrig && npm ci && cd ..     # OpenRig 0.6.10
.venv/bin/python -m pytest -q
node_modules/.bin/playwright test
```

各成果的專用建置腳本見 scripts/ 與對應教學。依賴版本由 package-lock.json、uv.lock、[data/tool-sources.json](data/tool-sources.json) 固定。

## 授權

原創程式與文件採用 MIT 授權，見 LICENSE。第三方元件與其授權見 [NOTICE.md](NOTICE.md)。

## 下一步

每週挑選新工具：用 scripts/weekly_candidates.py 產生候選清單，再由人決定實踐哪些，見 [docs/weekly.md](docs/weekly.md)。其他想法見 [docs/next-ideas.md](docs/next-ideas.md)，尚未實作。
