"""
Data validation module for transaction data.

This module provides functions to clean, validate, and report on transaction data quality.
It handles data type validation, missing value handling, and error reporting.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re


def detect_date_format(date_string: str) -> str:
    """
    Detect date format from string pattern.
    
    Args:
        date_string: Date string to analyze
        
    Returns:
        str: Format code - 'ISO', 'DMY', 'MDY', or 'AMBIGUOUS'
    """
    # Check ISO format (YYYY-MM-DD or YYYY/MM/DD)
    if re.match(r'^\d{4}[-/]\d{2}[-/]\d{2}', date_string):
        return 'ISO'
    
    # Extract numeric parts from common separators (/, -, .)
    parts = re.findall(r'\d+', date_string)
    
    if len(parts) >= 3:
        try:
            first, second = int(parts[0]), int(parts[1])
            
            # If first > 12, must be day (DD/MM/YYYY)
            if first > 12:
                return 'DMY'
            
            # If second > 12, first must be month (MM/DD/YYYY)
            if second > 12:
                return 'MDY'
            
            # Both values <= 12: ambiguous
            return 'AMBIGUOUS'
        except (ValueError, IndexError):
            pass
    
    return 'UNKNOWN'


def clean_amount(value) -> float:
    """
    Clean and convert amount value to float.
    
    Args:
        value: Amount value (str, int, or float)
        
    Returns:
        float: Cleaned amount value
        
    Raises:
        ValueError: If value cannot be converted to float
    """
    if pd.isna(value):
        raise ValueError("Amount is missing")
    
    # If already numeric, return as float
    if isinstance(value, (int, float)):
        return float(value)
    
    # Convert to string and clean
    value_str = str(value).strip()
    
    if not value_str:
        raise ValueError("Amount is empty")
    
    # Remove currency symbols and whitespace
    cleaned = re.sub(r'[£$€\s]', '', value_str)
    
    # Remove thousands separators (commas)
    cleaned = cleaned.replace(',', '')
    
    # Handle parentheses notation for negative numbers (accounting format)
    if cleaned.startswith('(') and cleaned.endswith(')'):
        cleaned = '-' + cleaned[1:-1]
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to number")


def parse_date(value, dayfirst: bool = True) -> datetime:
    """
    Parse date value to datetime object with support for multiple formats.
    
    Supports:
    - DD/MM/YYYY (European format, default)
    - MM/DD/YYYY (US format, when dayfirst=False)
    - ISO format (YYYY-MM-DD)
    - Various separators (/, -, .)
    
    Args:
        value: Date value (str or datetime)
        dayfirst: Whether to interpret first value as day (DD/MM/YYYY vs MM/DD/YYYY)
        
    Returns:
        datetime: Parsed date
        
    Raises:
        ValueError: If value cannot be parsed as date, with helpful format hints
    """
    if pd.isna(value):
        raise ValueError("Date is missing")
    
    # If already datetime, return it
    if isinstance(value, (datetime, pd.Timestamp)):
        return pd.Timestamp(value).to_pydatetime()
    
    # Convert to string and clean
    value_str = str(value).strip()
    
    if not value_str:
        raise ValueError("Date is empty")
    
    # Detect format for better error messages
    detected_format = detect_date_format(value_str)
    
    try:
        # Use pandas to_datetime which handles multiple formats
        # It automatically handles ISO, DD/MM/YYYY, MM/DD/YYYY based on dayfirst
        parsed = pd.to_datetime(value_str, dayfirst=dayfirst)
        return parsed.to_pydatetime()
    except Exception as e:
        # Provide helpful error message based on detected format
        error_msg = f"Cannot parse '{value}' as date"
        
        if detected_format == 'UNKNOWN':
            error_msg += ". Expected format: DD/MM/YYYY (e.g., 25/12/2024) or YYYY-MM-DD"
        elif 'day is out of range' in str(e).lower() or 'month must be' in str(e).lower():
            error_msg += f". Invalid day or month value"
            if detected_format == 'DMY':
                error_msg += " (detected DD/MM/YYYY format)"
            elif detected_format == 'MDY':
                error_msg += " (detected MM/DD/YYYY format)"
        elif detected_format == 'AMBIGUOUS':
            format_used = "DD/MM/YYYY" if dayfirst else "MM/DD/YYYY"
            error_msg += f". Ambiguous date - interpreted as {format_used}"
        
        raise ValueError(error_msg)


def validate_row(row: pd.Series, row_number: int) -> Tuple[bool, str]:
    """
    Validate a single transaction row.
    
    Args:
        row: DataFrame row as Series
        row_number: Original row number (1-indexed for user display)
        
    Returns:
        Tuple of (is_valid, error_message)
        error_message is empty string if valid
    """
    # Check for required columns
    if 'Amount' not in row or 'Date' not in row:
        return False, f"Row {row_number}: Missing required columns (Amount or Date)"
    
    # Validate Amount
    try:
        clean_amount(row['Amount'])
    except ValueError as e:
        return False, f"Row {row_number}: Invalid amount - {str(e)}"
    
    # Validate Date
    try:
        parse_date(row['Date'])
    except ValueError as e:
        return False, f"Row {row_number}: Invalid date - {str(e)}"
    
    # Valid row
    return True, ""


def validate_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Validate entire DataFrame and return cleaned data with validation report.
    
    Args:
        df: DataFrame with normalized transaction data
        
    Returns:
        Tuple of (cleaned_df, validation_report)
        
    validation_report structure:
        {
            'total_rows': int,
            'valid_rows': int,
            'skipped_rows': int,
            'errors': [{'row': int, 'reason': str}, ...],
            'warnings': [str, ...]
        }
    """
    if df is None or df.empty:
        return pd.DataFrame(), {
            'total_rows': 0,
            'valid_rows': 0,
            'skipped_rows': 0,
            'errors': [],
            'warnings': ['No data to validate']
        }
    
    total_rows = len(df)
    valid_rows = []
    errors = []
    
    # Validate each row
    for idx, row in df.iterrows():
        row_number = idx + 1  # 1-indexed for user display
        is_valid, error_msg = validate_row(row, row_number)
        
        if is_valid:
            # Clean the data for valid rows
            try:
                cleaned_row = row.copy()
                cleaned_row['Amount'] = clean_amount(row['Amount'])
                cleaned_row['Date'] = parse_date(row['Date'])
                valid_rows.append(cleaned_row)
            except Exception as e:
                # Shouldn't happen since we validated, but handle gracefully
                errors.append({'row': row_number, 'reason': f"Cleaning error: {str(e)}"})
        else:
            errors.append({'row': row_number, 'reason': error_msg.split(': ', 1)[1]})
    
    # Create cleaned DataFrame
    if valid_rows:
        cleaned_df = pd.DataFrame(valid_rows)
        # Ensure proper data types
        cleaned_df['Amount'] = cleaned_df['Amount'].astype(float)
        cleaned_df['Date'] = pd.to_datetime(cleaned_df['Date'])
    else:
        cleaned_df = pd.DataFrame()
    
    # Build validation report
    valid_count = len(valid_rows)
    skipped_count = total_rows - valid_count
    
    warnings = []
    if valid_count < 10:
        warnings.append(
            f"Only {valid_count} valid transaction{'s' if valid_count != 1 else ''} found. "
            f"Analysis works best with at least 10 transactions."
        )
    
    if skipped_count > 0 and skipped_count == total_rows:
        warnings.append("All rows were skipped due to validation errors. Please check your CSV file.")
    elif skipped_count > total_rows * 0.5:  # More than 50% skipped
        warnings.append(
            f"More than half of the rows ({skipped_count}/{total_rows}) were skipped. "
            f"Please review your data quality."
        )
    
    validation_report = {
        'total_rows': total_rows,
        'valid_rows': valid_count,
        'skipped_rows': skipped_count,
        'errors': errors,
        'warnings': warnings
    }
    
    return cleaned_df, validation_report
