"""
Configuration Management
統一管理所有環境變數和 API 配置
"""
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


class Config:
    """Application configuration from environment variables"""

    # Google Gemini API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = "gemini-3-pro-preview"

    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

    # Streamlit Page Config
    PAGE_TITLE = "Handwriting Correction"
    PAGE_ICON = None
    LAYOUT = "wide"


def configure_gemini_api(api_key: str = None):
    """
    Configure Google Gemini API

    Args:
        api_key: Optional API key override
    """
    import google.generativeai as genai

    key = api_key or Config.GOOGLE_API_KEY
    if key:
        genai.configure(api_key=key)
        return True
    return False
