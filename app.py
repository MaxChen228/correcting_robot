import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io
import json
from datetime import datetime
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Supabase
supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = None
if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"❌ Supabase 連接失敗: {e}")

st.set_page_config(
    page_title="Handwriting Correction AI",
    page_icon="📝",
    layout="wide"
)

# --- Custom CSS & Theme Injection ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@400;600;700&display=swap');

    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }

    /* Gradient Background for Main App */
    .stApp {
        background: radial-gradient(circle at top left, #1a1c24, #0e1117);
    }

    /* Glassmorphism Containers */
    .glass-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }

    /* Custom Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #6C63FF 0%, #4834d4 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* File Uploader Styling */
    [data-testid="stFileUploader"] {
        border: 1px dashed rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.02);
        transition: border-color 0.3s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #6C63FF;
    }

    /* Card Styling for Corrections */
    .correction-card {
        background: rgba(30, 32, 40, 0.6);
        border-left: 4px solid #6C63FF;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    /* Status Container */
    .stStatus {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<div class="glass-container" style="text-align: center;">', unsafe_allow_html=True)
st.title("📝 Handwriting Translation Correction System")
st.markdown("""
<p style="font-size: 1.1rem; color: #a0a0a0;">
    Upload your handwritten translation exercises and the standard answer key.<br>
    The AI will <span style="color: #6C63FF; font-weight: 600;">transcribe</span>, 
    <span style="color: #6C63FF; font-weight: 600;">correct</span>, and 
    <span style="color: #6C63FF; font-weight: 600;">generate flashcards</span> for you.
</p>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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

# Sidebar: History Management
st.sidebar.divider()
st.sidebar.subheader("📚 批改歷史")

# Check Supabase connection
if supabase:
    st.sidebar.success("✅ 已連接雲端數據庫")

    # Fetch history count from Supabase
    try:
        response = supabase.table("correction_history").select("id", count="exact").execute()
        history_count = response.count if hasattr(response, 'count') else 0
        st.sidebar.metric("已記錄批改次數", history_count)

        # View history button
        if st.sidebar.button("📖 查看歷史記錄", use_container_width=True):
            st.session_state.show_history = True

    except Exception as e:
        st.sidebar.error(f"❌ 讀取歷史失敗: {e}")
else:
    st.sidebar.warning("⚠️ 未配置 Supabase，歷史記錄功能不可用")
    st.sidebar.info("請在 .env 或 Streamlit secrets 中設定 SUPABASE_URL 和 SUPABASE_KEY")


# --- Agent 1: Transcription ---
def agent_transcription(user_images, answer_image):
    """
    Agent 1: Digitizes handwriting and aligns it with the standard answer.
    Returns: JSON string.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
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
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
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
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
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
st.markdown('<div class="glass-container">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload User Handwriting")
    user_files = st.file_uploader("Upload handwriting images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

with col2:
    st.subheader("2. Upload Standard Answer")
    answer_file = st.file_uploader("Upload answer key image", type=['png', 'jpg', 'jpeg'])
st.markdown('</div>', unsafe_allow_html=True)

if st.button("Start Analysis 🚀", use_container_width=True):
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

        # --- Save to Supabase ---
        if supabase:
            try:
                correction_data = json.loads(correction_result)
                history_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "corrections": correction_data,
                    "flashcards": flashcards_result
                }
                supabase.table("correction_history").insert(history_entry).execute()
                st.success("✅ 已自動保存到雲端數據庫")
            except Exception as e:
                st.warning(f"⚠️ 無法保存到數據庫: {e}")

        # --- Display Results ---
        st.divider()
        st.markdown('<h2 style="text-align: center;">📊 批改結果</h2>', unsafe_allow_html=True)

        # Parse JSON and display in card format
        try:
            import json
            data = json.loads(correction_result)

            st.markdown(f"**批改完成，共 {len(data)} 題**")
            
            # Display each correction as a card
            for idx, item in enumerate(data, 1):
                question_id = item.get('id', f'Q{idx}')
                user_text = item.get('user', '')
                correction_text = item.get('correction', '')
                feedback = item.get('feedback', '')

                # Custom Card Container
                st.markdown(f"""
                <div class="correction-card">
                    <h4 style="margin-top:0; color:#6C63FF;">題號 {question_id}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                with st.container():
                    # User vs Correction comparison
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**📝 原文**")
                        st.info(user_text) # Use st.info for better visibility in dark mode

                    with col2:
                        st.markdown("**✅ 修正**")
                        st.success(correction_text) # Use st.success for better visibility

                    # Feedback section
                    st.markdown("**💡 說明**")
                    if isinstance(feedback, list):
                        for point in feedback:
                            st.warning(f"• {point}")
                    else:
                        st.warning(feedback)

                    st.markdown("---")

        except Exception as e:
            st.error(f"Error parsing correction data: {e}")
            with st.expander("查看原始輸出"):
                st.text(correction_result)

        st.divider()
        st.markdown('<h2 style="text-align: center;">📇 專屬單字卡</h2>', unsafe_allow_html=True)

        # Parse and display flashcard stats
        lines = flashcards_result.strip().split('\n')
        card_count = max(0, len(lines) - 1)
        
        st.markdown(f'<div class="glass-container">', unsafe_allow_html=True)
        st.markdown(f"**已生成 {card_count} 張單字卡**")

        # Preview in tabs
        tab1, tab2 = st.tabs(["📋 預覽", "📄 完整內容"])

        with tab1:
            st.markdown("**前 5 張單字卡預覽：**")
            if len(lines) > 1:
                import csv
                import io
                reader = csv.DictReader(io.StringIO(flashcards_result))
                for idx, row in enumerate(reader, 1):
                    if idx > 5:
                        break
                    
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
        st.markdown('</div>', unsafe_allow_html=True)

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
