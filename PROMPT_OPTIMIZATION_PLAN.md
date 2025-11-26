# Agent Prompt 優化計劃
## Handwriting Translation Correction System

---

## 📋 計劃概述

### 目標
優化 Agent 2（批改）和 Agent 3（單字卡）的 AI Prompt，使批改更精準地以標準答案為基準，並讓單字卡包含優質英文用法而非僅限錯誤。

### 修改範圍
- **Agent 2 (`agents/correction.py`)**: 強化「標準答案為聖經」的導向
- **Agent 3 (`agents/flashcards.py`)**: 新增「記錄優質用法」的功能

### 核心改變
1. Agent 2: 從「比對找錯」轉為「以標準答案為絕對參考」
2. Agent 3: 從「學習錯誤」擴展為「學習錯誤 + 優質用法」

---

## 🔍 現狀分析

### Agent 2 - 當前問題

**現有 Prompt 重點（第 26-63 行）**：
```
任務：
針對每一題，比對 User 的寫作與 Standard 標準答案，指出問題並提供修正版本。
```

**問題點**：
1. **平等比對**：「比對 User 的寫作與 Standard」暗示兩者地位相等
2. **修正版本不明確**：「The best corrected version」沒有明確說明應該等同於 Standard
3. **缺乏權威性**：未強調 Standard 是唯一正確的參考基準
4. **可能過度解讀**：AI 可能會自行判斷「更好的寫法」而偏離 Standard

**實際影響**：
- AI 可能給出「更自然」但不符合標準答案的修正
- 使用者無法準確知道與標準答案的差距
- 批改重點可能放在「改善」而非「對齊標準」

### Agent 3 - 當前問題

**現有 Prompt 重點（第 26-62 行）**：
```
任務：
從批改內容與標準答案中，提煉出使用者需要學習的「單字」、「片語」或「句型」，製作成簡潔易記的單字卡。
```

**問題點**：
1. **僅關注錯誤**：「需要學習的」暗示只提取有問題的部分
2. **遺漏優質用法**：沒有指示提取標準答案中的好句型
3. **學習範圍受限**：使用者無法從正確的標準答案中學到新用法

**實際影響**：
- 單字卡僅包含錯誤更正，缺乏正面學習材料
- 標準答案中的優美句型、慣用語被忽略
- 學習體驗偏向「糾錯」而非「吸收好用法」

---

## ✨ 優化策略

### Agent 2 - 優化方向

#### 核心原則
**Standard Answer = 參考聖經 (Golden Standard)**

#### 主要調整
1. **明確權威性**：標準答案是唯一正確的參考
2. **修正目標**：修正版本應盡可能與標準答案一致
3. **差異分析**：feedback 重點在「與標準答案的差異」
4. **減少主觀判斷**：避免 AI 自行「改善」超出標準答案的範圍

#### Prompt 結構調整
```
舊：比對 User 的寫作與 Standard 標準答案
新：以 Standard 標準答案為絕對參考，檢視 User 的寫作與其差異
```

### Agent 3 - 優化方向

#### 核心原則
**學習來源 = 錯誤更正 + 優質用法**

#### 主要調整
1. **雙軌學習**：同時提取錯誤和優質用法
2. **正面學習**：標準答案中的好句型、慣用語
3. **區分標記**：可選擇性標記卡片來源（錯誤/優質用法）
4. **平衡數量**：確保不只是錯誤卡片

#### Prompt 結構調整
```
舊：提煉出使用者需要學習的「單字」、「片語」或「句型」
新：提煉兩類知識點：
    1. 使用者寫錯的部分（錯誤更正）
    2. 標準答案中的優質用法（值得學習的好句型）
```

---

## 📝 新版 Prompt 設計

### Agent 2 - 新版 Prompt

**位置**：`agents/correction.py` 第 26-63 行

**新版完整 Prompt**：
```python
    prompt = f"""
    你是一位專業的英文批改老師。請務必使用繁體中文。

    **重要：Standard 標準答案是絕對的參考基準（參考聖經），修正版本必須盡可能與其一致。**

    輸入資料 (JSON):
    {transcription_json}

    任務：
    針對每一題，以 Standard 標準答案為唯一正確的參考基準，檢視 User 的寫作與其差異，並提供符合標準答案的修正版本。

    批改原則：
    1. **Standard 是唯一標準**：修正版本應該盡可能等同於 Standard 標準答案
    2. **以 Standard 為準**：即使 User 的寫法「也算正確」，若與 Standard 不同，仍應指出差異
    3. **忠於 Standard**：不要自行創造「更好的寫法」，而是引導向 Standard 對齊
    4. **差異為重點**：feedback 應聚焦在「User 如何偏離 Standard」以及「Standard 的正確寫法」

    輸出格式要求：
    請直接輸出一個純 JSON Array，不要有任何 Markdown 標記（如 **, ##, 【】等）。
    格式如下：
    [
        {{
            "id": "1.1",
            "user": "User's original text",
            "correction": "Standard answer text (or closest match to Standard)",
            "feedback": [
                "第一個與標準答案的差異說明",
                "第二個與標準答案的差異說明"
            ]
        }},
        ...
    ]

    Correction 撰寫原則：
    - correction 欄位應該直接使用或高度接近 Standard 標準答案
    - 如果 User 的寫作完全正確且與 Standard 一致，correction 應與 Standard 完全相同
    - 如果 User 的寫作有誤，correction 應導向 Standard 的正確寫法

    Feedback 撰寫原則：
    - feedback 是一個陣列，每個元素是一個獨立的「與標準答案的差異點」
    - 每個差異點用 1-2 句話清楚說明：
      * User 寫了什麼
      * Standard 標準答案是什麼
      * 為什麼 Standard 的寫法是正確的
    - 如果 User 與 Standard 完全一致，feedback 可以是空陣列 [] 或給予正面肯定
    - 使用純文字，不使用任何 markdown 或 HTML 標記
    - 保持專業但易懂的語氣

    範例 feedback：
    [
        "User 使用 'practices'，但 Standard 標準答案使用 'drills'。在描述「聽力練習」時，'drills' 更精確表達重複訓練的概念。",
        "User 用 'it' 指代複數的 'practices'，造成單複數不一致。Standard 使用 'them' 正確對應複數名詞。",
        "User 的句型完全符合 Standard 標準答案，用法正確。"
    ]

    **再次提醒：Standard 標準答案是絕對的參考基準，修正應以對齊 Standard 為最高優先。**
    """
```

**關鍵變更總結**：
1. 新增粗體強調：「Standard 是絕對參考基準」
2. 任務描述改為：「以 Standard 為唯一正確參考」
3. 新增「批改原則」區塊，明確 4 項核心規則
4. correction 說明改為：「應直接使用或高度接近 Standard」
5. feedback 重點改為：「與標準答案的差異點」
6. 新增範例強調 Standard 導向
7. 最後再次粗體提醒

### Agent 3 - 新版 Prompt

**位置**：`agents/flashcards.py` 第 26-62 行

**新版完整 Prompt**：
```python
    prompt = f"""
    你是一個專業的單字卡製作助理。請務必使用繁體中文。

    輸入資料 (批改結果 JSON):
    {correction_json}

    任務：
    從批改內容與標準答案中，提煉出兩類知識點製作成簡潔易記的單字卡：

    **類型 1：錯誤更正（User 寫錯的部分）**
    - 使用者犯錯的「單字」、「片語」或「句型」
    - 從 feedback 和 correction 中提取需要改正的知識點

    **類型 2：優質用法（值得學習的好句型）**
    - Standard 標準答案中出現的優美句型、慣用語、精確用詞
    - 即使 User 沒有寫錯，只要 Standard 中有值得學習的用法，也應該製作成卡片
    - 例如：特殊句型、道地片語、精確的動詞搭配、優雅的表達方式

    **重要：不要只記錄錯誤！優質用法同樣重要，可以幫助使用者吸收標準答案中的好寫法。**

    輸出格式要求：
    1. 直接輸出 CSV 格式，包含 Header: Front,Back
    2. 使用純文字，適合直接匯入 Anki 或 Quizlet
    3. 優質用法卡片數量應與錯誤更正卡片達到平衡（不要只有錯誤）

    Front (正面) 格式：
    - 中文詞彙或片語 + (用法說明)
    - 範例：
      * 隨著(連接詞用法)
      * 收聽(搭配介系詞to)
      * 文法(不可數學科名)
      * 讓某人大大失望的是(情緒片語)
      * 注意到變化(精確動詞搭配) ← 優質用法範例
      * 進入青春期(慣用表達) ← 優質用法範例

    Back (背面) 格式：
    - 英文結構 + 簡短重點說明 + (Ex: 例句)
    - 範例：
      * As + S + V (Ex: As teenagers reach puberty, they notice changes in their bodies.)
      * tune in to (Ex: I tune in to the BBC news every morning.)
      * grammar (Ex: Grammar is the rule system of a language.)
      * Much to one's disappointment (Ex: Much to his disappointment, she said no.)
      * notice changes in (Ex: She noticed changes in his behavior.) ← 優質用法
      * reach puberty (Ex: Most girls reach puberty between ages 10-14.) ← 優質用法

    重要原則：
    - 每張卡片聚焦一個知識點
    - 保持簡潔，避免冗長解釋
    - 不要使用「注意」、「辨析」、「修正」等學術用語（除非是描述用法類型）
    - 例句要實用且貼近日常使用情境
    - 所有中文說明必須使用繁體中文
    - 純文字格式，不使用任何標記語言
    - **平衡錯誤與優質用法**：確保單字卡既能糾錯，也能學習好用法

    提取策略：
    1. 先從 feedback 提取明確的錯誤更正
    2. 再從 Standard 標準答案中尋找值得學習的句型、片語、用詞
    3. 優先提取具有「可複用性」的用法（能用在其他情境的表達方式）
    4. 避免過於簡單或基礎的詞彙（如 "is", "the" 等）

    **記住：優質用法卡片與錯誤更正卡片同等重要！**
    """
```

**關鍵變更總結**：
1. 任務明確分為「類型 1：錯誤更正」和「類型 2：優質用法」
2. 新增粗體強調：「不要只記錄錯誤！優質用法同樣重要」
3. Front/Back 範例中加入優質用法示例（標註 ← 優質用法）
4. 新增「提取策略」區塊，明確 4 步驟流程
5. 重要原則中新增「平衡錯誤與優質用法」
6. 最後再次粗體提醒

---

## 🔧 實施步驟

### Step 1: Agent 2 修改

**檔案**：`/Users/chenliangyu/Desktop/correcting_robot/agents/correction.py`

**修改位置**：第 26-63 行（完整替換 prompt 變數）

**具體操作**：
1. 找到 `prompt = f"""` 開始的位置（第 26 行）
2. 刪除從第 26 行到第 63 行的全部內容（包含結尾的 `"""`）
3. 替換為上方「Agent 2 - 新版 Prompt」的完整內容
4. 確保縮排正確（4 個空格）
5. 確保 f-string 格式正確（`{transcription_json}` 能正確插入）

**驗證點**：
- [ ] prompt 字串正確關閉（結尾有 `"""`）
- [ ] f-string 變數 `{transcription_json}` 存在且位置正確
- [ ] 中文繁體字無亂碼
- [ ] 無語法錯誤（Python 能正確解析）

### Step 2: Agent 3 修改

**檔案**：`/Users/chenliangyu/Desktop/correcting_robot/agents/flashcards.py`

**修改位置**：第 26-62 行（完整替換 prompt 變數）

**具體操作**：
1. 找到 `prompt = f"""` 開始的位置（第 26 行）
2. 刪除從第 26 行到第 62 行的全部內容（包含結尾的 `"""`）
3. 替換為上方「Agent 3 - 新版 Prompt」的完整內容
4. 確保縮排正確（4 個空格）
5. 確保 f-string 格式正確（`{correction_json}` 能正確插入）

**驗證點**：
- [ ] prompt 字串正確關閉（結尾有 `"""`）
- [ ] f-string 變數 `{correction_json}` 存在且位置正確
- [ ] 中文繁體字無亂碼
- [ ] 無語法錯誤（Python 能正確解析）

### Step 3: 功能測試

**測試案例設計**：

#### 測試案例 1：Agent 2 - 標準答案導向
**輸入**：
```json
[
  {
    "id": "1.1",
    "user": "I like to listen music.",
    "standard": "I enjoy listening to music."
  }
]
```

**預期輸出**：
- correction 應該是 "I enjoy listening to music."（完全符合 Standard）
- feedback 應該提到：
  1. User 用 "like to"，Standard 用 "enjoy" 更精確
  2. User 缺少介系詞 "to"
  3. User 用 "listen"，Standard 用 "listening"（動名詞）

#### 測試案例 2：Agent 3 - 包含優質用法
**輸入**：
```json
[
  {
    "id": "1.1",
    "user": "As people get older, they see changes.",
    "correction": "As people grow older, they notice changes in their bodies.",
    "feedback": [
      "User 用 'get older'，Standard 用 'grow older' 更自然。",
      "User 用 'see'，Standard 用 'notice' 更精確表達「察覺」之意。",
      "User 缺少 'in their bodies' 具體說明變化的範圍。"
    ]
  }
]
```

**預期輸出 CSV 應包含**：
- 錯誤更正：grow older (vs. get older), notice (vs. see), in their bodies (具體化)
- 優質用法：As + S + V (連接詞句型), notice changes in (精確搭配)

**驗證標準**：
- [ ] Agent 2 的 correction 高度接近或等同 Standard
- [ ] Agent 2 的 feedback 明確對比 User vs. Standard
- [ ] Agent 3 同時輸出錯誤更正和優質用法卡片
- [ ] Agent 3 的優質用法卡片數量合理（至少 30-40% 比例）

---

## 📊 預期效果

### Agent 2 改善

#### Before（舊版）
- **批改方向**：找出錯誤，提供「較好」的版本
- **參考標準**：AI 自行判斷「正確性」
- **可能問題**：修正版本可能偏離標準答案

#### After（新版）
- **批改方向**：對齊標準答案，指出與 Standard 的差異
- **參考標準**：Standard 是唯一絕對基準
- **優勢**：使用者能精確知道標準答案的要求

### Agent 3 改善

#### Before（舊版）
- **學習內容**：僅提取錯誤更正
- **單字卡性質**：100% 糾錯型
- **學習體驗**：偏向負面（只看錯誤）

#### After（新版）
- **學習內容**：錯誤更正 + 優質用法
- **單字卡性質**：50% 糾錯型 + 50% 正面學習型
- **學習體驗**：平衡學習（糾錯 + 吸收好用法）

---

## ⚠️ 潛在風險與應對

### 風險 1：Agent 2 過度嚴格

**問題**：
- 可能將「合理的替代寫法」也標記為錯誤
- 使用者可能感到挫折（明明寫對了卻被糾正）

**應對策略**：
- 在 feedback 中加入「User 的寫法也正確，但 Standard 使用...」
- 強調「對齊 Standard」而非「錯誤」
- 可選：future iteration 加入「嚴格度」參數

### 風險 2：Agent 3 優質用法過多

**問題**：
- 可能提取過多基礎用法
- 單字卡數量暴增，使用者負擔重

**應對策略**：
- Prompt 中強調「可複用性」和「避免過於簡單」
- 設定數量上限（如「每題最多提取 3-5 個優質用法」）
- 可選：future iteration 加入「難度篩選」

### 風險 3：CSV 格式錯誤

**問題**：
- AI 可能在 CSV 中加入不必要的引號或換行
- 特殊字元（逗號、引號）可能破壞格式

**應對策略**：
- Prompt 中強調「純文字格式」
- 測試時驗證 CSV 可正確匯入 Anki
- 可選：加入 CSV 格式後處理（escape 特殊字元）

---

## 🧪 測試計劃

### 階段 1：單元測試（Agent 獨立測試）

**Agent 2 測試**：
1. 準備 5 組測試資料（User 完全錯誤、部分錯誤、完全正確）
2. 驗證 correction 是否對齊 Standard
3. 驗證 feedback 是否明確對比 User vs. Standard
4. 檢查 JSON 格式正確性

**Agent 3 測試**：
1. 準備 3 組測試資料（含明顯錯誤、含優質句型、混合）
2. 驗證是否同時輸出錯誤更正和優質用法
3. 驗證優質用法卡片比例（應 ≥ 30%）
4. 檢查 CSV 格式正確性（可匯入 Anki）

### 階段 2：整合測試（完整流程）

1. 使用真實手寫圖片 + 標準答案
2. 運行完整 3-agent 流程
3. 驗證：
   - Agent 1 辨識正確
   - Agent 2 修正對齊 Standard
   - Agent 3 同時輸出糾錯 + 優質用法
4. 檢查使用者體驗（UI 顯示、CSV 下載）

### 階段 3：實戰測試

1. 選擇 3-5 個真實使用場景
2. 邀請使用者試用（如果可能）
3. 收集回饋：
   - Agent 2 的修正是否符合預期？
   - Agent 3 的優質用法是否有用？
   - 單字卡數量是否合理？

---

## 📋 實施檢查清單

### 修改前準備
- [ ] 備份當前 `agents/correction.py`
- [ ] 備份當前 `agents/flashcards.py`
- [ ] Git commit 當前版本（便於回滾）

### Agent 2 修改
- [ ] 開啟 `agents/correction.py`
- [ ] 定位到第 26-63 行
- [ ] 替換為新版 prompt
- [ ] 檢查縮排和語法
- [ ] 儲存檔案

### Agent 3 修改
- [ ] 開啟 `agents/flashcards.py`
- [ ] 定位到第 26-62 行
- [ ] 替換為新版 prompt
- [ ] 檢查縮排和語法
- [ ] 儲存檔案

### 測試驗證
- [ ] 執行 Agent 2 單元測試（測試案例 1）
- [ ] 執行 Agent 3 單元測試（測試案例 2）
- [ ] 執行完整流程整合測試
- [ ] 驗證 UI 顯示正常
- [ ] 驗證 CSV 可正常下載和匯入

### 最終確認
- [ ] 所有測試通過
- [ ] 無 Python 語法錯誤
- [ ] 無 AI 回應格式錯誤
- [ ] 使用者體驗符合預期
- [ ] Git commit 新版本

---

## 📈 效果評估指標

### 定量指標

| 指標 | 舊版 | 新版目標 | 測量方法 |
|------|------|----------|----------|
| Agent 2 修正版本與 Standard 相似度 | ~70% | ≥90% | 字串相似度比對 |
| Agent 2 feedback 提及 Standard 比例 | ~30% | 100% | 文本分析 |
| Agent 3 優質用法卡片比例 | 0% | 30-50% | 卡片分類統計 |
| Agent 3 單字卡總數 | 基準 | 1.3-1.5x | 數量統計 |

### 定性指標

**Agent 2**：
- 修正版本是否明確對齊 Standard？
- feedback 是否清楚說明與 Standard 的差異？
- 使用者是否理解「標準答案的要求」？

**Agent 3**：
- 優質用法卡片是否實用？
- 卡片內容是否平衡（糾錯 vs. 學習）？
- 使用者是否感到「正面學習」的體驗？

---

## 🔮 未來優化方向

### 短期（1-2 週）
1. **Agent 2 嚴格度調整**：根據使用者回饋微調「對齊 Standard」的嚴格程度
2. **Agent 3 數量控制**：加入「每題最多 N 張卡片」的限制
3. **錯誤處理**：加入 prompt 格式驗證和錯誤重試機制

### 中期（1-2 月）
1. **使用者偏好設定**：讓使用者選擇「嚴格模式」vs.「寬鬆模式」
2. **優質用法難度分級**：標記卡片難度（基礎/中級/進階）
3. **卡片分類標籤**：在 CSV 中加入「類型」欄位（錯誤/優質用法）

### 長期（3+ 月）
1. **AI 微調**：使用真實資料微調模型，提升批改準確度
2. **多版本標準答案**：支援多個合理的標準寫法
3. **個人化學習**：根據使用者錯誤頻率調整卡片優先級

---

## 💡 補充說明

### 為什麼要強調「Standard 為聖經」？

**教育情境考量**：
- 在學校考試中，標準答案通常有特定的評分標準
- 教師可能要求特定句型或用詞
- 學生需要知道「考試要求的寫法」而非「任意正確寫法」

**學習效果考量**：
- 明確的參考基準減少混淆
- 使用者能精確知道「目標寫法」
- 便於自我檢視與進步追蹤

### 為什麼要加入「優質用法」？

**正面學習心理**：
- 純糾錯容易打擊學習動機
- 正面範例提供「可模仿的目標」
- 平衡學習體驗（糾錯 + 吸收）

**實用性提升**：
- 標準答案通常經過精心設計，包含優質用法
- 學習這些用法能提升整體寫作水平
- 單字卡成為「寶庫」而非「錯題本」

---

## 📞 實施支援

### 如遇問題

**語法錯誤**：
- 檢查 f-string 格式：`{transcription_json}` 和 `{correction_json}`
- 檢查三重引號配對：`"""`
- 檢查縮排（應為 4 個空格）

**AI 回應格式錯誤**：
- 檢查 prompt 中的範例格式
- 增加「不要使用 Markdown」的強調
- 測試時使用 debug_mode 查看原始輸出

**效果不如預期**：
- 先確認 prompt 是否正確替換
- 使用明確的測試案例驗證
- 考慮調整 prompt 措辭或範例

---

## ✅ 計劃總結

### 核心改變
1. **Agent 2**：從「比對找錯」→「以 Standard 為絕對參考」
2. **Agent 3**：從「僅糾錯」→「糾錯 + 學習優質用法」

### 預期效果
- 批改更精準對齊標準答案
- 單字卡內容更豐富平衡
- 使用者學習體驗更正面

### 實施難度
- **技術難度**：低（僅修改 prompt 文本）
- **測試難度**：中（需驗證 AI 輸出品質）
- **風險程度**：低（易於回滾）

### 時間估計
- 修改時間：10-15 分鐘
- 測試時間：30-45 分鐘
- 總計：約 1 小時

---

**準備好後，即可開始實施！**
