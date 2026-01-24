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
    
    # --- Sidebar: User Preferences (Epic 5) ---
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Story 5.1: Savings Goal Input
        st.subheader("💰 Savings Goal")
        savings_goal = st.number_input(
            "Monthly Savings Target (£)",
            min_value=0,
            max_value=10000,
            value=0,
            step=50,
            help="Set your monthly savings target for personalized AI recommendations"
        )
        
        # Store in session state
        st.session_state['savings_goal'] = savings_goal if savings_goal > 0 else None
        
        # Story 5.2: Tone Mode Selection
        st.subheader("🎭 AI Coach Tone")
        tone_mode = st.selectbox(
            "Tone Mode",
            options=["Supportive", "Playful", "Serious"],
            index=0,
            help="Choose how the AI coach communicates with you"
        )
        
        # Store in session state
        st.session_state['tone_mode'] = tone_mode.lower()
        
        st.markdown("---")
        st.caption("FinanceApp v1.0")
    
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
            
            # --- Data Export (Story 4.1) ---
            st.markdown("---")
            st.subheader("💾 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export as CSV
                csv_data = categorized_data.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name="financeapp_processed_data.csv",
                    mime="text/csv",
                    help="Download processed transaction data as CSV"
                )
            
            with col2:
                # Export as JSON
                json_data = categorized_data.to_json(orient='records', indent=2)
                st.download_button(
                    label="📋 Download JSON",
                    data=json_data,
                    file_name="financeapp_processed_data.json",
                    mime="application/json",
                    help="Download processed transaction data as JSON"
                )
            
            # --- AI Cashflow Coach (Story 3.3) ---
            st.markdown("---")
            st.header("🤖 AI Cashflow Coach")
            
            # Initialize AI client
            client = GeminiClient()
            
            # Store AI advice in session state for export
            ai_advice_text = None
            
            if client.is_configured():
                # Generate AI advice button
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    generate_button = st.button(
                        "🎯 Generate AI Recommendations",
                        help="Click to get personalized AI coaching based on your current settings",
                        type="primary"
                    )
                
                # Only generate when button is clicked
                if generate_button:
                    # Show loading spinner while generating advice
                    with st.spinner("💭 Analyzing your finances and preparing personalized recommendations..."):
                        # Build prompt with financial data and user preferences (Epic 5)
                        prompt = build_coaching_prompt(
                            financial_summary,
                            category_summary,
                            savings_goal=st.session_state.get('savings_goal'),  # Story 5.1
                            tone=st.session_state.get('tone_mode', 'supportive')  # Story 5.2
                        )
                        
                        # Get AI advice
                        result = client.generate_financial_advice(prompt)
                        
                        # Cache the result
                        st.session_state['ai_result'] = result
                
                # Display cached result if available
                if 'ai_result' in st.session_state:
                    result = st.session_state['ai_result']
                    
                    if result['success']:
                        ai_advice_text = result['advice']
                        st.markdown("---")
                        # Display advice
                        st.markdown(ai_advice_text)
                        
                        # --- Export AI Plan (Story 4.2) ---
                        st.markdown("")  # Spacing
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Export as TXT
                            st.download_button(
                                label="📝 Download as Text",
                                data=ai_advice_text,
                                file_name="financeapp_monthly_plan.txt",
                                mime="text/plain",
                                help="Download AI coaching advice as plain text"
                            )
                        
                        with col2:
                            # Export as Markdown
                            st.download_button(
                                label="📄 Download as Markdown",
                                data=ai_advice_text,
                                file_name="financeapp_monthly_plan.md",
                                mime="text/markdown",
                                help="Download AI coaching advice as Markdown"
                            )
                    else:
                        # Show error message but continue
                        st.warning(result['error'])
                else:
                    st.info("👆 Click the button above to generate personalized AI recommendations based on your current settings.")
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
