import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io

# Load environment variables
load_dotenv()

# Configure Gemini API
# Users need to set GOOGLE_API_KEY in .env or via UI
api_key = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="Handwriting Correction AI",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Handwriting Translation Correction System")
st.markdown("""
Upload your handwritten translation exercises and the standard answer key.
The AI will transcribe, correct, and generate flashcards for you.
""")

# Sidebar for API Key if not in env
if not api_key:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
else:
    genai.configure(api_key=api_key)

# Debug Mode Toggle
st.sidebar.divider()
debug_mode = st.sidebar.checkbox("🐛 Debug Mode", value=False, help="顯示每個 Agent 的詳細輸出和預覽")


# --- Agent 1: Transcription ---
def agent_transcription(user_images, answer_image):
    """
    Agent 1: Digitizes handwriting and aligns it with the standard answer.
    Returns: JSON string.
    """
    model = genai.GenerativeModel('gemini-3-pro-preview')
    
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
        import traceback
        st.error(f"❌ Agent 1 錯誤: {type(e).__name__}: {str(e)}")
        with st.expander("🔍 查看錯誤詳情"):
            st.code(traceback.format_exc(), language='python')
        return None

# --- Agent 2: Correction ---
def agent_correction(transcription_json):
    """
    Agent 2: Analyzes the text and provides corrections.
    Returns: JSON string.
    """
    model = genai.GenerativeModel('gemini-3-pro-preview')
    
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
            "feedback": "簡潔說明錯誤原因和如何改正"
        }},
        ...
    ]

    Feedback 撰寫原則：
    - 用 2-3 句話清楚說明：哪裡錯了、為什麼錯、正確用法
    - 使用純文字，不使用任何 markdown 或 HTML 標記
    - 保持專業但易懂的語氣

    範例 feedback：
    "原文使用 'practices' 是複數，但後面用 'it' 指代是單數，應該用 'them'。另外 'drills' 比 'practices' 更適合描述聽力練習。"
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    except Exception as e:
        import traceback
        st.error(f"❌ Agent 2 錯誤: {type(e).__name__}: {str(e)}")
        with st.expander("🔍 查看錯誤詳情"):
            st.code(traceback.format_exc(), language='python')
        return None

# --- Agent 3: Flashcards ---
def agent_flashcards(correction_json):
    """
    Agent 3: Generates flashcards from the corrections.
    Returns: CSV string.
    """
    model = genai.GenerativeModel('gemini-3-pro-preview')
    
    prompt = f"""
    你是一個專業的單字卡製作助理。請務必使用繁體中文。

    輸入資料 (批改結果 JSON):
    {correction_json}

    任務：
    從批改內容與標準答案中，提煉出使用者需要學習的「單字」、「片語」或「句型」，製作成簡潔易記的單字卡。

    輸出格式要求：
    1. 直接輸出 CSV 格式，包含 Header: Front,Back
    2. 使用純文字，適合直接匯入 Anki 或 Quizlet

    Front (正面) 格式：
    - 中文詞彙或片語 + (用法說明)
    - 範例：
      * 隨著(連接詞用法)
      * 收聽(搭配介系詞to)
      * 文法(不可數學科名)
      * 讓某人大大失望的是(情緒片語)

    Back (背面) 格式：
    - 英文結構 + 簡短重點說明 + (Ex: 例句)
    - 範例：
      * As + S + V (Ex: As teenagers reach puberty, they notice changes in their bodies.)
      * tune in to (Ex: I tune in to the BBC news every morning.)
      * grammar (Ex: Grammar is the rule system of a language.)
      * Much to one's disappointment (Ex: Much to his disappointment, she said no.)

    重要原則：
    - 每張卡片聚焦一個知識點
    - 保持簡潔，避免冗長解釋
    - 不要使用「注意」、「辨析」、「修正」等學術用語
    - 例句要實用且貼近日常使用情境
    - 所有中文說明必須使用繁體中文
    - 純文字格式，不使用任何標記語言
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        import traceback
        st.error(f"❌ Agent 3 錯誤: {type(e).__name__}: {str(e)}")
        with st.expander("🔍 查看錯誤詳情"):
            st.code(traceback.format_exc(), language='python')
        return None

# --- UI Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload User Handwriting")
    user_files = st.file_uploader("Upload handwriting images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

with col2:
    st.subheader("2. Upload Standard Answer")
    answer_file = st.file_uploader("Upload answer key image", type=['png', 'jpg', 'jpeg'])

if st.button("Start Analysis 🚀"):
    if not api_key:
        st.error("Please provide a Google API Key to proceed.")
    elif not user_files or not answer_file:
        st.error("Please upload both handwriting images and the answer key.")
    else:
        # Process Images
        user_images = [Image.open(f) for f in user_files]
        answer_image = Image.open(answer_file)
        
        # --- Step 1: Transcription ---
        with st.status("🤖 Agent 1: 正在辨識手寫內容與標準答案...", expanded=True) as status:
            transcription_result = agent_transcription(user_images, answer_image)
            if transcription_result:
                # Parse and display stats
                try:
                    import json
                    transcription_data = json.loads(transcription_result)
                    question_count = len(transcription_data)
                    st.write(f"✅ 辨識完成！共 {question_count} 題")

                    # Preview first 2 items
                    if question_count > 0:
                        st.write("**預覽前 2 題：**")
                        for item in transcription_data[:2]:
                            st.markdown(f"- **{item.get('id', 'N/A')}**: User: `{item.get('user', '')[:50]}...` | Standard: `{item.get('standard', '')[:50]}...`")

                    # Debug mode: show full output
                    if debug_mode:
                        with st.expander("📋 查看完整辨識結果 (JSON)"):
                            st.json(transcription_data)

                except json.JSONDecodeError as e:
                    st.warning(f"⚠️ JSON 解析失敗: {e}")
                    st.write("✅ 辨識完成（但格式可能有問題）")
                    if debug_mode:
                        with st.expander("📋 查看原始輸出"):
                            st.text(transcription_result)

                status.update(label="Agent 1 完成", state="complete", expanded=False)
            else:
                status.update(label="Agent 1 失敗", state="error")
                st.stop()

        # --- Step 2: Correction ---
        with st.status("👩‍🏫 Agent 2: 正在進行批改與點評...", expanded=True) as status:
            correction_result = agent_correction(transcription_result)
            if correction_result:
                # Parse and display stats
                try:
                    import json
                    correction_data = json.loads(correction_result)
                    correction_count = len(correction_data)
                    st.write(f"✅ 批改完成！共批改 {correction_count} 題")

                    # Preview first 2 corrections
                    if correction_count > 0:
                        st.write("**預覽前 2 題批改：**")
                        for item in correction_data[:2]:
                            st.markdown(f"- **{item.get('id', 'N/A')}**: {item.get('feedback', '')[:80]}...")

                    # Debug mode: show full output
                    if debug_mode:
                        with st.expander("📋 查看完整批改結果 (JSON)"):
                            st.json(correction_data)

                except json.JSONDecodeError as e:
                    st.warning(f"⚠️ JSON 解析失敗: {e}")
                    st.write("✅ 批改完成（但格式可能有問題）")
                    if debug_mode:
                        with st.expander("📋 查看原始輸出"):
                            st.text(correction_result)

                status.update(label="Agent 2 完成", state="complete", expanded=False)
            else:
                status.update(label="Agent 2 失敗", state="error")
                st.stop()

        # --- Step 3: Flashcards ---
        with st.status("📇 Agent 3: 正在製作單字卡...", expanded=True) as status:
            flashcards_result = agent_flashcards(correction_result)
            if flashcards_result:
                # Count and display stats
                lines = flashcards_result.strip().split('\n')
                card_count = max(0, len(lines) - 1)  # Subtract header row
                st.write(f"✅ 單字卡製作完成！共 {card_count} 張")

                # Preview first 3 lines
                if len(lines) > 1:
                    st.write("**預覽前 3 張單字卡：**")
                    preview_lines = lines[:4]  # Header + 3 rows
                    st.code('\n'.join(preview_lines), language='csv')

                # Debug mode: show full output
                if debug_mode:
                    with st.expander("📋 查看完整單字卡 (CSV)"):
                        st.text(flashcards_result)

                status.update(label="Agent 3 完成", state="complete", expanded=False)
            else:
                status.update(label="Agent 3 失敗", state="error")
                st.stop()
        
        # --- Display Results ---
        st.divider()
        st.header("📊 批改結果")

        # Parse JSON and display in card format
        try:
            import json
            data = json.loads(correction_result)

            st.markdown(f"**批改完成，共 {len(data)} 題**")
            st.divider()

            # Display each correction as a card
            for idx, item in enumerate(data, 1):
                question_id = item.get('id', f'Q{idx}')
                user_text = item.get('user', '')
                correction_text = item.get('correction', '')
                feedback = item.get('feedback', '')

                # Card container
                with st.container():
                    # Header with question ID
                    st.markdown(f"### 題號 {question_id}")

                    # User vs Correction comparison
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**📝 原文**")
                        st.text_area(
                            label="原文",
                            value=user_text,
                            height=100,
                            key=f"user_{idx}",
                            disabled=True,
                            label_visibility="collapsed"
                        )

                    with col2:
                        st.markdown("**✅ 修正**")
                        st.text_area(
                            label="修正",
                            value=correction_text,
                            height=100,
                            key=f"correction_{idx}",
                            disabled=True,
                            label_visibility="collapsed"
                        )

                    # Feedback section - directly display without processing
                    st.markdown("**💡 說明**")
                    st.info(feedback)

                    st.divider()

        except Exception as e:
            st.error(f"Error parsing correction data: {e}")
            with st.expander("查看原始輸出"):
                st.text(correction_result)

        st.divider()
        st.header("📇 專屬單字卡")

        # Parse and display flashcard stats
        lines = flashcards_result.strip().split('\n')
        card_count = max(0, len(lines) - 1)
        st.markdown(f"**已生成 {card_count} 張單字卡**")

        # Preview in tabs
        tab1, tab2 = st.tabs(["📋 預覽", "📄 完整內容"])

        with tab1:
            st.markdown("**前 5 張單字卡預覽：**")
            if len(lines) > 1:
                # Parse CSV and display as cards
                import csv
                import io
                reader = csv.DictReader(io.StringIO(flashcards_result))
                for idx, row in enumerate(reader, 1):
                    if idx > 5:
                        break
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown(f"**正面**")
                            st.info(row.get('Front', ''))
                        with col2:
                            st.markdown(f"**背面**")
                            st.success(row.get('Back', ''))
                        if idx < 5 and idx < card_count:
                            st.markdown("---")

        with tab2:
            st.markdown("**完整 CSV 內容（可直接複製匯入 Anki/Quizlet）：**")
            st.text_area(
                label="CSV",
                value=flashcards_result,
                height=400,
                label_visibility="collapsed"
            )

        # Download Button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.download_button(
                label="⬇️ 下載 CSV",
                data=flashcards_result,
                file_name="flashcards.csv",
                mime="text/csv",
                use_container_width=True
            )
