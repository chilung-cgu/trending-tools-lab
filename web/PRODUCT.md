# Trending 探索器

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

使用者指定靜態 web/ 成品；以原生 HTML、CSS、JavaScript 讀取 ../data/index.json，無額外建置依賴。

## Users

依本次需求推定：想比較四週 GitHub Trending 快照的繁體中文讀者，透過搜尋、語言與日期找到值得研究的 repo。

## Product Purpose

在可查證的來源與觀測日期下探索週榜、月榜，查看同一 repo 在不同快照中的紀錄。

## Capabilities and Constraints

日期、週月榜、名稱與描述搜尋、語言篩選、詳細資訊與來源連結。未出現在 Top 10 只代表未觀測；各期滾動 stars 不累加。資料為固定歷史快照，不宣稱即時。外部 repo URL 限定 https://github.com/。

## Brand Commitments

暖紙色、墨色、編輯式表格、寬裕留白與繁體中文。所有互動必須具實際用途。

## Evidence on Hand

../data/index.json 包含快照日期、commit、台北擷取時間、來源 URL 與每期 repo 數據。

## Accessibility & Inclusion

使用明確 label、語意表格、鍵盤可操作的內嵌詳情與可見焦點；桌機和手機皆可閱讀。
