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

    **核心原則：Standard 標準答案是優質的參考範本，但 User 的正確寫法也應該被認可。只有真實錯誤才需要修正。**

    輸入資料 (JSON):
    {transcription_json}

    任務：
    針對每一題，參考 Standard 標準答案，檢視 User 的寫作，區分「真實錯誤」與「可接受的差異」，並給予專業的批改建議。

    批改分類：

    **1. 真實錯誤（Must Fix）**
    - 文法錯誤（如：時態錯誤、主詞動詞不一致、介系詞誤用）
    - 拼字錯誤（如：develope → develop）
    - 詞性誤用（如：economic → economically）
    - 搭配不當（如：單複數不一致、冠詞缺漏）
    → 這些情況 correction 必須修正

    **2. 可改進之處（Can Improve）**
    - User 的寫法正確，但 Standard 的用詞更精確、更道地
    - User 的句型正確，但 Standard 的結構更優雅
    - User 的表達通順，但 Standard 的語氣更合適
    → 這些情況 correction 保持 User 原文，在 feedback 中「建議」參考 Standard

    **3. 完全正確（Well Done）**
    - User 的寫法與 Standard 相同或相近
    - User 的寫法雖與 Standard 不同，但同樣正確且無明顯差距
    → 這些情況 correction = user 原文，feedback 給予肯定或留空

    輸出格式要求：
    請直接輸出一個純 JSON Array，不要有任何 Markdown 標記（如 **, ##, 【】等）。
    格式如下：
    [
        {{
            "id": "1.1",
            "user": "User's original text",
            "correction": "修正後的版本（僅在有真實錯誤時修改，否則保持原文）",
            "feedback": [
                "批改意見（區分錯誤與建議）"
            ]
        }},
        ...
    ]

    Correction 撰寫原則：
    - **僅在有真實錯誤時修改**，其他情況保持 User 原文
    - 修正時可參考 Standard 的正確用法，但不要強制對齊所有用詞
    - 如果 User 完全正確，correction 就是 User 的原文

    Feedback 撰寫原則：
    - feedback 是一個陣列，每個元素是一個獨立的批改意見
    - **明確區分錯誤與建議**：

      錯誤類：
      「User 寫作 'the economic of Greece' 有文法錯誤（economic 為形容詞，不能接 of），應改為 'the economy of Greece' 或 'economically dependent'。」

      建議類：
      「User 使用 'trip blogs' 也是正確的，Standard 使用 'travel blogs online' 更為常見。如欲更貼近標準答案，可考慮此用法。」

      肯定類：
      「User 的句型與用詞正確，表達清楚。」

    - 使用純文字，不使用任何 markdown 或 HTML 標記
    - 保持專業但鼓勵性的語氣

    範例 feedback（錯誤類）：
    [
        "User 寫作 'one fifth jobs' 缺少介系詞，應為 'one fifth of jobs'。分數後接名詞時必須加 'of'。"
    ]

    範例 feedback（建議類）：
    [
        "User 使用 'get through language barriers' 也是正確的片語，Standard 使用 'overcome the language barrier'。兩者意思相近，Standard 的用詞稍微更正式一些，可作為參考。"
    ]

    範例 feedback（混合類）：
    [
        "User 拼字錯誤 'develope' 應為 'develop'（必須修正）。",
        "User 使用 'have more recognition of' 文法正確但較不自然，Standard 使用 'know more about' 更為口語化，建議參考。"
    ]

    **再次提醒：只修正真實錯誤，不要強制對齊 Standard 的所有用詞選擇。User 的正確寫法應該被認可。**
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
