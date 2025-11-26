"""
Agent 3: Flashcards
單字卡生成與知識萃取
"""
import google.generativeai as genai
import streamlit as st
import traceback
from typing import Optional

from config.settings import Config


def process(correction_json: str, debug_mode: bool = False) -> Optional[str]:
    """
    Agent 3: Generates flashcards from the corrections.

    Args:
        correction_json: JSON string from Agent 2
        debug_mode: Show detailed error messages

    Returns:
        CSV string or None if error occurs
    """
    model = genai.GenerativeModel(Config.GEMINI_MODEL)

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
      * 注意到變化(精確動詞搭配)
      * 進入青春期(慣用表達)

    Back (背面) 格式：
    - 英文結構 + 簡短重點說明 + (Ex: 例句)
    - 範例：
      * As + S + V (Ex: As teenagers reach puberty, they notice changes in their bodies.)
      * tune in to (Ex: I tune in to the BBC news every morning.)
      * grammar (Ex: Grammar is the rule system of a language.)
      * Much to one's disappointment (Ex: Much to his disappointment, she said no.)
      * notice changes in (Ex: She noticed changes in his behavior.)
      * reach puberty (Ex: Most girls reach puberty between ages 10-14.)

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

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        st.error(f"Agent 3 Error: {type(e).__name__}: {str(e)}")
        if debug_mode:
            st.code(traceback.format_exc(), language='python')
        return None
