import streamlit as st
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://app:8021")

st.set_page_config(page_title="Request History", page_icon="📜", layout="wide")

# Header
st.title("📜 Request History")
st.markdown("View all your previous extraction requests")

st.divider()

# Initialize session state
if 'selected_request' not in st.session_state:
    st.session_state.selected_request = None

def fetch_history(limit=50, offset=0):
    """Fetch historical requests from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/historical-requests",
            params={"limit": limit, "offset": offset},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch history: {response.status_code}")
            return {"items": [], "total": 0}
    except Exception as e:
        st.error(f"Error fetching history: {str(e)}")
        return {"items": [], "total": 0}

def fetch_request_details(request_id):
    """Fetch detailed information for a specific request"""
    try:
        response = requests.get(f"{API_BASE_URL}/status/{request_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching details: {str(e)}")
        return None

def format_datetime(iso_string):
    """Format ISO datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string

# Main layout with two columns
col1, col2 = st.columns([1, 2])

# Left column - Request list
with col1:
    st.subheader("All Requests")
    
    # Fetch history
    history_data = fetch_history(limit=100)
    items = history_data.get('items', [])
    total = history_data.get('total', 0)
    
    if total > 0:
        st.metric("Total Requests", total)
        
        st.divider()
        
        # Display each request as a clickable item
        for item in items:
            request_id = item['request_id']
            status = item['status']
            metadata = item.get('metadata', {})
            filename = metadata.get('original_filename', 'Unknown')
            created_at = format_datetime(item['created_at'])
            
            # Create container for each request
            with st.container():
                # Button to select request
                button_label = f"{filename[:30]}..." if len(filename) > 30 else filename
                
                if st.button(
                    button_label,
                    key=f"req_{request_id}",
                    use_container_width=True,
                    type="secondary" if st.session_state.selected_request != request_id else "primary"
                ):
                    st.session_state.selected_request = request_id
                    st.rerun()
                
                # Display status badge
                if status == 'success':
                    st.success(f"Status: {status.upper()}", icon="✅")
                elif status == 'failed':
                    st.error(f"Status: {status.upper()}", icon="❌")
                elif status == 'inprogress':
                    st.warning(f"Status: {status.upper()}", icon="⏳")
                else:
                    st.info(f"Status: {status.upper()}", icon="🔵")
                
                st.caption(f"Created: {created_at}")
                st.caption(f"ID: {request_id[:16]}...")
                
                st.divider()
    else:
        st.info("No requests found. Start by extracting some documents!")

# Right column - Request details
with col2:
    st.subheader("Request Details")
    
    if st.session_state.selected_request:
        # Fetch detailed information
        details = fetch_request_details(st.session_state.selected_request)
        
        if details:
            # Display request ID
            st.code(details['request_id'], language=None)
            
            # Status
            status = details['status']
            if status == 'success':
                st.success(f"Status: {status.upper()}")
            elif status == 'failed':
                st.error(f"Status: {status.upper()}")
            elif status in ['initiated', 'inprogress']:
                st.warning(f"Status: {status.upper()}")
            else:
                st.info(f"Status: {status.upper()}")
            
            st.divider()
            
            # Metadata
            metadata = details.get('metadata', {})
            if metadata:
                st.subheader("Metadata")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("Filename", metadata.get('original_filename', 'N/A'))
                    st.metric("Checksum", metadata.get('checksum', 'N/A')[:16] + "...")
                
                with col_b:
                    st.metric("File Size", f"{metadata.get('file_size', 0) / 1024:.2f} KB")
                    st.metric("Created At", format_datetime(details['created_at']))
            
            st.divider()
            
            # Extracted data or error
            if details['status'] == 'success' and details.get('extracted_data'):
                st.subheader("Extracted Data")
                st.json(details['extracted_data'])
                
                # Download button
                json_str = json.dumps(details['extracted_data'], indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"extracted_data_{details['request_id']}.json",
                    mime="application/json",
                    type="primary"
                )
                
            elif details['status'] == 'failed':
                st.subheader("Error Information")
                error_msg = details.get('message') or details.get('errors', {})
                st.error(f"Error: {error_msg}")
                
            elif details['status'] in ['initiated', 'inprogress']:
                st.info("This request is still being processed.")
                
                if st.button("Refresh Status", type="secondary"):
                    st.rerun()
        else:
            st.error("Failed to load request details.")
    else:
        st.info("Select a request from the list to view its details")
