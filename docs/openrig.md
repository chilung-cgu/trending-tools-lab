# OpenRig：把多個編碼代理組成一支團隊

這個成果把 [OpenRig](https://github.com/mvschwarz/openrig)（Apache-2.0）實際跑在隔離環境裡：三個席位、三次佇列交接、關閉後還原，並附上真實的儀表板截圖與原始紀錄。目前固定版本是 0.6.10。

## 先回答你一開始的疑問

OpenRig **不需要多個 Codex 帳號**。官方 README 寫明可以只用 Claude Code、只用 Codex，或兩者都用，不需要第二份訂閱。本實驗使用的 stub 席位不呼叫模型，因此連登入都不需要。

## 它是什麼

OpenRig 管理的是代理之間形成的「系統」，不是代理本身：哪些 tmux 工作階段在跑、彼此如何交接工作、重開機後怎麼還原。你用 YAML 描述團隊，用 `rig up` 啟動，之後可以送訊息、交接工作、查看狀態、關閉並還原。

## 先看成果

在專案根目錄執行 `sh scripts/serve.sh`，開啟入口的「OpenRig 多代理團隊實驗場」，或直接開 [成果頁](../artifacts/openrig/index.html)。頁面顯示：

- 真實儀表板截圖：triage 團隊的 lead、scout、reviewer 三個席位。
- 三次佇列交接的真實狀態（lead → scout → reviewer → lead）。
- 關閉後還原的兩種結果：沒加 `--fresh` 時三席停在「等待你決定」，加了之後才重新啟動。
- `rig send --verify` 只代表訊息出現在目標終端，不代表代理讀到或回覆。

## 自己重跑

```sh
cd openrig && npm ci          # 固定安裝 @openrig/cli 0.6.10
cd ..
bash scripts/openrig_demo.sh --out /tmp/openrig-run --shots
```

需要 Node 22（專案內 `.tools/node` 已提供）與系統的 tmux。輸出目錄必須不存在或為空；若已有內容，腳本會拒絕並保留原檔。完成後看 `/tmp/openrig-run/run.json`（整理後的結果）與 `raw/`（每個命令的原始輸出）。

## 隔離與清理

腳本把 HOME、OPENRIG_HOME、CODEX_HOME、CLAUDE_CONFIG_DIR 與 tmux socket 都指到輸出目錄或暫存目錄，daemon 只綁定 127.0.0.1 的隨機埠。官方文件說明 OpenRig 平常會改寫 `~/.codex/config.toml`、`~/.claude/skills`、`~/.tmux.conf` 等檔案；本實驗在執行前後比對這些檔案，全部未變動。結束時腳本會刪除團隊、停止 daemon、關閉專用 tmux 並刪除暫存。

## 怎麼玩

1. 改 [團隊定義](../openrig/rigs/trending-desk/rig.yaml)：新增第四個席位或改邊（`delegates_to`、`escalates_to`），再用 `rig spec validate` 驗證。
2. 改席位的 `seats/*/.openrig/stub/script.json`，讓它在啟動時印出不同文字，觀察 `rig capture`。
3. 手動接力：在示範中途暫停，用 `rig queue list` 與 `rig queue show` 看每一棒的狀態與 transitions。
4. 若你想接上真實代理，先讀官方 README 的「What OpenRig changes on your machine」，再用 `rig setup --dry-run` 預覽；它會改動你的全域設定，不要在重要環境直接跑。

## 實測限制

- stub 不呼叫模型，也不讀取輸入；只能證明 tmux、daemon、SQLite 與 CLI 的團隊機制，不能證明代理的判斷或對話品質。
- 沒有測 Claude Code 或 Codex 真實席位、herdr、cmux、跨主機與重開機後還原。
- 網頁介面被官方標示為維護模式，命令列才是主要介面。
- 官方文件指出 stub 席位沒有可續接的 session 狀態（resume token），所以還原需要 `--fresh`；真實席位的還原行為沒有實測。
- 資料來源：OpenRig v0.6.10 官方 README、docs/reference 與 test-layers；版本以 `openrig/package-lock.json` 為準。
