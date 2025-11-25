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
        st.error(f"Supabase Connection Error: {e}")

st.set_page_config(
    page_title="Handwriting Correction",
    page_icon=None,
    layout="wide"
)

# --- Custom CSS & Theme Injection ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Tangerine:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    /* Global Variables */
    :root {
        --bg-color: #0a0a0a;
        --card-bg: #121212;
        --text-primary: #e0e0e0;
        --text-secondary: #a0a0a0;
        --accent-color: #ffffff;
        --border-color: #333333;
    }

    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Space Mono', monospace;
        background-color: var(--bg-color);
        color: var(--text-primary);
        font-weight: 400;
    }
    
    /* Headings */
    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary) !important;
    }
    
    h1 {
        font-size: 3.5rem !important;
        font-style: italic;
        margin-bottom: 0 !important;
    }
    
    h2 {
        font-size: 2.2rem !important;
        margin-top: 1.5rem !important;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-family: 'Space Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
    }

    /* Code & Monospace */
    code, .stCode, .stJson {
        font-family: 'Space Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    /* Accent Text (Tangerine) */
    .accent-text {
        font-family: 'Tangerine', cursive;
        font-size: 2.5rem;
        color: var(--text-secondary);
        margin-bottom: -1rem;
        display: block;
    }

    /* Minimalist Containers */
    .minimal-container {
        border-top: 1px solid var(--border-color);
        padding-top: 1.5rem;
        margin-top: 1rem;
    }

    /* Custom Button Styling - Minimalist */
    .stButton > button {
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 0.6rem 1.5rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: var(--text-primary);
        color: var(--bg-color);
        border-color: var(--text-primary);
    }
    .stButton > button:active {
        transform: translateY(1px);
    }

    /* File Uploader Styling */
    [data-testid="stFileUploader"] {
        border: 1px solid var(--border-color);
        border-radius: 0px;
        padding: 30px;
        background: transparent;
        transition: border-color 0.3s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--text-secondary);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: transparent;
        border: none;
        border-bottom: 1px solid var(--border-color);
        border-radius: 0;
        color: var(--text-primary);
        font-family: 'Space Mono', monospace;
    }
    .stTextInput > div > div > input:focus {
        border-bottom-color: var(--text-primary);
        box-shadow: none;
    }

    /* Card Styling for Corrections */
    .correction-card {
        background: transparent;
        border-left: 1px solid var(--border-color);
        padding: 0 0 0 20px;
        margin-bottom: 40px;
    }
    
    /* Status Container */
    .stStatus {
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0px !important;
        font-family: 'Space Mono', monospace !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid var(--border-color);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<div style="text-align: center; padding: 2rem 0 1rem 0;">', unsafe_allow_html=True)
st.markdown('<span class="accent-text">The Art of Translation</span>', unsafe_allow_html=True)
st.title("Handwriting Correction")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for API Key if not in env
if not api_key:
    api_key = st.sidebar.text_input("API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
else:
    genai.configure(api_key=api_key)

# Debug Mode Toggle
st.sidebar.markdown("### Settings")
debug_mode = st.sidebar.checkbox("Debug Mode", value=False)

# Sidebar: History Management
st.sidebar.markdown("### History")

# Check Supabase connection
if supabase:
    # Fetch history count from Supabase
    try:
        response = supabase.table("correction_history").select("id", count="exact").execute()
        history_count = response.count if hasattr(response, 'count') else 0
        st.sidebar.markdown(f"<p style='font-family:Space Mono; font-size:0.8rem'>Total Corrections: {history_count}</p>", unsafe_allow_html=True)

        # View history button
        if st.sidebar.button("View Archive", use_container_width=True):
            st.session_state.show_history = True

    except Exception as e:
        st.sidebar.error(f"History Error: {e}")
else:
    st.sidebar.info("Supabase not configured.")


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
        st.error(f"Agent 1 Error: {type(e).__name__}: {str(e)}")
        if debug_mode:
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
        st.error(f"Agent 2 Error: {type(e).__name__}: {str(e)}")
        if debug_mode:
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
        st.error(f"Agent 3 Error: {type(e).__name__}: {str(e)}")
        if debug_mode:
            st.code(traceback.format_exc(), language='python')
        return None

# --- UI Layout ---
st.markdown('<div class="minimal-container">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 01. User Handwriting")
    user_files = st.file_uploader("Upload images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True, label_visibility="collapsed")

with col2:
    st.markdown("### 02. Standard Answer")
    answer_file = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("INITIALIZE ANALYSIS", use_container_width=True):
    if not api_key:
        st.error("API Key Required")
    elif not user_files or not answer_file:
        st.error("Files Missing")
    else:
        # Process Images
        user_images = [Image.open(f) for f in user_files]
        answer_image = Image.open(answer_file)
        
        # --- Step 1: Transcription ---
        with st.status("Processing Transcription...", expanded=True) as status:
            transcription_result = agent_transcription(user_images, answer_image)
            if transcription_result:
                try:
                    import json
                    transcription_data = json.loads(transcription_result)
                    question_count = len(transcription_data)
                    st.write(f"Identified {question_count} items")
                except json.JSONDecodeError:
                    st.write("Transcription complete")
                
                status.update(label="Transcription Complete", state="complete", expanded=False)
            else:
                status.update(label="Transcription Failed", state="error")
                st.stop()

        # --- Step 2: Correction ---
        with st.status("Analyzing & Correcting...", expanded=True) as status:
            correction_result = agent_correction(transcription_result)
            if correction_result:
                try:
                    import json
                    correction_data = json.loads(correction_result)
                    st.write(f"Corrected {len(correction_data)} items")
                except json.JSONDecodeError:
                    st.write("Correction complete")
                
                status.update(label="Correction Complete", state="complete", expanded=False)
            else:
                status.update(label="Correction Failed", state="error")
                st.stop()

        # --- Step 3: Flashcards ---
        with st.status("Generating Study Materials...", expanded=True) as status:
            flashcards_result = agent_flashcards(correction_result)
            if flashcards_result:
                lines = flashcards_result.strip().split('\n')
                st.write(f"Generated {max(0, len(lines) - 1)} cards")
                status.update(label="Generation Complete", state="complete", expanded=False)
            else:
                status.update(label="Generation Failed", state="error")
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
            except Exception:
                pass # Silent fail for elegance

        # --- Display Results ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center;">Analysis Report</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Parse JSON and display in card format
        try:
            import json
            data = json.loads(correction_result)

            for idx, item in enumerate(data, 1):
                question_id = item.get('id', f'{idx:02d}')
                user_text = item.get('user', '')
                correction_text = item.get('correction', '')
                feedback = item.get('feedback', '')

                # Custom Card Container
                st.markdown(f"""
                <div class="correction-card">
                    <h3 style="color: #666; margin-bottom: 1rem;">NO. {question_id}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                with st.container():
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Original**")
                        st.markdown(f"<p style='font-family: Inter; color: #ccc; line-height: 1.6;'>{user_text}</p>", unsafe_allow_html=True)

                    with col2:
                        st.markdown("**Correction**")
                        st.markdown(f"<p style='font-family: Inter; color: #fff; line-height: 1.6;'>{correction_text}</p>", unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("**Notes**")
                    if isinstance(feedback, list):
                        for point in feedback:
                            st.markdown(f"<p style='font-family: Cormorant Garamond; font-style: italic; color: #aaa; margin-bottom: 0.5rem;'>— {point}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='font-family: Cormorant Garamond; font-style: italic; color: #aaa;'>— {feedback}</p>", unsafe_allow_html=True)

                    st.markdown("<hr style='border-top: 1px solid #333; margin: 2rem 0;'>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Parsing Error: {e}")

        st.markdown('<h2 style="text-align: center;">Study Cards</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Parse and display flashcard stats
        lines = flashcards_result.strip().split('\n')
        
        tab1, tab2 = st.tabs(["PREVIEW", "CSV DATA"])

        with tab1:
            if len(lines) > 1:
                import csv
                import io
                reader = csv.DictReader(io.StringIO(flashcards_result))
                for idx, row in enumerate(reader, 1):
                    if idx > 6:
                        break
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"<span style='font-family:Space Mono; font-size:0.8rem; color:#666'>FRONT</span>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size:1.1rem'>{row.get('Front', '')}</p>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<span style='font-family:Space Mono; font-size:0.8rem; color:#666'>BACK</span>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size:1.1rem; color:#aaa'>{row.get('Back', '')}</p>", unsafe_allow_html=True)
                    st.markdown("<hr style='border-top: 1px solid #222;'>", unsafe_allow_html=True)

        with tab2:
            st.text_area(
                label="CSV",
                value=flashcards_result,
                height=300,
                label_visibility="collapsed"
            )

        st.download_button(
            label="DOWNLOAD CSV",
            data=flashcards_result,
            file_name="flashcards.csv",
            mime="text/csv",
            use_container_width=True
        )
