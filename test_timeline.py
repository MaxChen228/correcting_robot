import streamlit as st
from unittest.mock import MagicMock
import sys

# Mock DatabaseService before importing components
sys.modules['services.database'] = MagicMock()
mock_db = MagicMock()
mock_db.update_record_name.return_value = True
sys.modules['services.database'].DatabaseService.return_value = mock_db

from ui.components import render_history_page
from ui.theme import apply_custom_theme

# Mock Data
mock_history = [
    {
        "id": "1",
        "name": "English Homework #1",
        "timestamp": "2025-12-02T11:55:00",
        "transcriptions": [{"id": "01", "standard": "Hello World"}],
        "corrections": [{"id": "01", "user": "Helo World", "correction": "Hello World", "feedback": "Spelling error"}],
    },
    {
        "id": "2",
        "name": "", # Should show default
        "timestamp": "2025-12-01T09:30:00",
        "transcriptions": [],
        "corrections": [{"id": "01", "user": "Test", "correction": "Test", "feedback": "Good"}],
    },
    {
        "id": "3",
        "name": "Late Night Study",
        "timestamp": "2025-11-30T14:20:00",
        "transcriptions": [],
        "corrections": [],
    }
]

st.set_page_config(layout="wide")
apply_custom_theme()

st.title("Timeline Component Test")

# Initialize session state for the back button to work without erroring (though it won't do anything in this test script)
if 'show_history' not in st.session_state:
    st.session_state.show_history = True

render_history_page(mock_history)
