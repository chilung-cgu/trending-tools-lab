# text-to-cad：參數化桌面線材整理架與本機 CAD 流程

本任務實作真實的本機 CAD 模型建置與輸出流程，使用 cadgen 與 build123d 幾何核心，產出具備三條線槽的桌面線材整理架（Desktop Cable Organizer）。模型支援 STEP、STL、GLB 多格式匯出、真實幾何量測摘要（geometry.json）、A4 示範工程圖 PDF（第三角投影）以及無頭瀏覽器產出之真實視圖快照。

## 成品與入口清單

所有建置產物均輸出至專案標準目錄，不使用任何假圖或純 HTML 替代：

| 檔案路徑 | 類型 | 說明 |
| --- | --- | --- |
| [artifacts/cad/index.html](../artifacts/cad/index.html) | Web 3D | 互動檢視入口（由主代理實作本機 Three.js GLB viewer） |
| [artifacts/cad/cable_organizer.step](../artifacts/cad/cable_organizer.step) | 3D CAD | 標準 STEP 模型檔案（包含封閉實體幾何與完整拓撲） |
| [artifacts/cad/cable_organizer.stl](../artifacts/cad/cable_organizer.stl) / [.glb](../artifacts/cad/cable_organizer.glb) | 網格檔案 | STL 用於 3D 列印切片；GLB 為二進位 glTF 2.0 供 Web 預覽 |
| [artifacts/cad/cable_organizer_drawing.pdf](../artifacts/cad/cable_organizer_drawing.pdf) | 圖面文件 | A4 示範工程圖（包含第三角投影、視圖與標註） |
| [artifacts/cad/geometry.json](../artifacts/cad/geometry.json) / [snapshot.png](../evidence/cad/snapshot.png) | 驗證證據 | 包含實體量測摘要 JSON 與 Playwright Chromium 原生快照 |

## 核心設計與特色

1. 真實實體建構（Single Solid）：
   模型由矩形基座經由四邊垂直圓角與三道對稱開槽差集構成，經 OpenCASCADE 核心驗證為單一連續封閉實體（solid count = 1，volume > 0）。
2. 雙重結構開槽（Cable Retention Slot）：
   示範下方 6.0 mm 通道與上方 3.5 mm 狹縫；實際能否卡入及保持取決於線徑、材料彈性與列印公差，尚未實測。
3. 嚴謹的參數化架構：
   所有幾何尺寸集中定義在 [cad/parameters.json](../cad/parameters.json)，無多餘或未使用的假參數。
4. A4 示範工程圖與投影：
   透過 `cadgen.eng_drawing` 產出 A4 橫式示範工程圖，自動自幾何物件投影 Top、Front、Right 及 Isometric 四視圖。材質標記為 `DEMO ONLY`，公差標記為 `UNSPECIFIED`，並包含「示範尺寸，未經量產驗證」註記，避免暗示具備製造認證。

## 建置與測試指令

本模組使用專案專屬之 Python 3.13 虛擬環境（.venv）與固定的 cadgen 0.7.21 版本。

### 1. 執行完整建置

從專案根目錄執行建置腳本：

```bash
./scripts/build_cad.sh
```

建置腳本將依序執行：
- 載入環境變數（CADGEN_TELEMETRY=0、CADGEN_UPDATE_CHECK=0、DO_NOT_TRACK=1）
- 執行 `cad/cable_organizer.py` 產出 STEP、STL 與 GLB
- 呼叫 OpenCASCADE 核心量測實體體積與邊界框，寫入 `artifacts/cad/geometry.json`
- 執行 `cad/cable_organizer_drawing.py` 產出 `artifacts/cad/cable_organizer_drawing.pdf`
- 執行 `cadgen step snapshot` 渲染真實視圖快照至 `evidence/cad/snapshot.png`

### 2. 執行自動化行為測試

從專案根目錄執行 pytest：

```bash
source .venv/bin/activate
pytest -v tests/test_cad.py
```

驗收測試固定鎖定在基準預設值（100.0 × 30.0 × 15.0 mm）與精確定義的緊湊型函式變體（80.0 × 25.0 × 12.0 mm）。若自行修改 `parameters.json` 進行客製化外形實驗，測試套件會因基準尺寸比對不符而報錯；這屬於驗證預設基準的預期行為，不代表任意未受約束的自訂尺寸在實體製造上均屬可行。

## 參數修改說明

[cad/parameters.json](../cad/parameters.json) 控制預設模型外形：

| 參數名稱 | 預設值 | 說明 |
| --- | --- | --- |
| `width` | 100.0 mm | 基座總寬度（X 軸跨度） |
| `depth` | 30.0 mm | 基座總深度（Y 軸跨度） |
| `height` | 15.0 mm | 基座總高度（Z 軸跨度） |
| `slot_diameter` | 6.0 mm | 下方圓柱收納通道直徑 |
| `spacing` | 24.0 mm | 相鄰兩槽中心間距（分布於 -spacing、0、+spacing） |
| `slot_entry_width` | 3.5 mm | 上方開口狹縫寬度 |
| `fillet_radius` | 3.0 mm | 四個垂直轉角的圓角半徑 |

修改參數後請再次執行 `./scripts/build_cad.sh`，即可同步更新 STEP、STL、GLB、geometry.json 與示範工程圖。

## 實測幾何數據與驗證結果

使用預設參數建置之實測幾何數據（記錄於 [geometry.json](../artifacts/cad/geometry.json)）：

- 實體數量：1 個有效實體（Solid）
- 實體體積：40865.195 mm³
- 邊界框（Bounding Box）：
  - X 範圍：-50.0 mm 至 +50.0 mm（寬度 100.0 mm）
  - Y 範圍：-15.0 mm 至 +15.0 mm（深度 30.0 mm）
  - Z 範圍：0.0 mm 至 +15.0 mm（高度 15.0 mm）
- 變更尺寸測試（80.0 × 25.0 × 12.0 mm）：實測產生有效實體，體積縮小，尺寸符合預期。

## 限制與注意事項

1. 示範尺寸與非量產認證：
   本整理架幾何尺寸為桌面配件示範設計，未針對特定電路板或機構干涉進行量產驗證。工程圖標籤明確標記材料為 DEMO ONLY、公差為 UNSPECIFIED，不應視為經過量產驗證之製造規格圖。
2. 平台與核心依賴：
   本流程在 Linux ARM64（aarch64）架構下搭配 uv 及 Python 3.13 運行。cadgen 依賴的 OCP (OpenCASCADE) 核心已透過預編譯 wheel 正確載入。
3. 視圖快照渲染：
   快照採用 Playwright 下載之 headless Chromium 執行 WebGL 離線渲染，產出為標準 PNG 檔案。

