"""
CSV data model for transaction data.

This module handles the data layer for CSV transactions including
validation, normalization, and storage.
"""

import pandas as pd
from io import BytesIO
from typing import Dict, Optional, Tuple
from utils.bank_detector import detect_and_normalize
from utils.data_validator import validate_dataframe


class CSVDataModel:
    """Model for CSV transaction data."""
    
    def __init__(self):
        """Initialize the CSV data model."""
        self.raw_data: Optional[pd.DataFrame] = None
        self.normalized_data: Optional[pd.DataFrame] = None
        self.validated_data: Optional[pd.DataFrame] = None
        self.validation_report: Optional[Dict] = None
        self.detected_format: Optional[str] = None
        self.filename: Optional[str] = None
        self.file_size: Optional[int] = None
    
    def load_from_file(self, file: BytesIO, filename: str) -> Dict:
        """
        Load and validate CSV data from file.
        
        Args:
            file: BytesIO object containing CSV data
            filename: Original filename
            
        Returns:
            Dictionary with validation result:
            - valid (bool): True if file is valid
            - error (str): Error message if invalid, None otherwise
            - rows (int): Number of rows if valid
        """
        try:
            # Reset file pointer
            file.seek(0)
            
            # Check if file is empty
            content = file.read()
            if not content or len(content) == 0:
                return {
                    'valid': False,
                    'error': 'File is empty. Please upload a valid CSV.',
                    'rows': 0
                }
            
            # Store file size
            self.file_size = len(content)
            
            # Reset for pandas
            file.seek(0)
            
            # Read CSV
            self.raw_data = pd.read_csv(file)
            
            # Detect bank format and normalize
            try:
                self.normalized_data, self.detected_format = detect_and_normalize(self.raw_data)
                self.filename = filename
                
                # Validate and clean the normalized data
                self.validated_data, self.validation_report = validate_dataframe(self.normalized_data)
                
                # Check if we have any valid data
                if self.validation_report['valid_rows'] == 0:
                    return {
                        'valid': False,
                        'error': 'No valid transactions found after validation. Please check your CSV data.',
                        'rows': 0
                    }
                
                return {
                    'valid': True,
                    'error': None,
                    'rows': self.validation_report['valid_rows']
                }
                
            except ValueError as e:
                # Format detection failed
                return {
                    'valid': False,
                    'error': str(e),
                    'rows': 0
                }
                
        except pd.errors.EmptyDataError:
            return {
                'valid': False,
                'error': 'File is empty. Please upload a valid CSV.',
                'rows': 0
            }
        except Exception as e:
            return {
                'valid': False,
                'error': 'File format not recognized. Please upload a CSV file.',
                'rows': 0
            }
    
    def get_normalized_data(self) -> Optional[pd.DataFrame]:
        """Get normalized transaction data."""
        return self.normalized_data
    
    def get_validated_data(self) -> Optional[pd.DataFrame]:
        """Get validated and cleaned transaction data."""
        return self.validated_data
    
    def get_validation_report(self) -> Optional[Dict]:
        """Get validation report with statistics and errors."""
        return self.validation_report
    
    def get_raw_data(self) -> Optional[pd.DataFrame]:
        """Get raw transaction data."""
        return self.raw_data
    
    def get_format_info(self) -> Dict:
        """
        Get information about detected format.
        
        Returns:
            Dictionary with format information
        """
        if not self.detected_format:
            return {'format': None, 'display': 'Unknown'}
        
        if self.detected_format in ['monzo', 'revolut', 'barclays']:
            return {
                'format': self.detected_format,
                'display': f'🏦 **Format detected:** {self.detected_format.title()}'
            }
        elif self.detected_format == 'auto-detected':
            return {
                'format': 'auto-detected',
                'display': '🏦 **Format:** Auto-detected'
            }
        else:
            return {
                'format': 'standard',
                'display': '🏦 **Format:** Standard'
            }
    
    def get_file_info(self) -> Dict:
        """
        Get file information.
        
        Returns:
            Dictionary with file information
        """
        return {
            'filename': self.filename,
            'size': self.file_size,
            'rows': len(self.normalized_data) if self.normalized_data is not None else 0
        }
    
    def clear(self):
        """Clear all stored data."""
        self.raw_data = None
        self.normalized_data = None
        self.validated_data = None
        self.validation_report = None
        self.detected_format = None
        self.filename = None
        self.file_size = None
