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

    /* Custom Button Styling - Enhanced */
    .stButton > button {
        background: rgba(30, 30, 30, 0.8);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 0.7rem 1.8rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover {
        background: rgba(50, 50, 50, 0.9);
        border-color: #555;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
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
        background: rgba(18, 18, 18, 0.6);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 32px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3),
                    0 1px 3px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }

    .correction-card:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4),
                    0 2px 4px rgba(0, 0, 0, 0.3);
        border-color: #444;
    }

    /* Status Container */
    .stStatus {
        background: rgba(18, 18, 18, 0.5) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        font-family: 'Space Mono', monospace !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(25, 25, 25, 0.8);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(35, 35, 35, 0.9);
        border-color: #444;
    }

    .streamlit-expanderContent {
        background: rgba(15, 15, 15, 0.6);
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 6px 6px;
        padding: 20px;
        margin-top: -1px;
    }

    /* Container Borders */
    .stContainer {
        border-radius: 6px;
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
