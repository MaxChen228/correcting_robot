# Supabase 設置教學

## 步驟 1：創建 Supabase 專案

1. 前往 https://supabase.com/
2. 用 GitHub 帳號登入
3. 點擊「New Project」
4. 填寫：
   - Project name: `correcting-robot`
   - Database Password: 設一個密碼
   - Region: 選 `Northeast Asia (Tokyo)` 或 `Southeast Asia (Singapore)`
5. 點擊「Create new project」（等待 1-2 分鐘）

## 步驟 2：創建資料表

在 Supabase 控制台：

1. 點擊左側 **SQL Editor**
2. 點擊「New query」
3. 貼上以下 SQL：

```sql
create table correction_history (
  id bigserial primary key,
  created_at timestamptz default now(),
  timestamp text,
  corrections jsonb,
  flashcards text
);
```

4. 點擊「Run」執行

## 步驟 3：獲取 API 金鑰

1. 點擊左側 **Project Settings** → **API**
2. 複製：
   - `Project URL` (例如：https://xxxxx.supabase.co)
   - `anon public` key (一長串字串)

## 步驟 4：配置應用

### 本地開發

1. 複製 `.env.example` 為 `.env`
2. 填入你的金鑰：

```env
GOOGLE_API_KEY=your-google-api-key
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Streamlit Cloud 部署

1. 在 Streamlit Cloud 的應用設定中
2. 點擊「Secrets」
3. 貼上（TOML 格式）：

```toml
GOOGLE_API_KEY = "your-google-api-key"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

4. 點擊「Save」

## 完成！

現在應用會自動保存所有批改記錄到 Supabase 雲端數據庫。

### 查看數據

在 Supabase 控制台：
- 點擊 **Table Editor**
- 選擇 `correction_history` 表
- 可以看到所有記錄
