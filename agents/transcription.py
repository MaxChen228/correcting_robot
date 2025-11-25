"""
Agent 1: Transcription
手寫辨識與標準答案對齊
"""
import google.generativeai as genai
import streamlit as st
import traceback
from typing import List, Optional
from PIL import Image

from config.settings import Config


def process(user_images: List[Image.Image], answer_image: Image.Image, debug_mode: bool = False) -> Optional[str]:
    """
    Agent 1: Digitizes handwriting and aligns it with the standard answer.

    Args:
        user_images: List of user handwriting images
        answer_image: Standard answer image
        debug_mode: Show detailed error messages

    Returns:
        JSON string or None if error occurs
    """
    model = genai.GenerativeModel(Config.GEMINI_MODEL)

    prompt = """
    你是一個專業的文字辨識與對齊助理。
    任務：
    1. 讀取「使用者手寫英文翻譯練習」的圖片（可能有多張）。
    2. 讀取「標準答案」的圖片（通常是一張教科書或講義截圖）。
    3. 請將每一題的「使用者手寫 (User)」與對應的「標準答案 (Standard)」精準對齊。

    輸出格式要求：
    請直接輸出一個純 JSON Array，不要有任何 Markdown 標記或額外文字 (如 ```json ... ```）。
    格式如下：
    [
        {
            "id": "1.1",
            "user": "User's handwritten text here...",
            "standard": "Standard answer text here..."
        },
        {
            "id": "1.2",
            "user": "...",
            "standard": "..."
        }
    ]

    注意：
    - 忽略非翻譯題目的雜訊。
    - 如果手寫字跡潦草，請根據上下文盡量辨識。
    - 題號請依照圖片上的標示（如 1.1, 1.2, 2.1 等）。
    """

    # Combine content: Prompt + User Images + Answer Image
    content = [prompt]
    for img in user_images:
        content.append(img)
    content.append(answer_image)

    try:
        response = model.generate_content(content)
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
        st.error(f"Agent 1 Error: {type(e).__name__}: {str(e)}")
        if debug_mode:
            st.code(traceback.format_exc(), language='python')
        return None
