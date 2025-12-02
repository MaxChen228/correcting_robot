"""
Database Service
Supabase 雲端儲存管理
"""
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from typing import Optional
import json

from config.settings import Config


class DatabaseService:
    """Supabase database connection and operations"""

    def __init__(self):
        """Initialize Supabase client"""
        self.client: Optional[Client] = None
        self._connect()

    def _connect(self):
        """Establish connection to Supabase"""
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            try:
                self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            except Exception as e:
                st.error(f"Supabase Connection Error: {e}")
                self.client = None

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None

    def save_correction(
        self,
        correction_data: list,
        flashcards_csv: str,
        transcription_data: Optional[list] = None
    ) -> bool:
        """
        Save correction result to history

        Args:
            correction_data: Agent 2 output (Correction JSON data as list)
            flashcards_csv: Agent 3 output (Flashcards CSV string)
            transcription_data: Agent 1 output (Transcription JSON data as list, optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "corrections": correction_data,
                "flashcards": flashcards_csv,
                "transcriptions": transcription_data
            }
            self.client.table("correction_history").insert(history_entry).execute()
            return True

        except Exception:
            # Silent fail for elegance
            return False

    def get_history_count(self) -> int:
        """
        Get total number of corrections in history

        Returns:
            Number of records, 0 if error
        """
        if not self.is_connected():
            return 0

        try:
            response = self.client.table("correction_history").select("id", count="exact").execute()
            return response.count if hasattr(response, 'count') else 0

        except Exception:
            return 0

    def get_all_history(self) -> list:
        """
        Get all correction history records

        Returns:
            List of history records, empty list if error
        """
        if not self.is_connected():
            return []

        try:
            response = self.client.table("correction_history").select("*").order("created_at", desc=True).execute()
            return response.data if response.data else []

        except Exception as e:
            st.error(f"Failed to load history: {e}")
            return []

    def render_sidebar_info(self):
        """Render database info in sidebar"""
        st.sidebar.markdown("### History")

        if not self.is_connected():
            st.sidebar.info("Supabase not configured.")
            return

        # Display history count
        history_count = self.get_history_count()
        st.sidebar.markdown(
            f"<p style='font-family:Space Mono; font-size:0.8rem'>Total Corrections: {history_count}</p>",
            unsafe_allow_html=True
        )

        # View history button (placeholder)
        if st.sidebar.button("View Archive", use_container_width=True):
            st.session_state.show_history = True
