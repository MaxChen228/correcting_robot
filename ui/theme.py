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

        /* Extended color variables */
        --border-light: #444444;
        --border-lighter: #555555;
        --border-dark: #222222;
        --glow-subtle: rgba(255, 255, 255, 0.02);
        --glow-medium: rgba(255, 255, 255, 0.05);
        --glow-strong: rgba(255, 255, 255, 0.1);
        --shadow-light: rgba(0, 0, 0, 0.2);
        --shadow-medium: rgba(0, 0, 0, 0.3);
        --shadow-strong: rgba(0, 0, 0, 0.5);

        /* Easing functions */
        --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
        --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
        --ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55);
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

    /* Restore button special styling */
    .restore-button-wrapper .stButton > button {
        background: linear-gradient(135deg, rgba(35,35,35,0.9) 0%, rgba(25,25,25,0.8) 100%);
        border: 1px solid #3a3a3a;
        position: relative;
        overflow: hidden;
    }

    /* Ripple effect */
    .restore-button-wrapper .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        transform: translate(-50%, -50%);
        transition: width 0.5s ease, height 0.5s ease;
    }

    .restore-button-wrapper .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }

    .restore-button-wrapper .stButton > button:hover {
        border-color: #4a4a4a;
        box-shadow:
            0 4px 12px rgba(0,0,0,0.4),
            inset 0 0 0 1px rgba(255,255,255,0.05),
            0 0 15px rgba(255,255,255,0.02);
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

    /* Enhanced correction card */
    .correction-card-enhanced {
        position: relative;
        overflow: hidden;
    }

    /* Shimmer effect */
    .correction-card-enhanced::before {
        content: '';
        position: absolute;
        top: 0;
        left: -150%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.03) 50%, transparent 100%);
        transition: left 0.8s ease;
        pointer-events: none;
        z-index: 1;
    }

    .correction-card-enhanced:hover::before {
        left: 150%;
    }

    /* Scale + Shadow + Border Glow */
    .correction-card-enhanced:hover {
        transform: scale(1.015) translateY(-3px);
        border-color: #444;
        box-shadow:
            0 8px 16px rgba(0, 0, 0, 0.4),
            0 2px 6px rgba(0, 0, 0, 0.3),
            inset 0 0 0 1px rgba(255, 255, 255, 0.05),
            0 0 30px rgba(255, 255, 255, 0.02);
    }

    .correction-card-enhanced:active {
        transform: scale(0.99) translateY(-1px);
        transition: transform 0.1s ease;
    }

    /* Enhanced flashcard item */
    .flashcard-item {
        position: relative;
        overflow: hidden;
    }

    .flashcard-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.02), transparent);
        transition: left 0.6s ease;
        pointer-events: none;
    }

    .flashcard-item:hover::before {
        left: 100%;
    }

    .flashcard-item:hover {
        border-color: #333;
        transform: translateX(4px);
        box-shadow:
            inset 0 0 0 1px rgba(255,255,255,0.03),
            -4px 0 8px rgba(0,0,0,0.3),
            0 2px 6px rgba(0,0,0,0.2),
            0 0 15px rgba(255,255,255,0.01);
    }

    /* Left border accent */
    .flashcard-item::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .flashcard-item:hover::after {
        opacity: 1;
    }

    /* Status Container */
    .stStatus {
        background: rgba(18, 18, 18, 0.5) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        font-family: 'Space Mono', monospace !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* Enhanced Expander Header */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(28,28,28,0.9) 0%, rgba(22,22,22,0.8) 100%);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 12px 16px;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 2px 4px rgba(0,0,0,0.3),
            inset 0 0 0 1px rgba(255,255,255,0.02);
        transition:
            all 0.35s cubic-bezier(0.4, 0, 0.2, 1),
            transform 0.2s ease;
    }

    /* Shimmer effect */
    .streamlit-expanderHeader::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 50%;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%);
        transition: left 0.6s ease;
        pointer-events: none;
    }

    .streamlit-expanderHeader:hover::before {
        left: 200%;
    }

    /* Left border accent */
    .streamlit-expanderHeader::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .streamlit-expanderHeader:hover::after {
        opacity: 1;
    }

    /* Hover state - Scale + Shadow + Border Glow */
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(35,35,35,0.95) 0%, rgba(28,28,28,0.9) 100%);
        border-color: #444;
        box-shadow:
            0 4px 8px rgba(0,0,0,0.4),
            inset 0 0 0 1px rgba(255,255,255,0.04),
            -4px 0 12px rgba(0,0,0,0.2),
            0 0 20px rgba(255,255,255,0.02);
        transform: translateX(2px);
    }

    .streamlit-expanderHeader:active {
        transform: translateX(1px) scale(0.99);
        transition: transform 0.1s ease;
    }

    /* Expander Content Enhanced */
    .streamlit-expanderContent {
        background: linear-gradient(180deg, rgba(15,15,15,0.7) 0%, rgba(12,12,12,0.5) 100%);
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 6px 6px;
        padding: 20px;
        margin-top: -1px;
        box-shadow:
            inset 0 2px 4px rgba(0,0,0,0.3),
            0 2px 4px rgba(0,0,0,0.2);
        position: relative;
    }

    /* Top glow */
    .streamlit-expanderContent::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%);
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
