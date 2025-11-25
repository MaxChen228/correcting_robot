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


def render_correction_results(correction_data, show_title: bool = True):
    """
    Render correction results in card format

    Args:
        correction_data: JSON string or list/dict of correction results
        show_title: Whether to show the title (default: True)
    """
    if show_title:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center;">Analysis Report</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    try:
        # Handle both JSON string and direct data
        if isinstance(correction_data, str):
            data = json.loads(correction_data)
        else:
            data = correction_data

        for idx, item in enumerate(data, 1):
            question_id = item.get('id', f'{idx:02d}')
            user_text = item.get('user', '')
            correction_text = item.get('correction', '')
            feedback = item.get('feedback', '')

            # Wrapper with inline card styling
            st.markdown("""
            <div style="
                background: rgba(18, 18, 18, 0.6);
                border: 1px solid #333;
                border-radius: 8px;
                padding: 24px;
                margin-bottom: 32px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3), 0 1px 3px rgba(0, 0, 0, 0.2);
            ">
            """, unsafe_allow_html=True)

            # Card header
            st.markdown(f"""
                <h3 style="color: #888; margin-bottom: 1.5rem; font-family: 'Space Mono', monospace; font-size: 0.9rem; letter-spacing: 0.1em; text-transform: uppercase;">
                    NO. {question_id}
                </h3>
            """, unsafe_allow_html=True)

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

            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Parsing Error: {e}")


def render_flashcards_section(flashcards_csv: str, show_title: bool = True, download_filename: str = "flashcards.csv"):
    """
    Render flashcards preview and download section

    Args:
        flashcards_csv: CSV string of flashcards
        show_title: Whether to show the title (default: True)
        download_filename: Filename for download button (default: "flashcards.csv")
    """
    if show_title:
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
        file_name=download_filename,
        mime="text/csv",
        use_container_width=True
    )


def render_history_page(history_records: list):
    """
    Render history archive page

    Args:
        history_records: List of history records from database
    """
    st.markdown('<h2 style="text-align: center;">Correction Archive</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not history_records:
        st.info("No history records found.")
        return

    # Back button
    if st.button("← BACK TO MAIN", use_container_width=True):
        st.session_state.show_history = False
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Display each history record
    for idx, record in enumerate(history_records, 1):
        timestamp = record.get('timestamp', 'Unknown')
        corrections = record.get('corrections', [])
        flashcards = record.get('flashcards', '')
        record_id = record.get('id', idx)

        # Format timestamp
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_time = timestamp

        # Expandable section for each record
        with st.expander(f"Record #{idx} - {formatted_time}", expanded=(idx == 1)):
            # Restore button
            if st.button("Restore this record", key=f"restore_{record_id}"):
                st.session_state.restored_corrections = corrections
                st.session_state.restored_flashcards = flashcards
                st.session_state.show_history = False
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # Use shared rendering functions
            if corrections:
                render_correction_results(corrections, show_title=False)

            if flashcards:
                render_flashcards_section(
                    flashcards,
                    show_title=False,
                    download_filename=f"flashcards_{formatted_time.replace(' ', '_').replace(':', '-')}.csv"
                )
