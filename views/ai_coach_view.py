"""
AI Coach View Components

This module contains view functions for displaying AI-generated financial coaching
advice and handling unavailability scenarios.
"""

import streamlit as st


def render_ai_coach_summary(advice_text: str) -> None:
    """
    Render AI-generated financial coaching advice.
    
    Displays the AI coach section with personalized recommendations,
    money habits, and spending leak analysis in a user-friendly format.
    
    Args:
        advice_text: The AI-generated advice string containing
                    recommendations, habits, and spending insights
                    
    Example:
        >>> render_ai_coach_summary("RECOMMENDATIONS:\\n1. Save £50 on groceries...")
        # Displays formatted AI advice in Streamlit UI
    """
    st.header("🤖 AI Cashflow Coach")
    st.info(advice_text)


def render_ai_coach_unavailable(message: str) -> None:
    """
    Render message when AI coach is unavailable.
    
    Displays a warning message explaining why the AI coach cannot
    provide advice, while allowing users to continue using analytics.
    
    Args:
        message: The error or unavailability message to display
        
    Example:
        >>> render_ai_coach_unavailable("API key not configured")
        # Displays warning message in Streamlit UI
    """
    st.header("🤖 AI Cashflow Coach")
    st.warning(message)
