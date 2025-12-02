"""
UI Components
使用者介面組件與互動邏輯
"""
import streamlit as st
import streamlit.components.v1 as components
import json
import csv
import io
from typing import Optional, List
from uuid import uuid4
from PIL import Image

from config.settings import Config


def render_copy_json_button(json_text: str, label: str = "COPY 批改 JSON") -> None:
    """Render a clipboard button for copying formatted JSON."""
    if not json_text:
        return

    button_id = f"copy-json-btn-{uuid4().hex}"
    safe_json_payload = json.dumps(json_text).replace("</", "<\\/")
    components.html(
        f"""
        <style>
            body {{
                margin: 0;
                background: transparent;
                font-family: 'Space Mono', monospace;
            }}
            #{button_id} {{
                background: rgba(255,255,255,0.02);
                border: 1px solid #333;
                color: #f5f5f5;
                font-size: 0.72rem;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                padding: 0.65rem 1.75rem;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            #{button_id}:hover {{
                border-color: #666;
                color: #ffffff;
            }}
            #{button_id}.copied {{
                border-color: #2ecc71;
                color: #2ecc71;
            }}
            #{button_id}.error {{
                border-color: #ff6b6b;
                color: #ff6b6b;
            }}
        </style>
        <div style="display:flex; justify-content:flex-end; margin:-12px 0 20px 0;">
            <button id="{button_id}">{label}</button>
        </div>
        <script>
            (function() {{
                const copyBtn = document.getElementById('{button_id}');
                const payload = {safe_json_payload};
                if (!copyBtn || !payload) return;
                const defaultText = copyBtn.textContent;

                copyBtn.addEventListener('click', async () => {{
                    try {{
                        await navigator.clipboard.writeText(payload);
                        copyBtn.textContent = 'COPIED!';
                        copyBtn.classList.remove('error');
                        copyBtn.classList.add('copied');
                    }} catch (err) {{
                        copyBtn.textContent = 'COPY FAILED';
                        copyBtn.classList.remove('copied');
                        copyBtn.classList.add('error');
                    }} finally {{
                        setTimeout(() => {{
                            copyBtn.textContent = defaultText;
                            copyBtn.classList.remove('copied');
                            copyBtn.classList.remove('error');
                        }}, 1800);
                    }}
                }});
            }})();
        </script>
        """,
        height=70,
    )


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


def render_correction_results(transcription_data=None, correction_data=None, show_title: bool = True):
    """
    Render correction results in 3-column stacked layout

    Args:
        transcription_data: JSON string or list/dict with {id, user, standard} from Agent 1
        correction_data: JSON string or list/dict with {id, user, correction, feedback} from Agent 2
        show_title: Whether to show the title (default: True)

    Note: For backward compatibility, if only one argument is passed, it's treated as correction_data
    """
    # Backward compatibility: if transcription_data looks like correction data, swap them
    if transcription_data is not None and correction_data is None:
        correction_data = transcription_data
        transcription_data = None
    if show_title:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center;">Analysis Report</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    try:
        # Parse transcription data (Agent 1: {id, user, standard})
        transcription_dict = {}
        if transcription_data:
            if isinstance(transcription_data, str):
                trans_list = json.loads(transcription_data)
            else:
                trans_list = transcription_data
            # Build lookup dict by id
            transcription_dict = {item.get('id'): item for item in trans_list}

        # Parse correction data (Agent 2: {id, user, correction, feedback})
        formatted_json = ""
        if isinstance(correction_data, str):
            data = json.loads(correction_data)
        else:
            data = correction_data

        if data is None:
            data = []

        if data:
            formatted_json = json.dumps(data, ensure_ascii=False, indent=2)
            render_copy_json_button(formatted_json)

        for idx, item in enumerate(data, 1):
            question_id = item.get('id', f'{idx:02d}')
            user_text = item.get('user', '')
            correction_text = item.get('correction', '')
            feedback = item.get('feedback', '')

            # Get standard from transcription data
            standard_text = ''
            if question_id in transcription_dict:
                standard_text = transcription_dict[question_id].get('standard', '')

            # Card wrapper - Sharp corners style
            st.markdown("""
            <div class="correction-card-sharp" style="
                background: rgba(18, 18, 18, 0.6);
                border: 1px solid #333;
                border-radius: 0;
                padding: 24px;
                margin-bottom: 32px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
            ">
            """, unsafe_allow_html=True)

            # Card header
            st.markdown(f"""
                <div class="card-header" style="
                    padding-bottom: 1rem;
                    margin-bottom: 1.5rem;
                    border-bottom: 1px solid #333;
                ">
                    <h3 style="
                        color: #888;
                        font-family: 'Space Mono', monospace;
                        font-size: 0.85rem;
                        letter-spacing: 0.15em;
                        text-transform: uppercase;
                        margin: 0;
                    ">NO. {question_id}</h3>
                </div>
            """, unsafe_allow_html=True)

            # Upper section: User | Standard (small text, secondary color)
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<p style="font-family: Space Mono; font-size: 0.75rem; color: #666; margin-bottom: 0.5rem;">USER WRITING</p>', unsafe_allow_html=True)
                st.markdown(
                    f"<p class='text-small text-secondary' style='font-family: Inter; font-size: 0.85rem; color: #999; line-height: 1.5;'>{user_text}</p>",
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown('<p style="font-family: Space Mono; font-size: 0.75rem; color: #666; margin-bottom: 0.5rem;">STANDARD ANSWER</p>', unsafe_allow_html=True)
                st.markdown(
                    f"<p class='text-small text-secondary' style='font-family: Inter; font-size: 0.85rem; color: #999; line-height: 1.5;'>{standard_text}</p>",
                    unsafe_allow_html=True
                )

            # Divider
            st.markdown("""
                <div class="divider" style="
                    height: 1px;
                    background: linear-gradient(90deg, transparent 0%, #444 10%, #444 90%, transparent 100%);
                    margin: 1.5rem 0;
                "></div>
            """, unsafe_allow_html=True)

            # Lower section: Correction (large text, primary color, emphasis)
            st.markdown('<p style="font-family: Space Mono; font-size: 0.75rem; color: #666; margin-bottom: 0.5rem;">CORRECTION</p>', unsafe_allow_html=True)
            st.markdown(
                f"<p class='text-large text-primary' style='font-family: Inter; font-size: 1.1rem; color: #e0e0e0; line-height: 1.7; font-weight: 500;'>{correction_text}</p>",
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p style="font-family: Space Mono; font-size: 0.75rem; color: #666; margin-bottom: 0.5rem;">NOTES</p>', unsafe_allow_html=True)

            # Handle feedback as list or string
            if isinstance(feedback, list):
                for point in feedback:
                    st.markdown(
                        f"<p class='note-item' style='font-family: Cormorant Garamond; font-style: italic; color: #aaa; margin-bottom: 0.5rem; padding-left: 0.5rem; border-left: 2px solid #333;'>— {point}</p>",
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    f"<p class='note-item' style='font-family: Cormorant Garamond; font-style: italic; color: #aaa; padding-left: 0.5rem; border-left: 2px solid #333;'>— {feedback}</p>",
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

                # Flashcard item wrapper - Sharp corners
                st.markdown("""
                <div class="flashcard-item" style="
                    padding: 1.5rem;
                    border: 1px solid #222;
                    border-radius: 0;
                    margin-bottom: 1.5rem;
                    background: rgba(18, 18, 18, 0.4);
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    transition: all 0.3s ease;
                ">
                """, unsafe_allow_html=True)

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

                st.markdown("</div>", unsafe_allow_html=True)

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
            # Restore button with wrapper
            st.markdown('<div class="restore-button-wrapper">', unsafe_allow_html=True)
            if st.button("Restore this record", key=f"restore_{record_id}"):
                st.session_state.restored_corrections = corrections
                st.session_state.restored_flashcards = flashcards
                st.session_state.show_history = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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
