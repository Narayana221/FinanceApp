"""
FinanceApp - Personal Cashflow Coach

A Streamlit application for analyzing bank transaction data and receiving
AI-powered financial coaching.

This application follows MVC architecture:
- Models: Data handling and business logic (models/)
- Views: UI components (views/)
- Controllers: Request handling and flow control (controllers/)
"""

import streamlit as st
from models import CSVDataModel
from controllers import CSVController
from views import (
    render_header,
    render_upload_form,
    render_success,
    render_error,
    render_data_preview,
    render_placeholder,
    render_validation_summary
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'csv_model' not in st.session_state:
        st.session_state['csv_model'] = CSVDataModel()
    if 'csv_controller' not in st.session_state:
        st.session_state['csv_controller'] = CSVController(st.session_state['csv_model'])


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title="FinanceApp - Personal Cashflow Coach",
        page_icon="💰",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Get controller from session
    controller = st.session_state['csv_controller']
    
    # Render header
    render_header()
    
    # Render file upload form
    uploaded_file = render_upload_form()
    
    # Handle file upload
    if uploaded_file is not None:
        # Process upload through controller
        result = controller.process_upload(uploaded_file, uploaded_file.name)
        
        if result['success']:
            # Render success message and file info
            render_success(result)
            
            # Render validation summary
            render_validation_summary(result['validation_report'])
            
            # Render data preview
            render_data_preview(result['data'])
        else:
            # Render error message
            render_error(result['error'])
    else:
        # Show placeholder when no file uploaded
        render_placeholder()


if __name__ == "__main__":
    main()
