# HyperFrames：把四週榜單做成影片

成品是 [30 秒 MP4](../artifacts/video/trending.mp4)。它以四個固定日期的週榜前三名做成六個場景：開場、四週觀察、結尾。可直接播放或下載，不需要登入 HeyGen。

## 先玩成品

在專案根目錄執行 `sh scripts/serve.sh`，開啟 `http://127.0.0.1:8765/`，選「四週開源觀察影片」。播放、暫停、拖曳時間軸，對照 [資料探索器](../web/index.html) 同一天的週榜。

本版沒有配音與背景音樂；輸出為 H.264、1280×720、24 fps、30 秒。每週顯示的是該日 GitHub Trending 的原始排名，不依 stars 數字重新排序。

## 它有什麼特色

HyperFrames 用 HTML/CSS 與可定位時間的 GSAP timeline 產生影片。修改排版像改網頁，renderer 則逐格設定時間並用 FFmpeg 編碼；它不是把螢幕錄影拼成假示範。本專案先把快照內容寫進 HTML、把 GSAP 存成本機資產，避免渲染時再抓榜單。

影片由 [generate_video.py](../scripts/generate_video.py) 生成；[video/index.html](../video/index.html) 是可重建的輸出檔。請改 generator，否則下一次建置會蓋掉直接修改的 HTML。

## 修改與重新生成

從專案根目錄執行：

```sh
sh scripts/build_video.sh
```

腳本依序生成 HTML、跑原生 lint 與 check、渲染 MP4、保存 ffprobe metadata，並擷取 1、6、13、20、28 秒畫面至 `artifacts/video/`。腳本會指定 Playwright 的 Chromium 路徑，並檢查 JSON 結果；瀏覽器檢查失敗或被跳過就停止，不會只因 CLI 回傳零而宣稱通過。需要專案內 Node、`npm ci` 安裝的依賴、Playwright Chromium 與系統 FFmpeg。若未安裝 browser，先執行：

```sh
export PATH="$PWD/.tools/node/bin:$PWD/node_modules/.bin:$PATH"
playwright install chromium
```

想用 Studio 看 timeline：

```sh
export PATH="$PWD/.tools/node/bin:$PWD/node_modules/.bin:$PATH"
hyperframes preview video --no-open
```

依 CLI 印出的 localhost URL 開啟 Studio。此版本預設綁定 loopback；遠端使用時另建 SSH tunnel。按 CLI 實際顯示的 port 轉送，別假設它一定是 8765。

## 可以怎麼玩

- 把 `weekly` 改成 `monthly`，同時修改標題與 `stars this week` 標籤，做月榜版。
- 改配色、字級與進場動畫，再比較同一秒的 PNG；可重現的 timeline 方便檢查兩版差異。
- 加一頁你選中的工具介紹。新增場景時也要調整根元素的 `data-duration`，避免結尾被截掉。

## 已知限制與來源

只展示保存的四日快照，並非即時榜單。週／月滾動區間可能重疊，不能把 `period_stars` 跨期累加。缺席 Top 10 不代表 stars 為零。

本次 ARM64 環境使用軟體 GPU 與 screenshot capture，沒有宣稱硬體加速。原生 lint 的七項 warning 是建議把六個場景拆成 sub-compositions 與降低同一 track 密度；不是影片編碼失敗。詳細結果保存在 `evidence/video/`。

工具版本固定 `hyperframes@0.8.150`。契約查核來自 [HyperFrames 官方 core skill](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-core/SKILL.md) 與已安裝版本的 CLI；相同品牌的舊 core 文件可能與目前的 duration 契約不同，重建請以 lockfile 與原生 CLI 為準。
