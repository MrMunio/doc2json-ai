import streamlit as st
import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://app:8021")
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL_SECONDS", "10"))

st.set_page_config(page_title="Extract Data", page_icon="📤", layout="wide")

# Header
st.title("📤 Extract Structured Data")
st.markdown("Upload your document and let AI extract structured information")

st.divider()

# Initialize session state
if 'request_id' not in st.session_state:
    st.session_state.request_id = None
if 'polling_active' not in st.session_state:
    st.session_state.polling_active = False
if 'last_status' not in st.session_state:
    st.session_state.last_status = None

def upload_file(file):
    """Upload file to the extraction API"""
    try:
        files = {'file': (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/extract", files=files, timeout=30)
        
        if response.status_code in [200, 202]:
            return response.json()
        else:
            st.error(f"Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return None

def check_status(request_id):
    """Check the status of an extraction request"""
    try:
        response = requests.get(f"{API_BASE_URL}/status/{request_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error checking status: {str(e)}")
        return None

# File upload section
uploaded_file = st.file_uploader(
    "Choose a document to extract data from",
    type=['pdf', 'docx', 'doc', 'txt'],
    help="Supported formats: PDF, DOCX, DOC, TXT"
)

if uploaded_file is not None:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Extract Data", type="primary", use_container_width=True):
            with st.spinner("Uploading file..."):
                result = upload_file(uploaded_file)
                
                if result:
                    st.session_state.request_id = result.get('request_id')
                    st.session_state.polling_active = True
                    st.session_state.last_status = result.get('status')
                    st.success("File uploaded successfully!")
                    st.info(f"Request ID: `{st.session_state.request_id}`")
                    st.rerun()

st.divider()

# Status monitoring section
if st.session_state.request_id and st.session_state.polling_active:
    st.subheader("Extraction Status")
    
    # Poll for status
    status_data = check_status(st.session_state.request_id)
    
    if status_data:
        current_status = status_data.get('status')
        st.session_state.last_status = current_status
        
        # Display status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if current_status == 'success':
                st.success(f"Status: {current_status.upper()}")
            elif current_status == 'failed':
                st.error(f"Status: {current_status.upper()}")
            elif current_status in ['initiated', 'inprogress']:
                st.warning(f"Status: {current_status.upper()}")
            else:
                st.info(f"Status: {current_status.upper()}")
        
        # Display metadata
        metadata = status_data.get('metadata', {})
        if metadata:
            with col2:
                st.metric("Filename", metadata.get('original_filename', 'N/A'))
            with col3:
                st.metric("File Size", f"{metadata.get('file_size', 0) / 1024:.2f} KB")
        
        st.divider()
        
        # Handle different statuses
        if current_status in ['initiated', 'inprogress']:
            # Show processing message
            with st.spinner(f"Processing your document... Checking again in {POLLING_INTERVAL} seconds"):
                time.sleep(POLLING_INTERVAL)
                st.rerun()
            
        elif current_status == 'success':
            st.session_state.polling_active = False
            st.success("Extraction completed successfully!")
            
            # Display extracted data
            extracted_data = status_data.get('extracted_data')
            if extracted_data:
                st.subheader("Extracted JSON Data")
                st.json(extracted_data)
                
                # Download button
                json_str = json.dumps(extracted_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"extracted_data_{st.session_state.request_id}.json",
                    mime="application/json",
                    type="primary"
                )
            
        elif current_status == 'failed':
            st.session_state.polling_active = False
            st.error("Extraction failed")
            
            # Display error message
            error_msg = status_data.get('message') or status_data.get('errors', {})
            st.error(f"Error: {error_msg}")
    
    st.divider()
    
    # Reset button
    if st.button("Start New Extraction", type="secondary"):
        st.session_state.request_id = None
        st.session_state.polling_active = False
        st.session_state.last_status = None
        st.rerun()

# Info section
with st.expander("How it works", expanded=False):
    st.markdown(f"""
    1. Upload your document using the file uploader above
    2. Click "Extract Data" to start the extraction process
    3. The system will automatically poll for status every {POLLING_INTERVAL} seconds
    4. Once complete, view or download the extracted JSON data
    """)
