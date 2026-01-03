"""
Unit tests for CSV data model.

Tests cover the data model layer of MVC architecture.
"""

import pytest
import pandas as pd
from io import BytesIO
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.csv_model import CSVDataModel


class TestCSVDataModel:
    """Test suite for CSV data model."""
    
    def test_initialization(self):
        """Test model initialization."""
        model = CSVDataModel()
        
        assert model.raw_data is None
        assert model.normalized_data is None
        assert model.validated_data is None
        assert model.validation_report is None
        assert model.detected_format is None
        assert model.filename is None
        assert model.file_size is None
    
    def test_load_valid_csv(self):
        """Test loading valid CSV file."""
        model = CSVDataModel()
        csv_content = """Date,Description,Amount
01/01/2025,Tesco,-45.30
02/01/2025,Salary,2500.00
03/01/2025,Rent,-800.00
04/01/2025,Coffee,-3.50
05/01/2025,Sainsburys,-65.20
06/01/2025,Bonus,500.00
07/01/2025,Transport,-25.00
08/01/2025,Restaurant,-45.00
09/01/2025,Utilities,-120.00
10/01/2025,Refund,20.00
11/01/2025,Groceries,-85.00"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        result = model.load_from_file(csv_file, "test.csv")
        
        assert result['valid'] is True
        assert result['error'] is None
        assert result['rows'] == 11
        assert model.filename == "test.csv"
        assert model.file_size > 0
        assert model.validated_data is not None
        assert model.validation_report is not None
        assert model.validation_report['valid_rows'] == 11
        assert model.validation_report['skipped_rows'] == 0
    
    def test_load_empty_file(self):
        """Test loading empty file."""
        model = CSVDataModel()
        csv_file = BytesIO(b"")
        result = model.load_from_file(csv_file, "empty.csv")
        
        assert result['valid'] is False
        assert "File is empty" in result['error']
    
    def test_load_invalid_format(self):
        """Test loading file with undetectable format."""
        model = CSVDataModel()
        csv_content = """Random,Columns
Value1,Value2"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        result = model.load_from_file(csv_file, "invalid.csv")
        
        assert result['valid'] is False
        assert "Unable to detect required columns" in result['error']
    
    def test_get_format_info_monzo(self):
        """Test format info for Monzo format."""
        model = CSVDataModel()
        csv_content = """Date,Name,Amount,Category
01/01/2025,Tesco,-45.30,Groceries"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        model.load_from_file(csv_file, "monzo.csv")
        
        format_info = model.get_format_info()
        assert format_info['format'] == 'monzo'
        assert 'Monzo' in format_info['display']
    
    def test_get_format_info_auto_detected(self):
        """Test format info for auto-detected format."""
        model = CSVDataModel()
        csv_content = """Transaction Date,Merchant,Value
01/01/2025,Tesco,-45.30"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        model.load_from_file(csv_file, "custom.csv")
        
        format_info = model.get_format_info()
        assert format_info['format'] == 'auto-detected'
        assert 'Auto-detected' in format_info['display']
    
    def test_get_file_info(self):
        """Test file information retrieval."""
        model = CSVDataModel()
        csv_content = """Date,Description,Amount
01/01/2025,Tesco,-45.30"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        model.load_from_file(csv_file, "test.csv")
        
        file_info = model.get_file_info()
        assert file_info['filename'] == "test.csv"
        assert file_info['size'] > 0
        assert file_info['rows'] == 1
    
    def test_clear(self):
        """Test clearing model data."""
        model = CSVDataModel()
        csv_content = """Date,Description,Amount
01/01/2025,Tesco,-45.30"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        model.load_from_file(csv_file, "test.csv")
        
        model.clear()
        
        assert model.raw_data is None
        assert model.normalized_data is None
        assert model.validated_data is None
        assert model.validation_report is None
        assert model.detected_format is None
        assert model.filename is None
        assert model.file_size is None
    
    def test_load_csv_with_invalid_rows(self):
        """Test loading CSV with some invalid rows."""
        model = CSVDataModel()
        csv_content = """Date,Description,Amount
01/01/2025,Valid Transaction,-45.30
invalid_date,Bad Row,100.00
03/01/2025,Another Valid,-30.00
04/01/2025,Valid Again,abc
05/01/2025,Good Transaction,50.00
06/01/2025,Also Good,-20.00
07/01/2025,Another Good,75.00
08/01/2025,Valid Row,-15.00
09/01/2025,Good Row,90.00
10/01/2025,Last Valid,-25.00
11/01/2025,Final Good,100.00"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        result = model.load_from_file(csv_file, "mixed.csv")
        
        assert result['valid'] is True
        assert result['rows'] == 9  # 11 total - 2 invalid
        assert model.validation_report['total_rows'] == 11
        assert model.validation_report['valid_rows'] == 9
        assert model.validation_report['skipped_rows'] == 2
        assert len(model.validation_report['errors']) == 2
    
    def test_load_csv_all_invalid(self):
        """Test loading CSV where all rows are invalid."""
        model = CSVDataModel()
        csv_content = """Date,Description,Amount
invalid,Bad1,abc
bad_date,Bad2,xyz"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        result = model.load_from_file(csv_file, "all_invalid.csv")
        
        # File will be detected but all rows will fail validation
        assert result['valid'] is False
        # Error could be from bank detection OR from validation
        assert result['error'] is not None
    
    def test_get_validated_data(self):
        """Test retrieving validated data."""
        model = CSVDataModel()
        csv_content = """Date,Description,Amount
01/01/2025,Tesco,-45.30
02/01/2025,Salary,2500.00
03/01/2025,Invalid,abc
04/01/2025,Rent,-800.00
05/01/2025,Coffee,-3.50
06/01/2025,Sainsburys,-65.20
07/01/2025,Bonus,500.00
08/01/2025,Transport,-25.00
09/01/2025,Restaurant,-45.00
10/01/2025,Utilities,-120.00
11/01/2025,Refund,20.00"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        model.load_from_file(csv_file, "test.csv")
        
        validated = model.get_validated_data()
        assert validated is not None
        assert len(validated) == 10  # 11 - 1 invalid
        assert validated['Amount'].dtype == float
    
    def test_get_validation_report(self):
        """Test retrieving validation report."""
        model = CSVDataModel()
        csv_content = """Date,Description,Amount
01/01/2025,Test,-45.30"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        model.load_from_file(csv_file, "test.csv")
        
        report = model.get_validation_report()
        assert report is not None
        assert 'total_rows' in report
        assert 'valid_rows' in report
        assert 'skipped_rows' in report
        assert 'errors' in report
        assert 'warnings' in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
