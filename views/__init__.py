"""
Views package for FinanceApp.

This package contains view components following MVC architecture.
"""

from .csv_view import (
    render_header,
    render_upload_form,
    render_success,
    render_error,
    render_data_preview,
    render_placeholder,
    render_validation_summary,
    format_file_size
)

from .charts import (
    render_financial_summary_metrics,
    render_spending_by_category_chart,
    render_income_vs_expenses_chart,
    render_extreme_values_table
)

__all__ = [
    'render_header',
    'render_upload_form',
    'render_success',
    'render_error',
    'render_data_preview',
    'render_placeholder',
    'render_validation_summary',
    'format_file_size',
    'render_financial_summary_metrics',
    'render_spending_by_category_chart',
    'render_income_vs_expenses_chart',
    'render_extreme_values_table'
]
