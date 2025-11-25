"""
UI Theme Management
極簡主義設計系統：Cormorant Garamond + Space Mono + Tangerine
"""
import streamlit as st


def apply_custom_theme():
    """
    Apply custom CSS theme to Streamlit app
    Minimalist design with Google Fonts integration
    """
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


def render_header():
    """Render the app header with custom styling"""
    st.markdown('<div style="text-align: center; padding: 2rem 0 1rem 0;">', unsafe_allow_html=True)
    st.markdown('<span class="accent-text">The Art of Translation</span>', unsafe_allow_html=True)
    st.title("Handwriting Correction")
    st.markdown('</div>', unsafe_allow_html=True)
