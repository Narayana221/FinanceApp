"""
Unit tests for CSV controller.

Tests cover the controller layer of MVC architecture.
"""

import pytest
from io import BytesIO
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.csv_model import CSVDataModel
from controllers.csv_controller import CSVController


class TestCSVController:
    """Test suite for CSV controller."""
    
    def test_validate_file_type_csv(self):
        """Test CSV file type validation."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        assert controller.validate_file_type("test.csv") is True
        assert controller.validate_file_type("TEST.CSV") is True
    
    def test_validate_file_type_non_csv(self):
        """Test non-CSV file type rejection."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        assert controller.validate_file_type("test.txt") is False
        assert controller.validate_file_type("test.xlsx") is False
        assert controller.validate_file_type("test") is False
    
    def test_process_upload_success(self):
        """Test successful file upload processing."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        csv_content = """Date,Description,Amount
01/01/2025,Tesco,-45.30
02/01/2025,Salary,2500.00"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        result = controller.process_upload(csv_file, "test.csv")
        
        assert result['success'] is True
        assert result['error'] is None
        assert "uploaded successfully" in result['message']
        assert result['data'] is not None
        assert len(result['data']) == 2
    
    def test_process_upload_invalid_file_type(self):
        """Test upload with invalid file type."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        csv_file = BytesIO(b"some content")
        result = controller.process_upload(csv_file, "test.txt")
        
        assert result['success'] is False
        assert "File format not recognized" in result['error']
    
    def test_process_upload_empty_file(self):
        """Test upload with empty file."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        csv_file = BytesIO(b"")
        result = controller.process_upload(csv_file, "empty.csv")
        
        assert result['success'] is False
        assert "File is empty" in result['error']
    
    def test_process_upload_invalid_format(self):
        """Test upload with undetectable format."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        csv_content = """Random,Columns
Value1,Value2"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        result = controller.process_upload(csv_file, "invalid.csv")
        
        assert result['success'] is False
        assert "Unable to detect required columns" in result['error']
    
    def test_get_data(self):
        """Test getting data from controller."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        csv_content = """Date,Description,Amount
01/01/2025,Tesco,-45.30"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        controller.process_upload(csv_file, "test.csv")
        
        data = controller.get_data()
        
        assert data is not None
        assert 'data' in data
        assert 'format_info' in data
        assert 'file_info' in data
    
    def test_get_data_no_upload(self):
        """Test getting data when nothing uploaded."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        data = controller.get_data()
        assert data is None
    
    def test_clear_data(self):
        """Test clearing data."""
        model = CSVDataModel()
        controller = CSVController(model)
        
        csv_content = """Date,Description,Amount
01/01/2025,Tesco,-45.30"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        controller.process_upload(csv_file, "test.csv")
        
        controller.clear_data()
        
        data = controller.get_data()
        assert data is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
