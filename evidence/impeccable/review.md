# Impeccable 驗收紀錄

## 結果與範圍

Task 2 已完成。靜態 app 提供日期／週月榜、搜尋、語言、鍵盤內嵌詳情、跨快照紀錄及來源；資料由 ../data/index.json 讀取。寫入僅 web/、tests/web.spec.js、docs/impeccable.md、evidence/impeccable/。沒有安裝套件、修改共用設定／資料、commit 或啟動代理。

## 實際命令與結果

所有 Node 命令 PATH 前置 `/home/ubuntu/worktrees/trending-tools-lab/.tools/node/bin`。

| 命令 | 結果 |
| --- | --- |
| `node_modules/.bin/impeccable context --target web` | 成功，執行一次；當時 target 不存在、PRODUCT/設計未建立，要求手動 detector |
| `../node_modules/.bin/impeccable concept-seed --scope direction --mode operate`（cwd web/） | 成功，原始輸出 concept-seed.txt；固定 brief 優先 |
| `node_modules/.bin/playwright test --config evidence/impeccable/worker.config.js`（UI 實作前） | exit 1，8 failed，red.log |
| 同上（實作後） | exit 0，8 passed（4.9s） |
| 同上（手機來源連結補強後） | exit 0，8 passed（6.9s），green.log |
| `node_modules/.bin/impeccable detect --json web` | exit 0，一項 warning，detect.json 原始保留，執行一次 |
| `node --check web/app.js`、`node --check tests/web.spec.js` | exit 0 |

worker.config.js 只供獨立驗收，webServer 為 Python HTTP server，綁定 127.0.0.1:8765。測試 URL 與主專案設定相同，輸出限制在本 evidence 目錄。主專案測試可直接選 tests/web.spec.js；本 worker 未改主專案設定。

## Detector finding

`cream-palette` 指向 web/index.html 的 rgb(246,243,235)。這正是使用者指定的 warm paper/ink editorial table，不是無需求的預設，因此有意保留。沒有忽略規則、沒有修改全域設定，也沒有把 detector 的 exit 0 解讀為零 finding。掃描在手機連結最小高度修正前執行；修正僅 link 觸控尺寸，與 finding 無關。

## 人工 audit 與 polish

以真實 Chromium 執行三尺寸行為測試；人工檢視 1280x800 清單、390x844 詳情，最後確認 1920x1080 與 390x844 清單。共保留六張全頁截圖。桌機表格有清楚的 repo／描述／語言／數字層級，手機資料列不裁掉描述；三尺寸清單及展開詳情均無 document 水平溢出。

初次檢查發現手機 provenance 與指南連結太矮，已加最小 44px 高度並重跑 suite。焦點移到詳情標題、收起回原始按鈕的路徑由鍵盤測試確認；載入失敗可重試。history 來源連結有 44px 高度，文字本身的寬度較小，未對實體手機精準觸控做認證。

| 面向 | 局部評分 / 4 | 證據與限制 |
| --- | --- | --- |
| Accessibility | 3 | label、語意 table、focus、鍵盤流程、live 結果數；未做螢幕閱讀器完整稽核 |
| Performance | 3 | 原生 DOM、單一 JSON、無前端依賴載入；未做正式效能基準 |
| Theming | 3 | 固定暖紙色，CSS tokens；未提供需求外的深色模式 |
| Responsive | 3 | 三尺寸真實 Chromium，無水平 overflow；非實體手機測試 |
| Implementation integrity | 4 | 來源契約、原始排名、安全文字／URL、未觀測語意；暖紙色 warning 為有意決策 |

局部評分 16/20，只描述本次檢查，不是 WCAG 合規證明。未發現阻礙已測工作流程的 P0/P1；完整跨瀏覽器、螢幕閱讀器與實體觸控仍未驗證。

contrast.json 由 WCAG 相對亮度公式計算九組文字／表面顏色，全部 >= 4.5:1，最低為次要墨在淡綠表面的 4.85:1。此結果只涵蓋 authored text tokens，不包括 OS 原生 select popup 或每個狀態。

## 測試覆蓋

八項測試包含四日期兩週期所有列的 rank/name/period_stars、來源時間與 URL、名稱與描述搜尋、無結果及清除、語言過濾、詳情八列歷史、未觀測、來源與 repo 連結、鍵盤 focus、三尺寸清單與詳情、惡意描述與假 GitHub host、503 後重試。缺席不填 0，period_stars 未相加。所有資料文字以 textContent 呈現，GitHub link 驗證 protocol／hostname／port／credentials。
