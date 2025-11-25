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

    輸入資料 (JSON):
    {transcription_json}

    任務：
    針對每一題，比對 User 的寫作與 Standard 標準答案，指出問題並提供修正版本。

    輸出格式要求：
    請直接輸出一個純 JSON Array，不要有任何 Markdown 標記（如 **, ##, 【】等）。
    格式如下：
    [
        {{
            "id": "1.1",
            "user": "User's original text",
            "correction": "The best corrected version",
            "feedback": [
                "第一個錯誤點的說明",
                "第二個錯誤點的說明"
            ]
        }},
        ...
    ]

    Feedback 撰寫原則：
    - feedback 是一個陣列，每個元素是一個獨立的錯誤點
    - 每個錯誤點用 1-2 句話清楚說明：哪裡錯了、為什麼錯、正確用法
    - 如果只有一個錯誤，陣列就只有一個元素
    - 使用純文字，不使用任何 markdown 或 HTML 標記
    - 保持專業但易懂的語氣

    範例 feedback：
    [
        "原文使用 'practices' 是複數，但後面用 'it' 指代是單數，應該用 'them'。",
        "'drills' 比 'practices' 更適合描述聽力練習。"
    ]
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
