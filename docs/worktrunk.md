# Worktrunk (wt) 實戰教學指南

本指南說明如何在 Linux aarch64 環境中使用 Worktrunk（wt 0.80.0）管理 Git worktrees，並驗證多任務與多 Agent 工作流下的檔案隔離。

## 核心特色

Worktrunk 是專為平行 AI Agent 與多任務開發設計的 Git worktree 管理命令列工具：

- 快速目錄切換：透過分支名稱直接對應獨立工作目錄，無需手動管理繁瑣路徑。
- 原生狀態檢視：即時呈現各 worktree 的未提交改動、與主分支的差異與提交時間。
- 結構化 JSON 輸出：所有核心指令支援 --format json，便於腳本與自動化代理整合。
- 安全分支清理檢查：自動偵測 squash-merge 與祖先歷史，確認變更已合併才允許刪除分支。

## Linux aarch64 安裝方式

本專案使用免安裝全域設定的方式，將官方 musl 二進位包直接安置於工作區工具目錄：

```bash
# 1. 建立本機工具目錄
mkdir -p .tools/wt

# 2. 下載官方 aarch64 release 與校驗碼（以 v0.80.0 為例）
curl -fsSL https://github.com/max-sixty/worktrunk/releases/download/v0.80.0/worktrunk-aarch64-unknown-linux-musl.tar.xz -o .tools/wt/worktrunk-aarch64-unknown-linux-musl.tar.xz
curl -fsSL https://github.com/max-sixty/worktrunk/releases/download/v0.80.0/worktrunk-aarch64-unknown-linux-musl.tar.xz.sha256 -o .tools/wt/worktrunk-aarch64-unknown-linux-musl.tar.xz.sha256
(cd .tools/wt && sha256sum -c worktrunk-aarch64-unknown-linux-musl.tar.xz.sha256)

# 3. 解壓縮並建立執行檔軟連結
tar -xf .tools/wt/worktrunk-aarch64-unknown-linux-musl.tar.xz -C .tools/wt/
ln -sf worktrunk-aarch64-unknown-linux-musl/wt .tools/wt/wt
ln -sf worktrunk-aarch64-unknown-linux-musl/git-wt .tools/wt/git-wt

# 4. 驗證執行
.tools/wt/wt --version
```

## 常用 CLI 命令與捷徑

Worktrunk 原生支援簡潔的符號捷徑與自動化參數：

- wt switch --create <branch> --base @ --no-hooks --no-cd --format json：從當前分支 HEAD 建立並初始化新 worktree，但不切換當前 shell 路徑。
- wt list --format json：以 JSON 格式列出所有存在的 worktree、當前 HEAD 狀態與未提交變更。
- wt remove <branch> --foreground --no-hooks：在前台安全移除指定 worktree 與其分支（若內容已整合且無未提交變更）。
- 捷徑符號 @ 與 ^：@ 代表當前所在的分支與工作區；^ 代表儲存庫的預設分支（如 main）。

## 示範腳本與驗證重跑

可透過專案提供的示範腳本驗證檔案隔離：

```bash
# 確保位於專案根目錄
cd trending-tools-lab

# 執行 Worktree 隔離示範腳本
bash scripts/worktree_demo.sh

# 檢視隔離證據與 JSON 輸出
cat evidence/worktrunk/isolation_evidence.txt
cat evidence/worktrunk/worktrunk_demo.log
```

## 多 Agent 協作場景玩法

在多個代理人同時執行任務時，Worktrunk 提供強大的隔離機制：

- 專屬動態分支：為每個臨時子任務配置帶有時間戳記與行程編號的唯一分支（例如 demo-wt-timestamp-pid），互不踩踏。
- 實體驗證隔離：子代理在新建的 worktree 內產出原型檔案，原專案目錄與其他既有 worktree 完全不受污染。
- 保持既有身分：沿用儲存庫既有的 git config 使用者設定，不改動全域設定，亦不執行未授權的 push 或 merge。

worktree 隔離的是分支與檔案，並不隔離網路、credentials 或共用的 Git 物件資料庫。建立時也不會帶入目前尚未提交的檔案；本次唯一分支示範從目前分支 HEAD 開始，不是複製整個未提交工作區。此版本的 CLI、hooks 與 shell integration 說明以 [Worktrunk 官方文件](https://worktrunk.dev/) 為準。

## 安全限制與防護邊界

在自動化腳本中使用 Worktrunk 時，必須遵循以下安全原則：

- 嚴禁強制清除既存工作區：絕對不可執行 wt remove <既存分支> -f，避免刪除使用者未提交的實驗資料。
- 乾淨卸載原則：在移除動態產生的示範工作區前，應先清理該次示範建立的臨時檔案，再以無 force 的正規方式卸載。
- 保留未參與實驗的既存分支：如 demo-worktree-isolation 等既有工作區必須完整保留，不可納入清理範圍。

## 真實失敗與修復記錄

在完善 worktree 自動化示範的過程中，我們修正了以下問題：

1. 避免誤刪使用者既有工作區：早期腳本曾嘗試以 -f 清理 demo-worktree-isolation，修正為每次動態產生獨一無二的分支名稱，並嚴格保留所有既有 worktree。
2. 逐一巡檢儲存庫所有兄弟工作區：原先僅比對主專案根目錄，更新為使用 git worktree list --porcelain 完整走訪儲存庫內全部兄弟工作區，落實真正的全域隔離檢驗。
3. 移除危險 shell 指令：為符合安全規範，全面避免使用 rm -f，改用精確路徑逐檔清理後再呼叫 Worktrunk 原生移除命令。
