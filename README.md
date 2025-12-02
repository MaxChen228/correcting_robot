# 📝 Handwriting Translation Correction System

AI 驅動的手寫翻譯批改系統，使用 Google Gemini 多模態 AI 自動辨識、批改手寫英文翻譯作業，並生成個人化單字卡。

🔗 **線上體驗**: [Streamlit Cloud 部署版本](https://maxchen228-correcting-robot-app-ivwelt.streamlit.app)

---

## ✨ 核心功能

### 🤖 三階段 AI 處理流程

1. **Agent 1: 智能辨識**
   - 辨識手寫英文內容（支援多張圖片）
   - 自動對齊標準答案
   - 精準 OCR 文字識別

2. **Agent 2: 深度批改**
   - 比對使用者答案與標準答案
   - 提供詳細的錯誤說明
   - 給出最佳修正版本

3. **Agent 3: 單字卡生成**
   - 自動提煉關鍵詞彙和片語
   - 生成 Anki/Quizlet 格式 CSV
   - 包含用法說明和例句

### 💾 雲端持久化儲存

- **Supabase 資料庫整合**：所有批改記錄自動同步到雲端
- **跨裝置訪問**：隨時隨地查看歷史記錄
- **永久保存**：不怕資料遺失

### 🎨 清晰易用介面

- **卡片式批改結果**：左右對比原文與修正
- **簡潔說明**：每個錯誤點獨立呈現
- **Debug 模式**：查看完整 AI 輸出（開發者友善）

---

## 🚀 技術棧

### 核心技術
- **[Streamlit](https://streamlit.io/)** - 快速 Web 應用框架
- **[Google Gemini 3.0 Pro Preview](https://ai.google.dev/)** - 多模態 AI 模型
- **[Supabase](https://supabase.com/)** - 開源 Firebase 替代方案

### Python 依賴
```
streamlit
google-generativeai
supabase
pandas
python-dotenv
pillow
```

---

## 📦 安裝與部署

### 本地開發

1. **克隆專案**
```bash
git clone https://github.com/MaxChen228/correcting_robot.git
cd correcting_robot
```

2. **安裝依賴**
```bash
pip install -r requirements.txt
```

3. **設定環境變數**
```bash
cp .env.example .env
# 編輯 .env，填入你的 API 金鑰
```

4. **運行應用**
```bash
streamlit run app.py
```

### ☁️ Streamlit Cloud 部署

1. Fork 此專案到你的 GitHub
2. 前往 [Streamlit Cloud](https://share.streamlit.io/)
3. 連接你的 GitHub 倉庫
4. 在 **Secrets** 設定中添加：

```toml
GOOGLE_API_KEY = "你的-Google-API-Key"
SUPABASE_URL = "https://你的專案ID.supabase.co"
SUPABASE_KEY = "你的-Supabase-Secret-Key"
```

---

## ⚙️ Supabase 配置

### 1. 創建專案
- 前往 [Supabase](https://supabase.com/)
- 創建新專案
- 選擇 Tokyo 或 Singapore 區域

### 2. 創建資料表
在 **SQL Editor** 執行：

```sql
CREATE TABLE correction_history (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  timestamp TEXT,
  corrections JSONB,
  flashcards TEXT
);

-- 關閉 RLS（個人使用）
ALTER TABLE correction_history DISABLE ROW LEVEL SECURITY;
```

### 3. 獲取 API 金鑰
- 前往 **Settings** → **API**
- 複製 **Project URL** 和 **Secret Key**（`sb_secret_...`）

> ⚠️ **重要**：服務器端應用必須使用 **Secret Key**，不是 Publishable Key

詳細設定請參考 [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)

---

## 📖 使用方法

### 基本流程

1. **上傳手寫圖片**
   - 支援 PNG、JPG、JPEG 格式
   - 可上傳多張（最多 200MB/張）

2. **上傳標準答案**
   - 教科書或講義截圖
   - 系統會自動對齊題號

3. **開始分析**
   - 點擊 "Start Analysis 🚀"
   - 等待 AI 處理（通常 1-3 分鐘）

4. **查看結果**
   - 批改結果：左右對比原文與修正
   - 錯誤說明：簡潔清楚的文字說明
   - 單字卡：可直接下載 CSV 匯入 Anki

### 歷史記錄

- 所有批改自動保存到雲端
- 側邊欄顯示累積批改次數
- 隨時查看過往記錄

---

## 🛠️ 開發說明

### 專案結構
```
correcting_robot/
├── app.py                          # 主應用程式
├── requirements.txt                # Python 依賴
├── .env.example                    # 環境變數範例
├── .streamlit/
│   └── secrets.toml.example       # Streamlit Cloud 配置範例
├── SUPABASE_SETUP.md              # Supabase 設定教學
└── README.md                       # 本文件
```

### 核心流程

```python
# 1. Agent 1 (Transcription): Digitizes handwriting and aligns with standard answers.
transcription_result = agent_transcription(user_images, answer_image)

# 2. Agent 2 (Correction): Analyzes errors and provides detailed feedback.
correction_result = agent_correction(transcription_result)

# 3. 自動保存到 Supabase
supabase.table("correction_history").insert({
    "timestamp": datetime.now().isoformat(),
    "corrections": correction_data,
}).execute()
```

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 開發重點
- 保持程式碼簡潔
- 所有 prompt 使用繁體中文
- 遵循第一性原理：簡單直接

---

## 📄 授權

MIT License

---

## 🙏 致謝

- **Google Gemini AI** - 強大的多模態 AI 能力
- **Supabase** - 免費且易用的雲端資料庫
- **Streamlit** - 快速打造 Web 應用的利器
- **Claude Code** - AI 輔助開發工具

---

## 📞 聯絡

- GitHub: [@MaxChen228](https://github.com/MaxChen228)
- 專案連結: [correcting_robot](https://github.com/MaxChen228/correcting_robot)

---

**⭐ 如果這個專案對你有幫助，請給一個 Star！**
