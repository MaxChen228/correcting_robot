"""
Agent 2: Correction
深度批改與錯誤分析
"""
import google.generativeai as genai
import streamlit as st
import traceback
from typing import Optional

from config.settings import Config


def process(transcription_json: str, debug_mode: bool = False) -> Optional[str]:
    """
    Agent 2: Analyzes the text and provides corrections.

    Args:
        transcription_json: JSON string from Agent 1
        debug_mode: Show detailed error messages

    Returns:
        JSON string or None if error occurs
    """
    model = genai.GenerativeModel(Config.GEMINI_MODEL)

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

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    except Exception as e:
        st.error(f"Agent 2 Error: {type(e).__name__}: {str(e)}")
        if debug_mode:
            st.code(traceback.format_exc(), language='python')
        return None
