"""
CSV upload controller.

This module handles the business logic for CSV file upload,
validation, and processing.
"""

from typing import Dict, Optional
from io import BytesIO
from models.csv_model import CSVDataModel


class CSVController:
    """Controller for CSV upload operations."""
    
    def __init__(self, model: CSVDataModel):
        """
        Initialize controller with data model.
        
        Args:
            model: CSVDataModel instance
        """
        self.model = model
    
    def validate_file_type(self, filename: str) -> bool:
        """
        Check if filename has .csv extension.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if filename ends with .csv, False otherwise
        """
        return filename.lower().endswith('.csv')
    
    def process_upload(self, file: BytesIO, filename: str) -> Dict:
        """
        Process uploaded CSV file.
        
        Args:
            file: BytesIO object containing CSV data
            filename: Original filename
            
        Returns:
            Dictionary with processing result:
            - success (bool): True if processing succeeded
            - error (str): Error message if failed, None otherwise
            - message (str): Success message if succeeded
            - data (DataFrame): Normalized data if succeeded
            - format_info (dict): Format detection information
            - file_info (dict): File information
        """
        # Validate file type
        if not self.validate_file_type(filename):
            return {
                'success': False,
                'error': '❌ File format not recognized. Please upload a CSV file.',
                'message': None,
                'data': None,
                'format_info': None,
                'file_info': None
            }
        
        # Load and validate data
        validation_result = self.model.load_from_file(file, filename)
        
        if not validation_result['valid']:
            return {
                'success': False,
                'error': f"❌ {validation_result['error']}",
                'message': None,
                'data': None,
                'format_info': None,
                'file_info': None
            }
        
        # Success - prepare result
        return {
            'success': True,
            'error': None,
            'message': '✅ File uploaded successfully!',
            'data': self.model.get_validated_data(),
            'format_info': self.model.get_format_info(),
            'file_info': self.model.get_file_info(),
            'validation_report': self.model.get_validation_report()
        }
    
    def get_data(self) -> Optional[Dict]:
        """
        Get current data from model.
        
        Returns:
            Dictionary with data and metadata, or None if no data loaded
        """
        if self.model.validated_data is None:
            return None
        
        return {
            'data': self.model.get_validated_data(),
            'format_info': self.model.get_format_info(),
            'file_info': self.model.get_file_info(),
            'validation_report': self.model.get_validation_report()
        }
    
    def clear_data(self):
        """Clear all data from model."""
        self.model.clear()
