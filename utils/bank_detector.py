"""
Bank format detection and column mapping utilities.

This module handles:
- Detection of known bank CSV formats (Monzo, Revolut, Barclays)
- Column normalization to standard format
- Fallback detection for unknown formats
"""

import pandas as pd
import re
from typing import Dict, Tuple, Optional
from datetime import datetime


# Known bank format definitions
BANK_FORMATS = {
    'monzo': {
        'date': 'Date',
        'name': 'Name',
        'amount': 'Amount',
        'category': 'Category'
    },
    'revolut': {
        'started date': 'Date',
        'description': 'Description',
        'amount': 'Amount',
        'category': 'Category'
    },
    'barclays': {
        'date': 'Date',
        'memo': 'Description',
        'amount': 'Amount'
    }
}

# Standard output schema
STANDARD_COLUMNS = ['Date', 'Description', 'Amount', 'Category']


def detect_bank_format(df: pd.DataFrame) -> Optional[str]:
    """
    Detect bank format from DataFrame column headers.
    
    Args:
        df: DataFrame with CSV data
        
    Returns:
        Bank name if detected ('monzo', 'revolut', 'barclays'), None otherwise
    """
    # Normalize column names to lowercase for matching
    df_columns_lower = [col.lower().strip() for col in df.columns]
    
    # Try to match against each known bank format
    for bank_name, column_mapping in BANK_FORMATS.items():
        bank_columns_lower = [col.lower() for col in column_mapping.keys()]
        
        # Check if all required columns for this bank exist
        if all(col in df_columns_lower for col in bank_columns_lower):
            return bank_name
    
    return None


def _calculate_amount_from_money_in_out(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a single 'Amount' column from 'Money In' and 'Money Out'.
    
    Args:
        df: DataFrame containing 'Money In' and 'Money Out' columns
        
    Returns:
        DataFrame with a unified 'Amount' column
    """
    # Convert to numeric, coercing errors to NaN
    money_in = pd.to_numeric(df['Money In'], errors='coerce').fillna(0)
    money_out = pd.to_numeric(df['Money Out'], errors='coerce').fillna(0)
    
    # Money In is positive, Money Out is negative
    # Since Money Out is already negative in the file, we just sum them up
    # If Money Out were positive, we would use `money_in - money_out`
    df['Amount'] = money_in + money_out
    
    return df


def normalize_columns(df: pd.DataFrame, format_name: str) -> pd.DataFrame:
    """
    Normalize DataFrame columns to standard format using known bank mapping.
    
    Args:
        df: DataFrame with bank-specific column names
        format_name: Name of detected bank format
        
    Returns:
        DataFrame with standardized column names
    """
    if format_name not in BANK_FORMATS:
        raise ValueError(f"Unknown format: {format_name}")
    
    # Get column mapping for this bank
    column_mapping = BANK_FORMATS[format_name]
    
    # Create reverse mapping (case-insensitive)
    rename_map = {}
    df_columns_lower = {col.lower(): col for col in df.columns}
    
    for source_col_lower, target_col in column_mapping.items():
        if source_col_lower in df_columns_lower:
            original_col = df_columns_lower[source_col_lower]
            rename_map[original_col] = target_col
    
    # Rename columns
    normalized_df = df.rename(columns=rename_map)
    
    # For Monzo: if we have both Name and Description columns, use Description (more detailed)
    if format_name == 'monzo' and 'Name' in df.columns and 'Description' in df.columns:
        # Rename Name to Description, but keep the original Description if it exists
        normalized_df['Description'] = df['Description']
    elif 'Name' in normalized_df.columns and 'Description' not in normalized_df.columns:
        # If we only have Name, rename it to Description
        normalized_df['Description'] = normalized_df['Name']

    # Keep only standard columns that exist
    existing_standard_cols = [col for col in STANDARD_COLUMNS if col in normalized_df.columns]
    normalized_df = normalized_df[existing_standard_cols]
    
    return normalized_df


def is_date_column(series: pd.Series) -> bool:
    """
    Check if a pandas Series contains date-like values.
    
    Args:
        series: Pandas Series to check
        
    Returns:
        True if column appears to contain dates
    """
    if series.dtype == 'object':
        # Sample first few non-null values
        sample = series.dropna().head(10)
        
        if len(sample) == 0:
            return False
        
        # Common date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # dd/mm/yyyy or mm/dd/yyyy
            r'\d{4}-\d{2}-\d{2}',       # yyyy-mm-dd
            r'\d{1,2}-\d{1,2}-\d{4}',  # dd-mm-yyyy or mm-dd-yyyy
        ]
        
        matches = 0
        for value in sample:
            value_str = str(value)
            if any(re.search(pattern, value_str) for pattern in date_patterns):
                matches += 1
        
        # If majority of samples look like dates
        return matches / len(sample) >= 0.7
    
    return False


def is_amount_column(series: pd.Series) -> bool:
    """
    Check if a pandas Series contains numeric amount values.
    
    Args:
        series: Pandas Series to check
        
    Returns:
        True if column appears to contain amounts
    """
    # Check if already numeric
    if pd.api.types.is_numeric_dtype(series):
        return True
    
    if series.dtype == 'object':
        # Try to convert to numeric
        sample = series.dropna().head(10)
        
        if len(sample) == 0:
            return False
        
        numeric_count = 0
        for value in sample:
            value_str = str(value).strip().replace(',', '').replace('£', '').replace('$', '')
            try:
                float(value_str)
                numeric_count += 1
            except ValueError:
                pass
        
        # If majority can be converted to numeric
        return numeric_count / len(sample) >= 0.7
    
    return False


def fallback_detect(df: pd.DataFrame) -> Dict[str, str]:
    """
    Fallback detection by analyzing column content when format is unknown.
    
    Args:
        df: DataFrame with unknown format
        
    Returns:
        Dictionary mapping standard column names to detected column names
    """
    detected_mapping = {}
    
    # Try to detect Date column
    for col in df.columns:
        if is_date_column(df[col]):
            detected_mapping['Date'] = col
            break
    
    # Try to detect Amount column
    for col in df.columns:
        if col not in detected_mapping.values() and is_amount_column(df[col]):
            detected_mapping['Amount'] = col
            break
    
    # Try to detect Description column (text, not date, not amount)
    for col in df.columns:
        if col not in detected_mapping.values():
            if df[col].dtype == 'object' and not is_date_column(df[col]):
                detected_mapping['Description'] = col
                break
    
    # Check for Category column (optional)
    remaining_text_cols = [
        col for col in df.columns 
        if col not in detected_mapping.values() and df[col].dtype == 'object'
    ]
    if remaining_text_cols and 'category' in remaining_text_cols[0].lower():
        detected_mapping['Category'] = remaining_text_cols[0]
    
    return detected_mapping


def apply_fallback_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Apply fallback mapping to normalize columns.
    
    Args:
        df: DataFrame with original columns
        mapping: Dictionary mapping standard names to original column names
        
    Returns:
        DataFrame with normalized column names
    """
    # Create reverse mapping
    rename_map = {original: standard for standard, original in mapping.items()}
    
    # Rename columns
    normalized_df = df.rename(columns=rename_map)
    
    # Keep only standard columns that exist
    existing_standard_cols = [col for col in STANDARD_COLUMNS if col in normalized_df.columns]
    normalized_df = normalized_df[existing_standard_cols]
    
    return normalized_df


def detect_and_normalize(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Detect bank format and normalize columns in one operation.
    
    Args:
        df: DataFrame with CSV data
        
    Returns:
        Tuple of (normalized_df, format_name)
        format_name will be bank name or 'auto-detected' or 'unknown'
        
    Raises:
        ValueError: If critical columns (Date, Amount) cannot be detected
    """
    # Try known bank format detection first
    bank_format = detect_bank_format(df)
    
    if bank_format:
        normalized_df = normalize_columns(df, bank_format)
        return normalized_df, bank_format
    
    # Try fallback detection
    mapping = fallback_detect(df)
    
    # Validate critical columns were detected
    if 'Date' not in mapping or 'Amount' not in mapping:
        raise ValueError("Unable to detect required columns (Date, Amount). Please check file format.")
    
    # Apply fallback mapping
    normalized_df = apply_fallback_mapping(df, mapping)
    
    return normalized_df, 'auto-detected'
