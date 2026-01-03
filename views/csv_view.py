"""
CSV upload view components.

This module contains Streamlit UI components for CSV upload
following MVC architecture.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Optional


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def render_upload_form() -> Optional[object]:
    """
    Render the file upload form.
    
    Returns:
        Uploaded file object or None
    """
    st.subheader("📁 Upload Your Transaction Data")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your bank transaction CSV file. Supports Monzo, Revolut, Barclays, and standard formats"
    )
    
    return uploaded_file


def render_success(result: Dict):
    """
    Render success message and file information.
    
    Args:
        result: Processing result dictionary
    """
    st.success(result['message'])
    
    # Prepare info message
    file_info = result['file_info']
    format_info = result['format_info']
    
    info_parts = [
        f"📄 **Filename:** {file_info['filename']}",
        format_info['display'],
        f"📊 **Size:** {format_file_size(file_info['size'])}",
        f"📈 **Rows:** {file_info['rows']}"
    ]
    
    st.info("  \n".join(info_parts))


def render_validation_summary(validation_report: Dict):
    """
    Render validation summary with processing statistics.
    
    Args:
        validation_report: Validation report dictionary with stats and errors
    """
    if not validation_report:
        return
    
    total = validation_report['total_rows']
    valid = validation_report['valid_rows']
    skipped = validation_report['skipped_rows']
    errors = validation_report['errors']
    warnings = validation_report['warnings']
    
    # Show processing summary
    if skipped == 0:
        st.success(f"✅ All {valid} transactions processed successfully!")
    else:
        summary = f"📊 **Processing Summary:** {valid} valid, {skipped} skipped (out of {total} total)"
        st.info(summary)
    
    # Show warnings
    for warning in warnings:
        st.warning(f"⚠️ {warning}")
    
    # Show errors if any
    if errors:
        with st.expander(f"📋 View {len(errors)} Validation Error{'s' if len(errors) != 1 else ''}", expanded=False):
            for error in errors[:10]:  # Limit to first 10 errors
                st.text(f"• Row {error['row']}: {error['reason']}")
            
            if len(errors) > 10:
                st.text(f"... and {len(errors) - 10} more errors")


def render_error(error_message: str):
    """
    Render error message with sample format.
    
    Args:
        error_message: Error message to display
    """
    st.error(error_message)
    st.info("💡 **Expected format:**")
    st.code("""Date,Description,Amount,Category
01/01/2025,Tesco Superstore,-45.30,Groceries
02/01/2025,Salary Payment,2500.00,Income""", language="csv")


def render_data_preview(data: pd.DataFrame):
    """
    Render data preview table.
    
    Args:
        data: DataFrame to display
    """
    st.subheader("📋 Data Preview")
    st.dataframe(data.head(10), use_container_width=True)


def render_placeholder():
    """Render placeholder message when no file is uploaded."""
    st.info("👆 Please upload a CSV file to begin your financial analysis")


def render_header():
    """Render application header."""
    st.title("💰 FinanceApp - Personal Cashflow Coach")
    st.markdown("Upload your bank transaction CSV to get started with your financial analysis")
