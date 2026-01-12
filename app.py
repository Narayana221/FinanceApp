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
    render_validation_summary,
    render_financial_summary_metrics,
    render_spending_by_category_chart,
    render_income_vs_expenses_chart,
    render_extreme_values_table,
    render_monthly_trends_chart,
    render_ai_coach_summary,
    render_ai_coach_unavailable
)
from utils.categorizer import categorize_transactions, get_category_summary
from utils.analytics import get_financial_summary, flag_extreme_values, get_monthly_trends
from utils.gemini_client import GeminiClient
from utils.prompt_builder import build_coaching_prompt


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
            
            # Get validated data
            data = result['data']
            
            # --- Financial Analytics & Insights ---
            st.markdown("---")
            st.header("📊 Financial Insights")
            
            # Categorize transactions (Story 2.1)
            categorized_data = categorize_transactions(data)
            
            # Calculate analytics (Story 2.2)
            financial_summary = get_financial_summary(categorized_data)
            category_summary = get_category_summary(categorized_data)
            extreme_values = flag_extreme_values(categorized_data)
            
            # Display summary metrics (Story 2.3)
            render_financial_summary_metrics(financial_summary)
            
            st.markdown("")  # Spacing
            
            # Display charts side by side
            col1, col2 = st.columns(2)
            
            with col1:
                render_spending_by_category_chart(category_summary)
            
            with col2:
                render_income_vs_expenses_chart(financial_summary)
            
            # Display extreme value warnings
            if extreme_values:
                st.markdown("---")
                render_extreme_values_table(extreme_values)
            
            # --- AI Cashflow Coach (Story 3.3) ---
            st.markdown("---")
            st.header("🤖 AI Cashflow Coach")
            
            # Initialize AI client
            client = GeminiClient()
            
            if client.is_configured():
                # Show loading spinner while generating advice
                with st.spinner("💭 Analyzing your finances and preparing personalized recommendations..."):
                    # Build prompt with financial data
                    prompt = build_coaching_prompt(
                        financial_summary,
                        category_summary,
                        savings_goal=None  # Future enhancement
                    )
                    
                    # Get AI advice
                    result = client.generate_financial_advice(prompt)
                
                if result['success']:
                    # Display advice without header (already shown above)
                    st.markdown(result['advice'])
                else:
                    # Show error message but continue
                    st.warning(result['error'])
            else:
                # API key not configured
                st.warning(
                    "AI Coach currently unavailable. Configure GEMINI_API_KEY in .env file to enable personalized coaching."
                )
            
            # --- Monthly Trends ---
            # Display only if data spans multiple months
            monthly_trends = get_monthly_trends(categorized_data)
            
            if not monthly_trends.empty and len(monthly_trends) >= 2:
                st.markdown("---")
                st.header("📈 Monthly Trends")
                render_monthly_trends_chart(monthly_trends)
            
            # --- Data Preview ---
            st.markdown("---")
            st.header("📋 Transaction Data")
            
            # Render data preview with categories
            render_data_preview(categorized_data)
        else:
            # Render error message
            render_error(result['error'])
    else:
        # Show placeholder when no file uploaded
        render_placeholder()


if __name__ == "__main__":
    main()
