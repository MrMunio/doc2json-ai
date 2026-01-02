import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Doc2JSON AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main header
st.title("🤖 Doc2JSON AI")
st.subheader("AI-Powered Structured Data Extraction")

st.divider()

# Welcome content
st.markdown("""
### Welcome to Doc2JSON AI

Transform your documents into structured JSON data using advanced AI technology.

#### Features:
- **Extract** - Upload documents and extract structured data
- **History** - View all your previous extraction requests

Use the sidebar to navigate between pages.
""")

st.divider()

# Footer
st.caption("Powered by OpenAI GPT Model | Built with Streamlit")
