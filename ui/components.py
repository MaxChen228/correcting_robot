"""
UI Components
使用者介面組件與互動邏輯
"""
import streamlit as st
import json
import csv
import io
from typing import Optional, List
from PIL import Image

from config.settings import Config


def render_file_upload_section() -> tuple[Optional[List[Image.Image]], Optional[Image.Image]]:
    """
    Render file upload section for user handwriting and standard answer

    Returns:
        Tuple of (user_images, answer_image) or (None, None) if not uploaded
    """
    st.markdown('<div class="minimal-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    user_files = None
    answer_file = None

    with col1:
        st.markdown("### 01. User Handwriting")
        user_files = st.file_uploader(
            "Upload images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("### 02. Standard Answer")
        answer_file = st.file_uploader(
            "Upload image",
            type=['png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Convert to PIL Images if files are uploaded
    if user_files and answer_file:
        user_images = [Image.open(f) for f in user_files]
        answer_image = Image.open(answer_file)
        return user_images, answer_image

    return None, None


def render_sidebar_settings() -> tuple[Optional[str], bool]:
    """
    Render sidebar settings (API key input, debug mode)

    Returns:
        Tuple of (api_key, debug_mode)
    """
    # API Key Input
    api_key = Config.GOOGLE_API_KEY
    if not api_key:
        api_key = st.sidebar.text_input("API Key", type="password")

    # Debug Mode Toggle
    st.sidebar.markdown("### Settings")
    debug_mode = st.sidebar.checkbox("Debug Mode", value=False)

    return api_key, debug_mode


def render_correction_results(correction_json: str):
    """
    Render correction results in card format

    Args:
        correction_json: JSON string of correction results
    """
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">Analysis Report</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        data = json.loads(correction_json)

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
                    st.markdown(
                        f"<p style='font-family: Inter; color: #ccc; line-height: 1.6;'>{user_text}</p>",
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown("**Correction**")
                    st.markdown(
                        f"<p style='font-family: Inter; color: #fff; line-height: 1.6;'>{correction_text}</p>",
                        unsafe_allow_html=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Notes**")

                # Handle feedback as list or string
                if isinstance(feedback, list):
                    for point in feedback:
                        st.markdown(
                            f"<p style='font-family: Cormorant Garamond; font-style: italic; color: #aaa; margin-bottom: 0.5rem;'>— {point}</p>",
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        f"<p style='font-family: Cormorant Garamond; font-style: italic; color: #aaa;'>— {feedback}</p>",
                        unsafe_allow_html=True
                    )

                st.markdown("<hr style='border-top: 1px solid #333; margin: 2rem 0;'>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Parsing Error: {e}")


def render_flashcards_section(flashcards_csv: str):
    """
    Render flashcards preview and download section

    Args:
        flashcards_csv: CSV string of flashcards
    """
    st.markdown('<h2 style="text-align: center;">Study Cards</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    lines = flashcards_csv.strip().split('\n')

    tab1, tab2 = st.tabs(["PREVIEW", "CSV DATA"])

    with tab1:
        if len(lines) > 1:
            reader = csv.DictReader(io.StringIO(flashcards_csv))
            for idx, row in enumerate(reader, 1):
                if idx > 6:  # Show only first 6 cards
                    break

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(
                        f"<span style='font-family:Space Mono; font-size:0.8rem; color:#666'>FRONT</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p style='font-size:1.1rem'>{row.get('Front', '')}</p>",
                        unsafe_allow_html=True
                    )
                with col2:
                    st.markdown(
                        f"<span style='font-family:Space Mono; font-size:0.8rem; color:#666'>BACK</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p style='font-size:1.1rem; color:#aaa'>{row.get('Back', '')}</p>",
                        unsafe_allow_html=True
                    )
                st.markdown("<hr style='border-top: 1px solid #222;'>", unsafe_allow_html=True)

    with tab2:
        st.text_area(
            label="CSV",
            value=flashcards_csv,
            height=300,
            label_visibility="collapsed"
        )

    # Download button
    st.download_button(
        label="DOWNLOAD CSV",
        data=flashcards_csv,
        file_name="flashcards.csv",
        mime="text/csv",
        use_container_width=True
    )
