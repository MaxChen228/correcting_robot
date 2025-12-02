"""
Handwriting Translation Correction System
AI 驅動的手寫翻譯批改系統
"""
import streamlit as st
import json

# Import modules
from config.settings import Config, configure_gemini_api
from services.database import DatabaseService
from ui.theme import apply_custom_theme, render_header
from ui.components import (
    render_file_upload_section,
    render_sidebar_settings,
    render_correction_results,
    render_flashcards_section,
    render_history_page
)
from agents import transcription, correction, flashcards


def main():
    """Main application entry point"""

    # Configure page
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout=Config.LAYOUT
    )

    # Apply custom theme
    apply_custom_theme()
    render_header()

    # Initialize database service
    db = DatabaseService()

    # Sidebar settings
    api_key, debug_mode = render_sidebar_settings()
    if api_key:
        configure_gemini_api(api_key)

    # Sidebar history info
    db.render_sidebar_info()

    # Check if user wants to view history
    if st.session_state.get('show_history', False):
        # Show history page
        history_records = db.get_all_history()
        render_history_page(history_records)
        return

    # Check if there's a restored record to display
    if st.session_state.get('restored_corrections') and st.session_state.get('restored_flashcards'):
        # Show info and clear button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("Displaying restored record from history")
        with col2:
            if st.button("Clear", use_container_width=True):
                st.session_state.restored_transcriptions = None
                st.session_state.restored_corrections = None
                st.session_state.restored_flashcards = None
                st.rerun()

        # Display restored results
        render_correction_results(
            st.session_state.get('restored_transcriptions'),
            st.session_state.restored_corrections
        )
        render_flashcards_section(st.session_state.restored_flashcards)
        return

    # File upload section
    user_images, answer_image = render_file_upload_section()

    # Analysis button
    if st.button("INITIALIZE ANALYSIS", use_container_width=True):
        if not api_key:
            st.error("API Key Required")
            return

        if not user_images or not answer_image:
            st.error("Files Missing")
            return

        # Run three-stage AI pipeline
        run_analysis_pipeline(user_images, answer_image, debug_mode, db)


def run_analysis_pipeline(user_images, answer_image, debug_mode, db):
    """
    Execute three-stage AI analysis pipeline

    Args:
        user_images: List of user handwriting images
        answer_image: Standard answer image
        debug_mode: Show detailed debugging info
        db: Database service instance
    """

    # --- Stage 1: Transcription ---
    with st.status("Processing Transcription...", expanded=True) as status:
        transcription_result = transcription.process(user_images, answer_image, debug_mode)

        if transcription_result:
            try:
                transcription_data = json.loads(transcription_result)
                st.write(f"Identified {len(transcription_data)} items")
            except json.JSONDecodeError:
                st.write("Transcription complete")

            status.update(label="Transcription Complete", state="complete", expanded=False)
        else:
            status.update(label="Transcription Failed", state="error")
            return

    # --- Stage 2: Correction ---
    with st.status("Analyzing & Correcting...", expanded=True) as status:
        correction_result = correction.process(transcription_result, debug_mode)

        if correction_result:
            try:
                correction_data = json.loads(correction_result)
                st.write(f"Corrected {len(correction_data)} items")
            except json.JSONDecodeError:
                st.write("Correction complete")

            status.update(label="Correction Complete", state="complete", expanded=False)
        else:
            status.update(label="Correction Failed", state="error")
            return

    # --- Stage 3: Flashcards ---
    with st.status("Generating Study Materials...", expanded=True) as status:
        flashcards_result = flashcards.process(correction_result, debug_mode)

        if flashcards_result:
            lines = flashcards_result.strip().split('\n')
            st.write(f"Generated {max(0, len(lines) - 1)} cards")
            status.update(label="Generation Complete", state="complete", expanded=False)
        else:
            status.update(label="Generation Failed", state="error")
            return

    # --- Save to Database ---
    if db.is_connected():
        try:
            transcription_data = json.loads(transcription_result)
            correction_data = json.loads(correction_result)
            db.save_correction(correction_data, flashcards_result, transcription_data)
        except Exception:
            pass  # Silent fail for elegance

    # --- Display Results ---
    render_correction_results(transcription_result, correction_result)
    render_flashcards_section(flashcards_result)


if __name__ == "__main__":
    main()
