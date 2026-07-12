# 旋元佑英文字彙學習系統

本專案是一個基於 **Vue 3**、**Element Plus** 與 **PWA** 技術開發的英文字彙學習網頁系統。系統專為《旋元佑英文字彙》教科書量身打造，整合了字首/字根分類瀏覽、模糊搜尋定位、雙 TTS 語音發音引擎、Fisher-Yates 隨機小考測驗，以及基於 **Leitner 掌握度箱子演算法** 的錯字高效複習系統。

系統支援響應式深色主題與 Service Worker 離線快取，提供使用者沉浸且高效的學習體驗。

---

## 核心功能特色

### 1. 背單字模式 (Study Mode)
* **階層式章節導覽**：支援 Part 與章節級聯選擇器 (Cascader)，可精確跳轉至指定單元。
* **字面/釋義模糊搜尋**：整合全域搜尋框，支援英文字彙或中文釋義模糊比對，點選單字直接跨單元跳轉定位，保留上下文。
* **TTS 語音雙引擎**：單字與例句分開播放。優先調用「有道美音 TTS 發音引擎」，若遇離線或載入超時 (800ms) 會自動降級退回瀏覽器原生 Web Speech API，確保發音體驗不受網路影響。
* **多例句播放優化**：主按鈕支援串接多句例句依序播放，且每個例句左側均配備獨立語音播放按鈕，可單獨播放特定例句。

### 2. 小考模式 (Quiz Mode)
* **自訂範圍與題數**：可選擇測驗範圍（全書、指定 Part/章節，或僅限錯字本），自訂 10、20、30 或 50 題。
* **隨機亂序出題**：採用 Fisher-Yates 演算法進行題目與選項亂序，並自動從字彙庫中隨機抽取 3 個混淆字彙生成四選一單選題。
* **即時答題反饋**：答對高亮綠色，答錯高亮紅色並即時將單字寫入本機 LocalStorage 錯字池（初始設為 Leitner Box 1）。

### 3. 錯字複習模式 (Review Mode)
* **Leitner 複習箱子演算法**：錯字本單字包含三個掌握度盒子（Box 1: 33%, Box 2: 66%, Box 3: 100%）。
  * 點選「記住了」：單字晉升一箱（Box N + 1）。超越 Box 3 則判定熟記，自動畢業移出錯字本。
  * 點選「忘記了」：單字降回 Box 1 重新學習。
* **進度可視化**：在錯字列表視圖中，實作動態掌握度進度條，高亮各錯字學習狀態。
* **雙模式檢視**：提供「清單列表」（顯示錯誤次數、手動一鍵移出）與一體化「卡片複習」兩種檢視模式。

### 4. PWA 離線支援
* **完全離線可用**：實作動態 Service Worker 腳本，採用 Stale-While-Revalidate 與 dynamic cache-on-fetch 策略，預快取網頁資源與字彙資料庫 `vocabulary.json`，在完全無網環境下仍可正常閱讀、小考與複習。

---

## 專案結構說明

```text
├── data/                      # 存放原始 PDF 數據的目錄 (Git 已忽略)
├── dist/                      # 生產環境打包目錄 (Git 已忽略)
├── public/
│   ├── sw.js                  # PWA Service Worker 離線快取腳本
│   └── vocabulary.json        # 結構化且清洗後的字彙資料庫
├── src/
│   ├── components/
│   │   ├── StudyMode.vue      # 背單字模組
│   │   ├── QuizMode.vue       # 小考測驗模組
│   │   └── ReviewMode.vue     # 錯字複習模組
│   ├── App.vue                # 網頁主要框架與頂部導覽列
│   ├── main.js                # 專案進入點、Element Plus 註冊與 PWA 啟用
│   └── style.css              # Obsidian 暗色調 CSS 變數系統與全域樣式定義
├── extract_vocabulary.py      # Python PDF 結構化數據解析腳本
├── clean_vocabulary.py        # 資料庫深度清洗腳本 (修復 OCR 雜訊)
├── vite.config.js             # Vite 設定檔 (base 設定為相對路徑)
├── package.json               # 專案依賴定義
└── README.md                  # 專案說明文件
```

---

## 本地開發與執行指引

### 1. 安裝與執行前端網頁

在專案目錄下執行以下指令安裝依賴並啟動開發伺服器：

```bash
# 安裝前端依賴包
npm install

# 啟動本地開發伺服器
npm run dev
```

啟動後，在瀏覽器打開 `http://localhost:5173/` 即可進行本地體驗。

### 2. 生產環境編譯

如果您要進行生產部署，請執行以下指令打包：

```bash
# 進行生產打包
npm run build
```

打包後產生的 `dist/` 資料夾內所有檔案，可以直接部署至您的 **GitHub Pages** 服務中。

### 3. 字彙庫解析與更新 (Python)

字彙資料庫已隨附於專案中（`public/vocabulary.json`）。若您需要從 raw PDF 重新解析，請使用以下步驟：

```bash
# 創建並啟動虛擬環境 (Windows)
python -m venv venv
.\venv\Scripts\activate

# 安裝 PDF 解析依賴
pip install pypdf

# 執行 PDF 解析萃取腳本 (生成 vocabulary.json)
python extract_vocabulary.py

# 執行 OCR 數據清洗與錯字修復
python clean_vocabulary.py
```

*注意：`data/` 目錄因包含原書 PDF 著作權內容，已於 Git 中忽略，重新解析前需手動將 PDF 置於 `data/` 目錄中。*
