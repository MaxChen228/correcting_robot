"""
UI Components
使用者介面組件與互動邏輯
"""
import streamlit as st
import streamlit.components.v1 as components
import json
import csv
import io
import textwrap
from typing import Optional, List
from uuid import uuid4
from PIL import Image

from config.settings import Config



def clean_html(html: str) -> str:
    """Clean HTML string by removing all indentation line by line."""
    return "\n".join(line.strip() for line in html.split("\n") if line.strip())

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
    Supports images (PNG, JPG, JPEG) and PDF files

    Returns:
        Tuple of (user_images, answer_image) or (None, None) if not uploaded
    """
    from utils.file_converter import convert_files_to_images, is_pdf_supported

    st.markdown('<div class="minimal-container">', unsafe_allow_html=True)

    # Check PDF support and determine supported types
    supported_types = ['png', 'jpg', 'jpeg']
    if is_pdf_supported():
        supported_types.append('pdf')
    else:
        st.info("PDF support not enabled. Install: pip install pdf2image && brew install poppler")

    col1, col2 = st.columns(2)

    user_files = None
    answer_file = None

    with col1:
        st.markdown("### 01. User Handwriting")
        user_files = st.file_uploader(
            "Upload images or PDF",
            type=supported_types,
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("### 02. Standard Answer")
        answer_file = st.file_uploader(
            "Upload image or PDF",
            type=supported_types,
            label_visibility="collapsed"
        )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Convert files to PIL Images
    if user_files and answer_file:
        try:
            user_images = convert_files_to_images(user_files)
            answer_images = convert_files_to_images([answer_file])
            answer_image = answer_images[0]

            # Show conversion info if PDF files were processed
            pdf_count = sum(1 for f in user_files if f.type == 'application/pdf')
            if pdf_count > 0 or answer_file.type == 'application/pdf':
                st.info(
                    f"✓ PDF converted: {len(user_images)} images "
                    f"(Answer: using page 1)"
                )

            return user_images, answer_image

        except Exception as e:
            st.error(f"File conversion failed: {str(e)}")
            return None, None

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
            elif not transcription_data:
                # Old records without transcription data
                standard_text = '(資料不可用)'

            # Card wrapper - Premium Sharp Look
            # Build the complete HTML string first to avoid Streamlit/Browser auto-closing tags between st.markdown calls
            html_content = f"""
            <div class="correction-card-sharp" style="
                background: #0f0f0f;
                border: 1px solid #2a2a2a;
                border-left: 3px solid #e0e0e0;
                padding: 0;
                margin-bottom: 40px;
                position: relative;
            ">
                <!-- Header Section -->
                <div style="
                    padding: 20px 30px;
                    border-bottom: 1px solid #1f1f1f;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: rgba(255,255,255,0.01);
                ">
                    <h3 style="
                        color: #666;
                        font-family: 'Space Mono', monospace;
                        font-size: 0.9rem;
                        letter-spacing: 0.2em;
                        margin: 0;
                    ">ANALYSIS {question_id}</h3>
                    <div style="
                        font-family: 'Space Mono', monospace;
                        font-size: 0.7rem;
                        color: #4a8;
                        border: 1px solid #2a4a3a;
                        background: rgba(46, 204, 113, 0.05);
                        padding: 4px 8px;
                    ">AUTO-CORRECTED</div>
                </div>

                <!-- Content Section -->
                <div style="padding: 30px;">
                    <!-- Comparison Grid -->
                    <div style="
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 40px;
                        margin-bottom: 30px;
                    ">
                        <!-- User Input -->
                        <div>
                            <div style="
                                font-family: 'Space Mono', monospace;
                                font-size: 0.7rem;
                                color: #555;
                                letter-spacing: 0.1em;
                                margin-bottom: 12px;
                                text-transform: uppercase;
                            ">Original Input</div>
                            <div style="
                                font-family: 'Inter', sans-serif;
                                font-size: 1rem;
                                color: #888;
                                line-height: 1.6;
                                padding-left: 15px;
                                border-left: 1px solid #333;
                            ">{user_text}</div>
                        </div>

                        <!-- Standard Answer -->
                        <div>
                            <div style="
                                font-family: 'Space Mono', monospace;
                                font-size: 0.7rem;
                                color: #555;
                                letter-spacing: 0.1em;
                                margin-bottom: 12px;
                                text-transform: uppercase;
                            ">Standard Reference</div>
                            <div style="
                                font-family: 'Inter', sans-serif;
                                font-size: 1rem;
                                color: #888;
                                line-height: 1.6;
                                padding-left: 15px;
                                border-left: 1px solid #333;
                            ">{standard_text}</div>
                        </div>
                    </div>

                    <!-- Correction Hero Section -->
                    <div style="
                        background: rgba(255,255,255,0.03);
                        border: 1px solid #222;
                        padding: 25px;
                        margin-bottom: 30px;
                        position: relative;
                    ">
                        <div style="
                            position: absolute;
                            top: -10px;
                            left: 20px;
                            background: #0f0f0f;
                            padding: 0 10px;
                            font-family: 'Space Mono', monospace;
                            font-size: 0.7rem;
                            color: #e0e0e0;
                            letter-spacing: 0.1em;
                        ">OPTIMIZED CORRECTION</div>
                        <div style="
                            font-family: 'Cormorant Garamond', serif;
                            font-size: 1.6rem;
                            color: #fff;
                            line-height: 1.4;
                            font-style: italic;
                        ">{correction_text}</div>
                    </div>

                    <!-- Feedback/Notes -->
                    <div>
                        <div style="
                            font-family: 'Space Mono', monospace;
                            font-size: 0.7rem;
                            color: #555;
                            letter-spacing: 0.1em;
                            margin-bottom: 15px;
                            text-transform: uppercase;
                        ">Key Insights</div>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
            """

            # Handle feedback items
            feedback_items = feedback if isinstance(feedback, list) else [feedback]
            for point in feedback_items:
                html_content += f"""
                    <div style="
                        display: flex;
                        align-items: flex-start;
                        gap: 12px;
                    ">
                        <span style="
                            color: #4a8;
                            font-size: 1.2rem;
                            line-height: 1;
                            margin-top: -2px;
                        ">›</span>
                        <span style="
                            font-family: 'Inter', sans-serif;
                            font-size: 0.95rem;
                            color: #bbb;
                            line-height: 1.5;
                        ">{point}</span>
                    </div>
                """

            html_content += """
                        </div>
                    </div>
                </div>
            </div>
            """

            st.markdown(clean_html(html_content), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Parsing Error: {e}")


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
        transcriptions = record.get('transcriptions', [])
        corrections = record.get('corrections', [])
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
                st.session_state.restored_transcriptions = transcriptions
                st.session_state.restored_corrections = corrections
                st.session_state.show_history = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Use shared rendering functions
            if corrections:
                render_correction_results(transcriptions, corrections, show_title=False)
