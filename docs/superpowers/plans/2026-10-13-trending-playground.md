# Trending 工具實驗室 Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task. User explicitly authorizes autonomous design and execution; no repeated approval gates.

**Goal:** 完成五項工具成品／實驗及 Worktrunk 隔離練習，附繁中操作教學。

**Architecture:** 獨立專案，共同保存四週原始快照與標準 index；web、archify、video、cad、context 分別產出 artifacts。主代理掌握依賴安裝、來源固定、跨模組契約及驗證，worker 各自修改不相交目錄。

**Tech Stack:** 專案內 Node 22、固定 npm dependencies、Python uv/.venv、Chromium、FFmpeg、Archify CLI、HyperFrames、cadgen、context-mode、Worktrunk。

**Spec:** ../specs/2026-10-13-trending-playground-design.md

## Global Constraints

- Linux aarch64；Node 22 工具鏈使用專案內路徑；Python 採 uv/.venv。
- 日期 2026-09-21、2026-09-28、2026-10-05、2026-10-12；每日最後成功快照。
- rolling stars 不相加，未進 Top 10 不當作 0；公開來源 commit 固定。
- 不改全域 credentials、agent 規則或 shell 啟動檔；server 僅 loopback。
- Luna 若用只可 max；Sol CLI worker 指定 gpt-6.1-sol medium；不可假稱 provider 用量。
- 不發布、不 push、不操作真實硬體、不自動 merge；所有交付可重跑。

## Review Focus

- 過期 snapshot：UI 必須顯示來源日期，不宣稱即時。
- 空搜尋及語言 filter：正確空狀態，不殘留上一批結果。
- 四週缺席：跨期紀錄標為未進榜，不設 stars=0。
- ARM64 安裝失敗：保留實際錯誤，不拿替代圖片冒充 CAD／MP4。
- MCP 搜尋只找到部分錯誤：測試每個已知 marker，不能只報輸出縮小。

## Task 1: 專案與共用資料

Files: `scripts/export_snapshots.py`, `tests/test_snapshots.py`, `data/raw/*.json`, `data/index.json`, `data/provenance.json`, `package.json`, `.gitignore`, `scripts/env.sh`。

Interface: index.json = `{snapshots:[{date,commit,generated_at_taipei,source_url,weekly:Item[],monthly:Item[]}]} `；Item沿用 crawler 欄位。原始 commits 另記 provenance。

- [ ] 先寫測試：四日期、有47個unique repos、weekly/monthly各10個、最新generated_at正確、來源URI固定commit。
- [ ] 執行測試確認資料不存在時失敗。
- [ ] 匯出原始資料與index；固定工具鏈與依賴，保存版本。
- [ ] 執行完整資料測試，檢查 schema 与原始資料一致。

## Task 2: Impeccable web

Files: `web/index.html`, `web/style.css`, `web/app.js`, `web/PRODUCT.md`, `web/DESIGN.md`, `tests/web.spec.js`, `docs/impeccable.md`。

Consumes Task1 index via relative fetch；Produces `/web/` browser app、`evidence/impeccable/` detector JSON、screenshots。

- [ ] 閱讀已查核 Impeccable skill，寫實際UI驗收測試。
- [ ] 建立介面和filter，使用安全DOM rendering；記錄設計取捨。
- [ ] 執行實際detect，修正或明確說明具體finding。
- [ ] 真實Chromium測試三viewport、日期／period／搜尋／語言／details與source links。
- [ ] 教學含玩法與重建，保存截圖。

## Task 3: Archify workflow

Files: `diagrams/crawler.workflow.json`, `scripts/build_archify.sh`, `docs/archify.md`。

Consumes固定commit crawler source；Produces `artifacts/archify/crawler.html`、原生receipt及screenshot。

- [ ] 閱讀原生SKILL與workflow schema/example、source parser/retry邏輯。
- [ ] 產生真實工作流JSON，保存來源mapping。
- [ ] 執行native finalize及browser gate；修復失敗。
- [ ] 測試節點、route、theme／export等實際可用功能；補教學。

## Task 4: HyperFrames video

Files: `video/index.html`, `scripts/build_video.sh`, `docs/hyperframes.md`。

Consumes Task1 index；Produces `artifacts/video/trending.mp4`與frames、ffprobe JSON。

- [ ] 閱讀HyperFrames技能、composition契約、lint／render CLI。
- [ ] 以四日期建立30秒1280x720 composition；資料直接衍生，禁止累加rolling stars。
- [ ] native lint/render；ffprobe檢查duration/size，擷取三frames人工審查。
- [ ] 教學包含改腳本、換資料、preview與render。

## Task 5: CAD

Files: `cad/cable_organizer.py`, `cad/parameters.json`, `scripts/build_cad.sh`, `tests/test_cad.py`, `docs/text-to-cad.md`。

Produces STEP、STL、geometry.json、預覽/工程圖；參數以mm為單位。

- [ ] 確認ARM64 wheel，讀官方CAD skill與build契約。
- [ ] 定義預期bbox／volume／參數變更測試，先確認無模型時失敗。
- [ ] 建立真實solid與原生export；測試第二組尺寸。
- [ ] 本機預覽／工程圖，確認缺孔、裂體與單位；說明非製造認證。

## Task 6: context-mode與Worktrunk

Files: `context/mcp_experiment.py`, `context/generate_fixture.py`, `docs/context-mode.md`, `docs/worktrunk.md`, `scripts/worktree_demo.sh`。

Produces真實MCP receipts、benchmark.json、Worktrunk evidence；不改global hooks。

- [ ] 原生MCP initialize/tools/list，按返回schema呼叫工具。
- [ ] 生成含三marker的合成log；逐一搜尋並assert保留上下文。
- [ ] 記錄full/retrieval bytes及chars和stats，不將bytes當tokens。
- [ ] 使用wt建立/列出本專案demo worktrees，驗證檔案隔離。
- [ ] 教學區分MCP與hooks，提供opt-in步驟及安全練習。

## Task 7: 整合與交付

Files: `README.md`, `index.html`, `scripts/serve.sh`, `evidence/verification.json`, `docs/progress.md`。

- [ ] 所有入口相對連結有效；guide可跟著操作。
- [ ] 資料測試、UI suite、Archify native checks、影片probe、CAD geometry、MCP markers與wt均重跑。
- [ ] 獨立review，主代理修正具體finding與驗證。
- [ ] 提供入口、SSH tunnel、成品特色與證據，不把未測項目說成完成。
