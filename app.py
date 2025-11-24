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

# --- Agent 1: Transcription ---
def agent_transcription(user_images, answer_image):
    """
    Agent 1: Digitizes handwriting and aligns it with the standard answer.
    Returns: JSON string.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
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
        st.error(f"Agent 1 Error: {e}")
        return None

# --- Agent 2: Correction ---
def agent_correction(transcription_json):
    """
    Agent 2: Analyzes the text and provides corrections.
    Returns: JSON string.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    你是一位嚴格但循循善誘的英文作文教練。
    
    輸入資料 (JSON):
    {transcription_json}
    
    任務：
    針對每一題，比對 User 的寫作與 Standard 標準答案，進行深度批改。
    
    分析維度：
    1. **致命傷**：文法錯誤（如主詞動詞不一致、時態錯誤、單複數錯誤）。
    2. **選詞**：User 的用詞是否精準？有無更道地的表達？
    3. **句型**：句構是否符合英文邏輯？
    
    輸出格式要求：
    請直接輸出一個純 JSON Array，不要有任何 Markdown 標記。
    格式如下：
    [
        {{
            "id": "1.1",
            "user": "User's original text",
            "correction": "The best corrected version",
            "feedback": "【錯誤類型】詳細解釋... (請用繁體中文，可使用 markdown 語法)"
        }},
        ...
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
        st.error(f"Agent 2 Error: {e}")
        return None

# --- Agent 3: Flashcards ---
def agent_flashcards(correction_json):
    """
    Agent 3: Generates flashcards from the corrections.
    Returns: CSV string.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    你是一個單字卡製作助理。
    
    輸入資料 (批改結果 JSON):
    {correction_json}
    
    任務：
    從上述的批改內容與標準答案中，提煉出使用者需要學習的「單字」、「片語」或「句型」。
    不要只列出單字，要包含用法。
    
    輸出格式要求：
    請直接輸出 CSV 格式的文字，包含 Header。
    欄位：Front, Back
    
    Front (正面): 關鍵詞或中文提示 (例如: "隨著 (連接詞用法)")
    Back (背面): 英文用法、結構與例句 (例如: "As + S + V (Ex: As time goes by...)")
    
    請確保內容豐富且實用，適合匯入 Anki 或 Quizlet。
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Agent 3 Error: {e}")
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
                st.write("✅ 辨識完成！")
                # st.json(transcription_result) # Debug
                status.update(label="Agent 1 完成", state="complete", expanded=False)
            else:
                status.update(label="Agent 1 失敗", state="error")
                st.stop()

        # --- Step 2: Correction ---
        with st.status("👩‍🏫 Agent 2: 正在進行批改與點評...", expanded=True) as status:
            correction_result = agent_correction(transcription_result)
            if correction_result:
                st.write("✅ 批改完成！")
                status.update(label="Agent 2 完成", state="complete", expanded=False)
            else:
                status.update(label="Agent 2 失敗", state="error")
                st.stop()

        # --- Step 3: Flashcards ---
        with st.status("📇 Agent 3: 正在製作單字卡...", expanded=True) as status:
            flashcards_result = agent_flashcards(correction_result)
            if flashcards_result:
                st.write("✅ 單字卡製作完成！")
                status.update(label="Agent 3 完成", state="complete", expanded=False)
            else:
                status.update(label="Agent 3 失敗", state="error")
                st.stop()
        
        # --- Display Results ---
        st.divider()
        st.header("📊 分析結果 (Analysis Results)")
        
        # Parse JSON for Table Display
        try:
            import json
            data = json.loads(correction_result)
            df = pd.DataFrame(data)
            
            st.subheader("1. 詳細批改表")
            st.dataframe(df, use_container_width=True)
            
            with st.expander("查看詳細點評 (Markdown View)"):
                for item in data:
                    st.markdown(f"### 題號 {item['id']}")
                    st.markdown(f"**User**: {item['user']}")
                    st.markdown(f"**Correction**: {item['correction']}")
                    st.info(item['feedback'])
                    st.divider()
                    
        except Exception as e:
            st.error(f"Error parsing correction data: {e}")
            st.text(correction_result)

        st.divider()
        st.subheader("2. 專屬單字卡 (Flashcards)")
        st.text_area("CSV 內容 (可直接複製)", flashcards_result, height=300)
        
        # Download Button
        st.download_button(
            label="下載單字卡 CSV",
            data=flashcards_result,
            file_name="flashcards.csv",
            mime="text/csv"
        )
